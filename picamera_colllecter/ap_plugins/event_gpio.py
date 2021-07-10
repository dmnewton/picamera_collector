from gpiozero import Button
import time
from signal import pause
import requests

import logging
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

base_url = "http://{}:5000/api/v1/resources/takesend"

class PluginModule(object):
    "this can be use locally as plugin or run on remote device to trigger picture"

    def __init__(self,cf):
        self.auth=next(iter(cf.config_data['users'].items()))
        self.button = Button(17)
        self.button.when_deactivated = self.prepare_action
        self.button.when_activated = self.release_action
        self.state = 0
        self.url = base_url.format('[::1]')

    def prepare_action(self):
        logger.info("prepared")
        self.state = 1
        time.sleep(1)

    def remote_url(self,host):
        self.url = base_url.format(host)


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
    from picamera_colllecter.config import Configuration
    cf = Configuration()

    logger.info("starting")

    bb = PluginModule(cf)
    bb.remote_url(cf.config_data['camerahost'])

    pause()