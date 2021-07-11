from gpiozero import Button
import time
from signal import pause
import requests
import yaml
import pathlib

import logging
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)



class PluginModule(object):
    "this can be use locally as plugin or run on remote device to trigger picture"

    def __init__(self):
        path =pathlib.Path(__file__).parent
        
        with open(path / 'event_gpio.yaml') as file:
            self.config_data = yaml.load(file, Loader=yaml.FullLoader)

        self.auth=(self.config_data['user'],self.config_data['password'])
        signal_pin = int(self.config_data.get('gpio_pin'))
        self.button = Button(signal_pin)
        self.button.when_deactivated = self.prepare_action
        self.button.when_activated = self.release_action
        self.state = 0
        self.url = self.config_data['base_url'].format('[::1]')

    def prepare_action(self):
        logger.info("prepared")
        self.state = 1
        time.sleep(1)


    def release_action(self):
        logger.info('release')
        if self.state == 1:
            myResponse = requests.get(self.url,auth=self.auth)
            logger.info("photo resp %s", myResponse.text)
            self.state = 0
        time.sleep(1)
    
    def activate(self,app):
        return

if __name__ == '__main__':

    "use on a remote pi to trigger camera"
 
    logger.info("starting")

    bb = PluginModule()

    pause()