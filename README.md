# picamera_collector

To package helps you collect pictures for your AI project using the inexpensive Raspberry PI Camera.<br>
This tool supports three important steps
* Focus - in video mode allows you to focus your camera - important with HQ Camera
* Lighting - find the best setting for you object - important if it's moving
* Automation - use GPIO signals to trigger data collection

The trigger can come from an remote device

## Instructions

Install lite  raspios image using etcher <br>
https://www.balena.io/etcher/

2021-03-04-raspios-buster-armhf-lite.zip

mount on pc/mac <br>
enable ssh on boot<br>
touch /Volumes/boot/ssh


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

## access

http://localhost:5000

userid password are defined in the yaml

# plugins

One definable triger and storage function

## Sending to google cloud storage

edit app_settings.yaml

## copy over google service key
```shell
scp google-service-key.json pi@raspberrypi:
```


