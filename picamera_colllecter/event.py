from gpiozero import Button
import time
from signal import pause
import requests
import yaml

import logging
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

url = "http://[::1]:5000/api/v1/resources/takepicture"
url_gcs = "http://[::1]:5000/api/v1/resources/send_to_gcs/{}"


with open(r'app_settings.yaml') as file:
    config_data = yaml.load(file, Loader=yaml.FullLoader)
auth=next(iter(config_data['users'].items()))


def prepare_action():
    global state
    logger.info("prepared")
    state = 1
    time.sleep(1)

def release_action():
    global state
    logger.info('release')
    if state == 1:
        start=time.time()
        myResponse = requests.get(url,auth=auth)
        logger.info("photo resp %s", myResponse)
        myResponse = requests.get(url_gcs.format(myResponse.text),auth=auth)
        end=time.time()
        logger.info("process time %f", end-start)
        state = 0
        time.sleep(1)

if __name__ == '__main__':

    logger.info("starting")

    state = 0

    button = Button(17)

    button.when_deactivated = prepare_action
    button.when_activated = release_action

    pause()