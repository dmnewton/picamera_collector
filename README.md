# picamera_collector

To helps collect Image data for your AI project using the inexpensive Raspberry PI Camera.<br>
This tool supports three important steps
* Focus - in video mode allows you to focus your camera - important with HQ Camera
* Lighting - find the best setting for you object - important if it's moving
* Automation - use GPIO signals to trigger data collection

## Instructions

Install lite  raspios image using etcher <br>
2021-03-04-raspios-buster-armhf-lite.zip

mount on pc/mac <br>
enable ssh on boot<br>
touch /Volumes/boot/ssh


### If a pizero

enable device access via USB so you can configure WLAN etc.<br>
or you can connect keyboard and screen<br>

edit /Volumes/boot/config.txt<br>
dtoverlay=dwc2

edit /Volumes/boot/cmdline.txt after rootwait <br>
modules-load=dwc2,g_ether

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

## Install python and pip

```shell
sudo apt update
sudo apt install python3 git python3-pip
```
## install software as pip module
```shell
pip3 install git+https://github.com/dmnewton/picamera_colllecter.git
```

## start as service
```shell
cd /home/pi/.local/lib/python3.7/site-packages/picamera_colllecter
sudo cp camera.service /etc/systemd/system/
sudo systemctl enable camera.service
sudo systemctl start camera.service
sudo systemctl status camera.service
```

## Sendig to google cloud storage

edit app_settings.yaml

## copy over google service key
```shell
scp google-service-key.json pi@raspberrypi:
```


