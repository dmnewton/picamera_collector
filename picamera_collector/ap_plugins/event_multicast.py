from gpiozero import DigitalInputDevice
import time
from signal import pause
import yaml
import pathlib
import socket
import struct
import io
import pickle

import logging
logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT,level=logging.INFO)

class PluginModule(object):
    "this can be use locally as plugin or run on remote device to trigger picture"

    def __init__(self):
        path =pathlib.Path(__file__).parent
        
        with open(path / 'event_multicast.yaml') as file:
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

        self.addrinfo = socket.getaddrinfo(self.config_data.get('mgroup'), None)[0]

        self.s = socket.socket(self.addrinfo[0], socket.SOCK_DGRAM)

        # Set Time-to-live (optional)
        ttl_bin = struct.pack('@i', self.config_data.get('mttl'))

        self.s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
    
    def prepare_action(self):
        ts = round(time.time() * 1000)
        if (ts - self.bounce_ts) < self.bounce_avoid:
            logger.debug("bounce avoid prepare")
            self.state = 0
        else:
            if (self.state == 0):
                self.bounce_ts = ts    
                logger.info("prepared")
                pickleBuffer = io.BytesIO()
                pickle.dump((ts,self.config_data.get('lighston')), pickleBuffer)
                self.s.sendto(pickleBuffer.getvalue() , (self.addrinfo[4][0], self.config_data.get('mport')))
                self.state = 1

    def release_action(self):
        ts = round(time.time() * 1000)
        if (ts - self.bounce_ts) < self.bounce_avoid:
            logger.debug("bounce avoid release")
            self.state = 1
        else:
            if (self.state == 1):
                self.bounce_ts = ts
                logger.info("release") 
                pickleBuffer = io.BytesIO()
                pickle.dump((ts,self.config_data.get('takephoto')), pickleBuffer)
                self.s.sendto(pickleBuffer.getvalue() , (self.addrinfo[4][0], self.config_data.get('mport')))
                self.state = 0
   
    def activate(self,app):
        return

if __name__ == '__main__':

    "use on a remote pi to trigger camera"
 
    logger.info("starting")


    bb = PluginModule()

    pause()