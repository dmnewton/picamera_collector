import os
import io
import time
import yaml
import pathlib
import datetime
import requests

from queue import Queue
import threading 

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
        
        with open(path / 'store_to_rest.yaml') as file:
            self.config_data = yaml.load(file, Loader=yaml.FullLoader)
        logger.info('background store to rest api')
        self.myhost = os.uname()[1]
        self.thread_queue = Queue()
        self.url = "http://{}:{}/{}".format(self.config_data['hostname'],self.config_data['port'],self.config_data['url'])
        self.run()

    def store_action(self,epoch_time,sequence,blob,file_suffix):
        series = '{:02d}'.format(sequence)
        content_type = mime_types.get(file_suffix)
        dt = datetime.datetime.fromtimestamp(epoch_time/1000).strftime('%Y-%m-%d')
        destination_blob_name = "{}/{}-{}-{}.{}".format(dt,self.myhost,epoch_time,series,file_suffix)

        retry = True
        while retry:
            try:
                #stream_str = io.BytesIO(blob.encode())
                stream_str = io.BytesIO(blob)
                stream_str.seek(0)
                file = {'file': (destination_blob_name, stream_str, 'image/jpg')}
                #header = {"application-id": appID, "secret-key": restKey, "application-type": "REST"}
                r = requests.post(self.url, files=file)
                if r.status_code != 201:
                    raise Exception('return coode not 201')
                retry = False
            except Exception as e:
                logger.error('Failed to upload to rest api: '+ str(e))
                logger.error("sleeping 1 minute")
                time.sleep(60)

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
        threading.Thread(target=self.worker,daemon=True).start()

    def add_job(self,job):
        self.thread_queue.put(job)

    
    def activate(self,app,eventbus):
        eventbus.add_listener('storefile', self.add_job)
        return

if __name__ == '__main__':
    bs = PluginModule()
    for i in range(10):
        epoch_time = int(time.time()*1000)
        data = " a string plus " + str(epoch_time)
        bs.add_job((epoch_time,0,"abc","json"))
    bs.thread_queue.join()