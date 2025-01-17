# divo

Divoom Pixoo and Divoom Timebox Evo python controller, packet builder/parser and image renderer.

This project aims to fully implement controlling everything the Pixoo can do. (WIP)

## Requirements

* Python 3.6+

## Examples

Hints:

* you need a terminal that can render the colors to see the images properly 
* add `--send --mac-address 11:75:58:xx:xx:xx` to send these packets to your Pixoo
* add `--debug` for debug output
* there are a lot of tests demo'ing most of the Pixoo modes in the sub-command `./main.py test`

Send image file (16x16 px):

```shell
./main.py img --send --mac-address 11:75:58:xx:xx:xx test.png
```

Mudkip ([source](https://pixel.divoom-gz.com/#/pages/index/udetail?uid=400541387&suid=401026599)):

```shell
./main.py raw 01860044000a0a04aa7f00f40100080000004dbbef2989c8c1c3c5ff9f00ffffff1f1f30bf5c1500002001000000002402000000002402000000004402000000904409000000922449b00140922449b20d64d22469420e64e22471420e27e32471c80ff89b2449ff0d00d6b6adb60d00a06d92b40d00a06d89a40100106d89a401001049893400512802
```

Mudkip (eyes closed):

```shell
./main.py raw 01860044000a0a04aa7f00f40100080000004dbbef2989c8c1c3c5ff9f001f1f30bf5c15ffffff00000000000000002001000000002402000000002402000000004402000000904409000000922449006c40922449826d64922449426e64da2469436e2693264d486fb09f24c9ed6d00f6ffbfb66d00a06d92a40d00106d89a401001049893400142702
```

Nyan Cat:

```shell
./main.py raw 01e40044000a0a04aadd00f401001212173dffffffff0000000000293268ffaa00f193ed7b757bffff02e547da00ff005b585b00aaff6b74b2aa01ff909eddc1d9f2a5e6ff0004000000000000000000000000000000004000420821c618638c4108214208314a29659432c820a594518a31e38c31c619a594518c31e39c73ce1908a1518c49e38471c21808a1519231e38c71c6184aa9518c31c39cb38e194aa9518a49e3ac75d6198c31364a29658c31c6688c3176c618638c735a6bce39b7d67befbdb5de7bce39f7de7befbdf7c27b1042082184104218608031400821841042080384515d02
```

Palette 4 color test:

```shell
./main.py raw 015a0044000a0a04aa5300f4010004000000ff0000ff5500ffffffe40000c0000000300000000c000000030000c0000000300000000c000000030000c0000000300000000c000000030000c0000000300000000c00000003000000dc0c02
```

Palette 8 color test:

```shell
./main.py raw 01860044000a0a04aa7f00f4010008000000ff0000ff5500ffaa00ffff02adff0000ff00ffffff88c6fa0000e000000000001c000000008003000000007000000000000e00000000c001000000003800000000000700000000e000000000001c000000008003000000007000000000000e00000000c00100000000380000000000070000000000ee1602
```

Set up raspbian on raspberry pi 4:
```shell
#git clone repo
sudo apt install python3 python3-pip libopenjp2-7 libtiff5 zlib1g-dev libjpeg-dev pulseaudio-module-bluetooth bluez pi-bluetooth #bluez-tools
#to install pulse-audio as root
sudo bash divo/raspberry-pi/setup.sh
sudo adduser pi bluetooth
sudo adduser pi pulse
sudo adduser pi pulse-access

cd divo 
pip3 install -r requirements.txt
cd divo 

bluetoothctl power on
bluetoothctl agent on
bluetoothctl scan on #first time setup
bluetoothctl devices #first time setup
bluetoothctl pair 11:75:58:xx:xx:xx #first time setup
bluetoothctl trust 11:75:58:xx:xx:xx #first time setup
bluetoothctl connect 11:75:58:xx:xx:xx #can just do this after paired and trusted
#if you don't install pulseaudio as root
#pulseaudio --start
#pactl load-module module-bluetooth-discover
sudo pactl list sources short
sudo pactl set-default-sink 1

# you can also play audio with mplayer

```

WIP Docker - this works but maybe/probably over-privileged  
```shell
docker run -ti --privileged --net=host -v /dev/bus/usb:/dev/bus/usb -v /run/dbus:/run/dbus -v /var/run/dbus:/var/run/dbus -v /var/run/sdp:/var/run/sdp -v /home/pi/divo:/opt/divo --cap-add=ALL debian
apt update; apt install -y python3 python3-pip libopenjp2-7 libtiff5 zlib1g-dev libjpeg-dev pulseaudio-module-bluetooth bluez
# can resume above steps from pip3 install
```
