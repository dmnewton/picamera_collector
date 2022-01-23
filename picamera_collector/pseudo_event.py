from gpiozero import DigitalOutputDevice
from time import sleep

sleep_time = 5

test_pin = DigitalOutputDevice(17)

while True:
    test_pin.on()
    sleep(sleep_time)
    test_pin.off()
    sleep(sleep_time)