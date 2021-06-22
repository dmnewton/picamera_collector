from gpiozero import Button
from time import sleep
from signal import pause
import time
import requests
import yaml
from requests.auth import HTTPBasicAuth

import picamera_colllecter
import logging
logging.basicConfig(level=logging.INFO) 

def execute_ws():
    global config_data
    print(config_data)
    r =requests.get(config_data.get('url'), auth=HTTPBasicAuth(config_data.get('user'), config_data.get('password')))
    logging.info(r.text)


def prepare_action():
    global state
    print("prepared")
    state = 1
    time.sleep(1)

def release_action():
    global state
    print('release')
    if state == 2:
        print('release')
        start=time.time()
        execute_ws()
        end=time.time()
        print("process time", end-start)
        state = 0
        time.sleep(1)

if __name__ == '__main__':

    with open(picamera_colllecter.__path__[0]+'/remote_trigger_settings.yaml') as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)

    state = 0

    signal_pin = int(config_data.get('gpio_pin'))

    button = Button(17)

    button.when_activated = prepare_action
    button.when_deactivated = release_action

    execute_ws()

    #pause()