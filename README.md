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

```shell
sudo apt update
sudo apt install python3 git python3-pip
```

```shell
pip3 install git+https://github.com/dmnewton/picamera_colllecter.git
```
