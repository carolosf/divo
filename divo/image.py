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

from math import ceil, log
from typing import List

from colorconsole import terminal


class Color:
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b})"


class Palette:
    def __init__(self):
        self.palette = []

    def __getitem__(self, item):
        return self.palette[item]

    def clear(self):
        self.palette.clear()

    def bits_per_pixel(self) -> int:
        return ceil(log(len(self.palette), 2))

    def print_to(self, screen: "Screen"):
        screen.print_palette(self.palette)


class ImageBuffer:
    def __init__(self, **kwargs):
        self.width = kwargs.get("width", 16)
        self.height = kwargs.get("height", self.width)
        self.default_value = kwargs.get("default_value", Color(0, 0, 0))

        self.buf = [[self.default_value]*self.width for _ in range(self.height)]

    def set(self, x: int, y: int, color: Color):
        self.buf[y][x] = color

    def print_to(self, screen: 'Screen'):
        for row in self.buf:
            for pixel in row:
                screen.print_color(pixel)

            screen.line_end()


class Screen:
    def __init__(self, **kwargs):
        self.screen = terminal.get_terminal(conEmu=False)
        self.block = kwargs.get("block", "██")

    def print_color(self, color: Color):
        self.screen.xterm24bit_set_fg_color(color.r, color.g, color.b)
        print(self.block, end="")
        self.screen.reset()

    @staticmethod
    def line_end():
        print()

    def print_palette(self, palette: List[Color]):
        print(f"Palette ({len(palette)}):")
        for i, color in enumerate(palette):
            print(i, end=" ")
            self.print_color(color)
            print("", color)
        print("\n")
