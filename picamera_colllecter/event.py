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

class ButtonEvent(object):

    def __init__(self):
        with open(r'app_settings.yaml') as file:
            config_data = yaml.load(file, Loader=yaml.FullLoader)
        self.auth=next(iter(config_data['users'].items()))
        self.button = Button(17)
        self.button.when_deactivated = self.prepare_action
        self.button.when_activated = self.release_action
        self.state = 0

    def prepare_action(self):
        logger.info("prepared")
        self.state = 1
        time.sleep(1)

    def release_action(self):
        logger.info('release')
        if self.state == 1:
            start=time.time()
            myResponse = requests.get(url,auth=self.auth)
            logger.info("photo resp %s", myResponse)
            myResponse = requests.get(url_gcs.format(myResponse.text),auth=self.auth)
            end=time.time()
            logger.info("process time %f", end-start)
            self.state = 0
        time.sleep(1)

if __name__ == '__main__':

    logger.info("starting")

    bb = ButtonEvent()

    pause()