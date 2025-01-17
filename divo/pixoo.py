"""
This file is part of divo (https://github.com/spezifisch/divo).
Copyright (c) 2021 spezifisch (https://github.com/spezifisch).

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

from datetime import datetime
from typing import Optional, Union, Any

from loguru import logger

import bluetooth_base
import command
import exceptions
from packet import ResponsePacket, Packet, CommandBase


class Pixoo:
    def __init__(self, bt_device: bluetooth_base.BluetoothBase):
        self.comm = bt_device
        self.comm.connect()
        self.comm.flush()

        self.command_parser = command.CommandParser()

    def write(self, data: bytes) -> Union[Optional[bytes], Any]:
        """
        send raw data to Pixoo and receive and parse response packet

        :param data: raw packet to send
        :return: ResponsePacket if this command has a response and we successfully received it
        """

        if not Packet.is_valid(self.command_parser, data):
            raise exceptions.PacketWriteException("tried to send invalid packet")

        self.comm.write(data)
        logger.debug(f"sending {list(data)}")

        cmd = data[3]
        if cmd in command.without_response:
            return None

        # read packet start marker and packet size
        response = self.comm.read(3)
        if len(response) == 3:
            if response[0] == Packet.START_OF_PACKET:
                size_lo = response[1]
                size_hi = response[2]
                size = ((size_hi & 0xff) << 8) | (size_lo & 0xff)
                logger.debug(f"receiving payload with length {size}")

                # read rest of packet
                rest = self.comm.read(size + 1)
                if len(rest):
                    if rest[-1] == Packet.END_OF_PACKET:
                        # we received a complete packet
                        packet = response + rest
                        logger.debug(f"received {list(packet)}")
                        return ResponsePacket.parse(self.command_parser, packet)
                    else:
                        logger.error(f"end marker not present: rest={rest}")
                else:
                    logger.error("rest empty")
            else:
                logger.error(f"received garbage: {response}")
        else:
            logger.error(f"didn't receive enough data for response, only: {response}")

        return None

    def write_command(self, cmd: CommandBase, cmd_data: Optional[Union[bytes, int]] = None) \
            -> Union[Optional[bytes], Any]:
        """
        send command with payload and receive response if there is any

        :param cmd: Command id
        :param cmd_data: raw data, command-specific
        :return: parsed ResponsePacket if we received it successfully
        """
        return self.write(Packet.build(cmd, cmd_data))

    def set_brightness(self, percent: int):
        if not (0 <= percent <= 100):
            raise ValueError("out of range")

        return self.write_command(command.Command.SET_SYSTEM_BRIGHTNESS, percent)

    def set_score(self, blue_score: int, red_score: int):
        rs_lo = red_score & 0xff
        rs_hi = (red_score >> 8) & 0xff
        bs_lo = blue_score & 0xff
        bs_hi = (blue_score >> 8) & 0xff
        val = bytes([command.BoxMode.WATCH, 0, rs_lo, rs_hi, bs_lo, bs_hi, 0, 0, 0, 0])
        return self.write_command(command.Command.SET_BOX_MODE, val)

    def set_music_visualizer(self, visualizer: int):
        if not (0 <= visualizer <= 11):
            raise ValueError("visualizer id out of range")

        val = bytes([command.BoxMode.MUSIC, visualizer & 0xff] + [0] * 8)
        return self.write_command(command.Command.SET_BOX_MODE, val)

    def set_time(self, ts: Optional[datetime] = None):
        if ts is None:
            ts = datetime.now()

        year = ts.year
        month = ts.month
        day_of_month = ts.day
        hours = ts.hour
        minutes = ts.minute
        seconds = ts.second
        day_of_week = ts.isoweekday() % 7

        val = bytes([
            int(year % 100),
            int(year / 100),
            month,  # 1 to 12
            day_of_month,  # 1 to 31
            hours,
            minutes,
            seconds,
            day_of_week,  # 0=sun, 1=mon, ..6=sat
        ])
        return self.write_command(command.Command.SET_TIME, val)

    def set_game(self, enable: bool, game: int):
        if not (0 <= game <= 8):
            raise ValueError("game id out of range")

        val = bytes([int(enable), game])
        return self.write_command(command.Command.SET_GAME, val)

    def set_system_color(self, r: int, g: int, b: int):
        val = bytes([r & 0xff, g & 0xff, b & 0xff])
        return self.write_command(command.Command.SET_SYSTEM_COLOR, val)

    def set_sleep_color(self, r: int, g: int, b: int):
        val = bytes([r & 0xff, g & 0xff, b & 0xff])
        return self.write_command(command.Command.SET_SLEEP_COLOR, val)

    def get_box_mode(self) -> command.GetBoxMode:
        return self.write_command(command.Command.GET_BOX_MODE)

    def set_light_mode_clock(self, time_type: command.TimeType, red: int, green: int, blue: int,
                             modes: Optional[command.ActivatedModes] = None):
        if modes is None:
            modes = command.ActivatedModes.get_default()

        val = bytes([
            command.BoxMode.ENV.value,
            1,
            time_type.value,
            int(modes.clock),
            int(modes.weather),
            int(modes.temperature),
            int(modes.date),
            red,
            green,
            blue
        ])
        return self.write_command(command.Command.SET_BOX_MODE, val)

    def set_light_mode_temperature(self, box_mode: command.GetBoxMode):
        val = bytes([
            command.LightMode.TEMPERATURE.value,
            box_mode.temp_type,
            box_mode.temp_r,
            box_mode.temp_g,
            box_mode.temp_b,
            0
        ])
        return self.write_command(command.Command.SET_BOX_MODE, val)

    def send_app_newest_time(self, value: Optional[bool]):
        if value is None:
            value = -1 & 0xff
        else:
            value = int(value)
        return self.write_command(command.Command.SEND_APP_NEWEST_TIME, value)

    def set_light_mode_light(self, red: int, green: int, blue: int, modes: Optional[command.ActivatedModes] = None):
        if modes is None:
            modes = command.ActivatedModes.get_default()

        val = bytes([
            command.BoxMode.LIGHT.value,
            red,
            green,
            blue,
            0x14,
            0,
            int(modes.clock),
            int(modes.weather),
            int(modes.temperature),
            int(modes.date)
        ])
        return self.write_command(command.Command.SET_BOX_MODE, val)

    def set_light_mode_vj(self, pattern: int):
        if pattern < 0 or pattern > 15:
            raise ValueError("pattern id out of range")

        val = bytes([
            command.BoxMode.SPECIAL.value,
            pattern
        ])
        return self.write_command(command.Command.SET_BOX_MODE, val)
