import os
import time

from queue import Queue
import threading 

from google.cloud import storage

import logging
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

from picamera_colllecter.config import Configuration
cf = Configuration().config_data['gcs']

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cf['authfile']

storage_client = storage.Client()
bucket = storage_client.bucket(cf['bucket'])


class PluginModule(object):
    def __init__(self):
        logger.info('background store to google initiated')
        self.thread_queue = Queue()
        self.run()

    @staticmethod
    def store_action(phototime,image):
        epoch_time = int(phototime*1000)
        destination_blob_name = "{}/image-{}.{}".format(cf['directory'],epoch_time,'jpg')

        blob = bucket.blob(destination_blob_name)
        content_type='image/jpeg'
        rr = blob.upload_from_string(image,content_type=content_type)
        logger.info(
            "File uploaded to {} ".format(
                 destination_blob_name
            )
        )
        return 'OK'

    def worker(self):
        while True:
            phototime,image = self.thread_queue.get()
            self.store_action(phototime,image)
            self.thread_queue.task_done()
    
    def run(self):
        threading.Thread(target=self.worker, daemon=True).start()

    def add_job(self,job):
        self.thread_queue.put(job)
    
    def activate(self,app):
        return

if __name__ == '__main__':
    bs = PluginModule()
    time.sleep(1)
    bs.add_job((time.time(),"abc"))
    time.sleep(10)

    