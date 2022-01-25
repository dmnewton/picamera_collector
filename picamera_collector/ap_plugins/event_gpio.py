from gpiozero import DigitalInputDevice
import time
from signal import pause
import requests
import yaml
import pathlib
import socketio

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
        self.button = DigitalInputDevice(signal_pin)

        self.button.when_activated = self.prepare_action
        self.button.when_deactivated = self.release_action
        
        self.bounce_ts = 0
        
        self.bounce_avoid = 1000

        self.bounce_last = None

        self.state = 0
    
        self.url_take = [self.config_data['base_url'].format(x,self.config_data['takephoto']) for x in self.config_data['hosts']]
        self.url_lights = [self.config_data['base_url'].format(x,self.config_data['lighston']) for x in self.config_data['hosts']]

        self.sess = requests.Session()

        #self.sess.verify = True

        self.sio = [socketio.Client() for x in self.config_data['hosts']]
        self.connection_strings = ["http://{}:5000".format(x) for x in self.config_data['hosts']]

        for i in range(len(self.sio)):
            try:
                self.sio[i].connect(self.connection_strings[i])
            except:
                logger.error("unable to send message %s",i)
        
    def setup_sio(self):
        for i in range(len(self.sio)):
            if self.sio[i].connected == None:
                try:
                    self.sio[i].connect(self.connection_strings[i])
                except:
                    logger.error("unable to send message %s",i)

    def prepare_action(self):
        ts = round(time.time() * 1000)
        if (ts - self.bounce_ts) < self.bounce_avoid:
            logger.debug("bounce avoid prepare")
            self.state = 0
        else:
            if (self.state == 0):
                self.bounce_ts = ts    
                self.setup_sio()
                logger.info("prepared")
                for x in self.url_lights:
                    try:
                        myResponse = self.sess.get(x)
                    except:
                        logger.error("unable to send message %s",x)
                #myResponse = self.sess.get(self.url_lights,auth=self.auth)
                logger.info("lighting resp %s", myResponse.text)
                self.state = 1
        


    def release_action(self):
        ts = round(time.time() * 1000)
        if (ts - self.bounce_ts) < self.bounce_avoid:
            logger.debug("bounce avoid release")
            self.state = 1
        else:
            if (self.state == 1):
                self.bounce_ts = ts 
                self.setup_sio()
                logger.info('release')
                for i in range(len(self.sio)):
                    try:
                        self.sio[i].emit('takephoto',ts)
                    except:
                        logger.error("unable to send message %d",i)
                self.state = 0
   
    def activate(self,app):
        return

if __name__ == '__main__':

    "use on a remote pi to trigger camera"
 
    logger.info("starting")


    bb = PluginModule()

    pause()