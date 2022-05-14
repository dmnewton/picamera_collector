import logging
import yaml
import time
#import threading
from gpiozero import DigitalOutputDevice
import pathlib

import eventlet

import logging
logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT,level=logging.INFO)

class PluginModule(object):
    def __init__(self):
        logger.info('background light  control')
        
        path =pathlib.Path(__file__).parent
        
        with open(path / 'light_control.yaml') as file:
            self.config_data = yaml.load(file, Loader=yaml.FullLoader)
        
        self.relay = DigitalOutputDevice(int(self.config_data['gpio_pin']),active_high=True)
        
        self.turn_off_time = time.time()

        self.check_sleep_time = int(self.config_data['checktime'])

        self.waittime = int(self.config_data['waittime'])

        self.set_turn_on_time()

        self.run()
    
    def worker(self):
        while True:
            current_time = time.time()
            logger.info('time %s %s %s',self.turn_off_time,current_time,self.relay)
            if (self.turn_off_time <= current_time) & self.relay.is_active:
                logger.info('turn off')
                self.relay.off()
            eventlet.sleep(self.check_sleep_time)
    
    def run(self):
        logger.info('run')
        eventlet.spawn(self.worker)
        eventlet.sleep(0)
        #threading.Thread(target=self.worker, daemon=True).start()

    def set_turn_on_time(self,*args):
        logger.info('turn on')
        self.relay.on()
        self.turn_off_time = time.time() + self.waittime

    def set_turn_on_time_service(self):
        self.set_turn_on_time()
        return('OK')
        

    def activate(self,app,eventbus):
        eventbus.add_listener('lightson', self.set_turn_on_time)
        app.add_url_rule('/api/v1/resources/lighston', view_func=self.set_turn_on_time_service)


if __name__ == '__main__':
    bs = PluginModule()
    eventlet.sleep(3)
    bs.set_turn_on_time()
    eventlet.sleep(20)