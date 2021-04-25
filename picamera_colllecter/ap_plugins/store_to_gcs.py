import os
import time
from google.cloud import storage

import logging
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

from config import Configuration
cf = Configuration().config_data['gcs']

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cf['authfile']

storage_client = storage.Client()
bucket = storage_client.bucket(cf['bucket'])

def store_action(image):
    epoch_time = int(time.time())
    destination_blob_name = "{}/image-{}.jpg".format(cf['directory'],epoch_time)

    blob = bucket.blob(destination_blob_name)
    rr = blob.upload_from_string(image,content_type='image/jpeg')
    logger.info(
        "File uploaded to {} ".format(
             destination_blob_name
        )
    )
    return 'OK'