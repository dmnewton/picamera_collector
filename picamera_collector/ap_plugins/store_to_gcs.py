import os
import time
import yaml
import pathlib
import datetime

import eventlet

#from queue import Queue
#import threading 

from google.cloud import storage

import logging
logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT,level=logging.INFO)

mime_types = {'jpg':'image/jpeg',
    'h264':'video/mp4',
    'json': 'application/json'
}

class PluginModule(object):
    def __init__(self):
        path =pathlib.Path(__file__).parent
        
        with open(path / 'store_to_gcs.yaml') as file:
            self.config_data = yaml.load(file, Loader=yaml.FullLoader)
        logger.info('background store to google initiated')
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.config_data['authfile']
        self.myhost = os.uname()[1]
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(self.config_data['bucket'])
        self.thread_queue = eventlet.Queue()
        self.run()

    def store_action(self,epoch_time,sequence,blob,file_suffix):
        series = '{:02d}'.format(sequence)
        content_type = mime_types.get(file_suffix)
        dt = datetime.datetime.fromtimestamp(epoch_time/1000).strftime('%Y-%m-%d')
        destination_blob_name = "{}/{}/{}-{}-{}.{}".format(self.config_data['directory'],dt,self.myhost,epoch_time,series,file_suffix)

        blob_location = self.bucket.blob(destination_blob_name)

        blob_location.upload_from_string(blob,content_type=content_type)
        logger.info(
            "File uploaded to {} ".format(
                 destination_blob_name
            )
        )
        return 'OK'

    def worker(self):
        while True:
            epoch_time,sequence,blob,file_suffix = self.thread_queue.get()
            self.store_action(epoch_time,sequence,blob,file_suffix)
            self.thread_queue.task_done()
    
    def run(self):
        eventlet.spawn(self.worker)
        eventlet.sleep(0)

    def add_job(self,job):
        self.thread_queue.put(job)
    
    def activate(self,app):
        return

if __name__ == '__main__':
    bs = PluginModule()
    eventlet.sleep(1)
    epoch_time = int(time.time()*1000)
    bs.add_job((epoch_time,0,"abc"))
    eventlet.sleep(10)