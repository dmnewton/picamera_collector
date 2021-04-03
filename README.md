# picamera

install lite  PI image using etcher <br>
2021-03-04-raspios-buster-armhf-lite.zip

enable ssh access via USB so you can configure WLAN etc.

mount on mac <br>

touch /Volumes/boot/ssh

edit /Volumes/boot/config.txt<br>
dtoverlay=dwc2

edit /Volumes/boot/cmdline.txt after rootwait <br>
modules-load=dwc2,g_ether

Now you can connect via usb<br>

ssh pi@raspberrypi.local

password is raspberry <br>

raspi-config<br>
  your wifi<br>
  enable camera<br>
  gpu 128<br>
  change password

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
sudo cp myscript.service /etc/systemd/system/myscript.service <br>
sudo systemctl enable myscript.service <br>
sudo systemctl status myscript.service
```
