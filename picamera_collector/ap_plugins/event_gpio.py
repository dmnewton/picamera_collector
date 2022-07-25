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

    def __init__(self,mode='local'):

        self.mode=mode
        path =pathlib.Path(__file__).parent
        
        with open(path / 'event_gpio.yaml') as file:
            self.config_data = yaml.load(file, Loader=yaml.FullLoader)

        # self.auth=(self.config_data['user'],self.config_data['password'])
        signal_pin = int(self.config_data.get('gpio_pin'))
        self.button = DigitalInputDevice(signal_pin)

        if self.config_data.get('gpio_normal') == 'low':

            self.button.when_activated = self.prepare_action
            self.button.when_deactivated = self.release_action
        else:
            self.button.when_deactivated = self.prepare_action
            self.button.when_activated = self.release_action

        
        self.bounce_ts = 0
        
        self.bounce_avoid = 1000


        self.state = 0

        if self.mode=='remote':
    
            self.url_take = [self.config_data['base_url'].format(x,self.config_data['takephoto']) for x in self.config_data['hosts']]
            self.url_lights = [self.config_data['base_url'].format(x,self.config_data['lighston']) for x in self.config_data['hosts']]

            self.sess = requests.Session()

            self.reconnect = [True] * len(self.config_data['hosts'])

            self.sio = [socketio.Client() for x in self.config_data['hosts']]
            self.connection_strings = ["http://{}:5000".format(x) for x in self.config_data['hosts']]
        else:
            self.eventbus=None

    def connect_to_camera(self,i):
        try:
            self.sio[i].connect(self.connection_strings[i])
            self.reconnect[i] = False
        except Exception as e:
            logger.error("unable to connect to %s", self.config_data['hosts'][i])
            logger.error(e) 
 
        
    def setup_sio(self):
        for i in range(len(self.sio)):
            if self.reconnect[i]:
                self.connect_to_camera(i)
            #if ~self.sio[i].connected:
            #    self.connect_to_camera(i)

    def success_call_back(x,reconnect,i):
        reconnect[i] = False
        logger.info("reconnect map %s", reconnect)

    def prepare_action(self):
        ts = round(time.time() * 1000)
        if ts < self.bounce_ts:
            logger.info("bounce avoid prepare")
            self.state = 0
        else:
            if (self.state == 0):
                self.bounce_ts = ts + self.bounce_avoid    
                logger.info("prepared")
                if self.mode=='local':
                    self.eventbus.emit('lightson',None)
                else:
                    self.setup_sio()
                    for x in self.url_lights:
                        try:
                            myResponse = self.sess.get(x)
                            logger.info("lighting resp %s", myResponse.text)
                        except:
                            logger.error("unable to send http message %s",x)
                self.state = 1


    def release_action(self):
        ts = round(time.time() * 1000)
        if ts < self.bounce_ts:
            logger.info("bounce avoid release")
            self.state = 1
        else:
            if (self.state == 1):
                self.bounce_ts = ts + self.bounce_avoid
               
                logger.info('release')
                if self.mode=='local':
                    self.eventbus.emit('takepicture',False,ts)
                else:
                    self.setup_sio()
                    for i in range(len(self.sio)):
                        try:
                            self.reconnect[i] = True
                            self.sio[i].emit('takephoto',ts,callback=self.success_call_back(self.reconnect,i))
                        #self.sio[i].call('takephoto',ts,timeout=5)
                        except Exception as e:
                            self.reconnect[i] = True
                            logger.error("unable to send sio message %s",self.config_data['hosts'][i])
                            logger.error(e) 
                self.state = 0
   
    def activate(self, app, eventbus):
        self.eventbus=eventbus
        return

if __name__ == '__main__':

    "use on a remote pi to trigger camera"
 
    logger.info("starting")

    bb = PluginModule('remote')

    pause()
