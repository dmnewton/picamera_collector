# picamera_collector

This tool helps you collect pictures for your AI project using the inexpensive Raspberry PI Camera.<br>

This tool supports three important steps
* Focus - a video mode allows you to focus your camera - important with HQ Camera
* Lighting - find the best setting for you object - important if it's moving
* Automation - use GPIO signals to trigger data collection
* Storage - upload to cloud storage

The trigger can come from a remote device

## Instructions

This is based on picamera which is not yet compatibel with bullseye <br>

If installing on a pi zero use lite image (also good option if not conncting PI to monitor) <br>

https://downloads.raspberrypi.org/raspios_oldstable_lite_armhf/images/raspios_oldstable_lite_armhf-2021-12-02/2021-12-02-raspios-buster-armhf-lite.zip

Install the buster raspios image using etcher <br>

https://www.balena.io/etcher/

## Prepare SD Crad

### Enable ssh access - important if you plan to use headless

remove an dreinsert SD Card to mount on pc/mac <br>
```shell
touch /Volumes/boot/ssh
```

### If a pizero

enable device access via USB so you can configure WLAN etc.<br>
or you can connect keyboard and screen<br>
turbo and voltage are required for system stability when camera is attacehd to a zero<br>

edit /Volumes/boot/config.txt<br>
```shell
[pi0]
gpu_mem=128
start_x=1
dtoverlay=dwc2
force_turbo=1
over_voltage=4
```

edit /Volumes/boot/cmdline.txt after rootwait <br>
```shell
modules-load=dwc2,g_ether
```

Now you can connect via usb<br>


## Install SD card and boot

ssh pi@raspberrypi<br>
or<br>
ssh pi@raspberrypi.local (when via USB)<br>

initial password is raspberry <br>

sudo raspi-config<br>
*  hostname
*  your wifi<br>
*  enable camera<br>
*  gpu 128<br>
*  change password fo pi


## prepare environmnet with latest software
```shell
sudo apt update
sudo apt full-upgrade
```

## time
add local time server  <br>
```shell
sudo vim.tiny /etc/systemd/timesyncd.conf

[Time]
NTP=fritz.box

sudo systemctl restart systemd-timesyncd.service 

timedatectl timesync-status
```



## Install python , pip and git
```shell
sudo apt install python3 git python3-pip
```

## update pip packages
does not work!
```shell
pip3 freeze > requirements.txt
sed -i 's/==/>=/g' requirements.txt 
pip3 install -r requirements.txt --upgrade
```

## install software as pip module or clone
```shell
pip3 install git+https://github.com/dmnewton/picamera_collector.git
or
git clone https://github.com/dmnewton/picamera_collector.git
```

## start as service

Chose camera.service or trigger.service

```shell
cd /home/pi/.local/lib/python3.7/site-packages/picamera_colllecter
sudo cp camera.service /etc/systemd/system/
sudo systemctl enable camera.service
sudo systemctl start camera.service
sudo systemctl status camera.service
```

## browser access
```shell
http://<hostname>:5000
```
userid password are defined in the yaml

## plugins

One definable triger and storage function

## Sending to google cloud storage

edit app_settings.yaml

## copy over google service key
```shell
scp google-service-key.json pi@raspberrypi:
```

## when using a lan network adaptor on pi zero

```shell
sudo nano /boot/config.txt
at end add
dtoverlay=disable-wifi
dtoverlay=disable-bt

sudo nano /etc/network/if-pre-up.d/ethtool
at end add
$ETHTOOL --change eth0 advertise 0x008
```
