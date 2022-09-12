import time
import yaml
import pathlib
import eventlet
import json

import eventlet.green.socket as socket

import logging
logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT,level=logging.INFO)

class PluginModule(object):
    "this can be use locally as plugin or run on remote device to trigger picture"

    def __init__(self):
        path =pathlib.Path(__file__).parent
        
        with open(path / 'event_wago.yaml') as file:
            self.config_data = yaml.load(file, Loader=yaml.FullLoader)



        self.bounce_ts = 0
        
        self.bounce_avoid = 1000

        self.state = 0

        self.io_port = self.config_data.get('io_port') 

        self.wIO_client = None
        self.try_configure_connection()

        self.eventbus=None

        self.run()
    
    def configure_connection(self):
        client_wIO_IP =  socket.gethostbyname(self.config_data.get('address') )
        port = self.config_data.get('port')

        self.wIO_client = socket.create_connection((client_wIO_IP, port))

        pwinall = ""

        # set keep alive so we can recognise a dead box and attempt restart

        x = self.wIO_client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        self.wIO_client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1 * 60)
        self.wIO_client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1 * 10)
        self.wIO_client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 1) 

        logger.info('keep alive %s',x)

    def try_configure_connection(self):
        try:
            self.configure_connection()
            logger.info('sucessfully configured connection')
            return False
        except Exception as e:
            logger.info('failed to configure connection %s',e)
            eventlet.sleep(10)
            return True
            

    def next_message(self):
        restart = False
        while True:
            if (self.wIO_client == None) or restart :
                restart=self.try_configure_connection()
                continue
            try:
                recv = self.wIO_client.recv(4096)
                yield recv
            except Exception as e:
                logger.info("unexpected exception on socket %s",e)
                restart=True



    def worker(self):
        for msg  in self.next_message():
            try:
                # sometime you get multiple messages in one package 
                ts_server = round(time.time() * 1000)
        
                logger.info('message %s ',msg)

                data = json.loads(msg)

                logger.info('message %s ',data)

                input_pin_value = data.get(self.config_data.get('io_port'))

                logger.debug('value %s ', input_pin_value)

                if self.state == input_pin_value:
                    logger.debug('i did not change')
                    return

                self.state = input_pin_value

                if ts_server < self.bounce_ts:
                    logger.info('ignored bounce')
                    return

                self.bounce_ts = ts_server + self.bounce_avoid
            
                if input_pin_value:
                    logger.info('light on')
                    self.eventbus.emit('lightson',None)
                else:
                    logger.info('take photo')
                    self.eventbus.emit('takepicture',False,ts_server)
            except Exception as e:
                 logger.info('bad message %s',e)


    def run(self):
        logger.info('run')
        eventlet.spawn(self.worker)
        eventlet.sleep(0)
       
    def activate(self,app,eventbus):
        self.eventbus=eventbus
        return

if __name__ == '__main__':

    "use on a remote pi to trigger camera"
 
    logger.info("starting")


    bb = PluginModule()

    while True:
        eventlet.sleep(1)