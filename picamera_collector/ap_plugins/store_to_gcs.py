import os
import time
import yaml
import pathlib

from queue import Queue
import threading 

from google.cloud import storage

import logging
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

class PluginModule(object):
    def __init__(self):
        path =pathlib.Path(__file__).parent
        
        with open(path / 'store_to_gcs.yaml') as file:
            self.config_data = yaml.load(file, Loader=yaml.FullLoader)
        logger.info('background store to google initiated')
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.config_data['authfile']
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(self.config_data['bucket'])
        self.thread_queue = Queue()
        self.run()

    def store_action(self,phototime,image,file_suffix):
        epoch_time = int(phototime*1000)
        if file_suffix == 'jpg':
            content_type='image/jpeg'
        else:
            content_type='video/mp4'
        destination_blob_name = "{}/image-{}.{}".format(self.config_data['directory'],epoch_time,file_suffix)

        blob = self.bucket.blob(destination_blob_name)

        rr = blob.upload_from_string(image,content_type=content_type)
        logger.info(
            "File uploaded to {} ".format(
                 destination_blob_name
            )
        )
        return 'OK'

    def worker(self):
        while True:
            phototime,image,content_type = self.thread_queue.get()
            self.store_action(phototime,image,content_type)
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