from gpiozero import Button
import time
from signal import pause
import requests
import yaml
import pathlib
import socketio

import eventlet

import logging
logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT,level=logging.INFO)

class PluginModule(object):
    "this can be use locally as plugin or run on remote device to trigger picture"

    def __init__(self):
        path =pathlib.Path(__file__).parent
        
        with open(path / 'event_gpio.yaml') as file:
            self.config_data = yaml.load(file, Loader=yaml.FullLoader)

        # self.auth=(self.config_data['user'],self.config_data['password'])
        signal_pin = int(self.config_data.get('gpio_pin'))
        self.button = Button(signal_pin)
        #self.button.when_deactivated = self.prepare_action
        #self.button.when_activated = self.release_action

        self.button.when_activated = self.prepare_action
        self.button.when_deactivated = self.release_action

        self.state = 0
    
        self.url_take = [self.config_data['base_url'].format(x,self.config_data['takephoto']) for x in self.config_data['hosts']]
        self.url_lights = [self.config_data['base_url'].format(x,self.config_data['lighston']) for x in self.config_data['hosts']]

        self.sess = requests.Session()
        #self.sess.verify = True

        self.sio = [socketio.Client() for x in self.config_data['hosts']]
        self.connection_strings = ["http://{}:5000".format(x) for x in self.config_data['hosts']] 
        
    def setup_sio(self):
        for i in range(len(self.sio)):
            if self.sio[i].sid == None:
                 self.sio[i].connect(self.connection_strings[i])

    def prepare_action(self):

        self.setup_sio()
        logger.info("prepared")
        for x in self.url_lights:
            myResponse = self.sess.get(x)
        #myResponse = self.sess.get(self.url_lights,auth=self.auth)
            logger.info("lighting resp %s", myResponse.text)
        self.state = 1
        eventlet.sleep(1)


    def release_action(self):
        self.setup_sio()
        logger.info('release')
        if self.state == 1:
            ts = round(time.time() * 1000)
            #url = self.url_take + '?ts=' + str(ts)
            #logger.info("url %s",url)
            for i in range(len(self.sio)):
                self.sio[i].emit('takephoto',ts)
            #myResponse = self.sess.get(url)
            #myResponse = self.sess.get(url,auth=self.auth)
            #logger.info("photo resp %s", myResponse.text)
            self.state = 0
        eventlet.sleep(1)
    
    def activate(self,app):
        return

if __name__ == '__main__':

    "use on a remote pi to trigger camera"
 
    logger.info("starting")

    bb = PluginModule()

    pause()