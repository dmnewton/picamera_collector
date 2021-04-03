# picamera

install lite  PI image using etcher <br>
2021-03-04-raspios-buster-armhf-lite.zip

mount on mac <br>
touch /Volumes/boot/ssh

if pizero

enable ssh access via USB so you can configure WLAN etc.

edit /Volumes/boot/config.txt<br>
dtoverlay=dwc2

edit /Volumes/boot/cmdline.txt after rootwait <br>
modules-load=dwc2,g_ether

Now you can connect via usb<br>

ssh pi@raspberrypi.local

if normal pi
  touch /Volumes/boot/ssh
  ssh pi@raspberrypi

initial password is raspberry <br>

raspi-config<br>
*  hostname
*  your wifi<br>
*  enable camera<br>
*  gpu 128<br>
*  change password fo pi

## install python and pip

```shell
sudo apt update
sudo apt install python3 git python3-pip
```
## install module
```shell
pip3 install git+https://github.com/dmnewton/picamera_colllecter.git
```

## start as service
```shell
cd /home/pi/.local/lib/python3.7/site-packages/picamera_colllecter
sudo cp camera.service /etc/systemd/system/ <br>
sudo systemctl enable camera.service <br>
sudo systemctl status camera.service
```
