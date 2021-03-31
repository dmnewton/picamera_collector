import os
import time
from google.cloud import storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/gdiaunicorn-a4464e10106e.json"

storage_client = storage.Client()
bucket = storage_client.bucket("roof_images")

def send_picture_to_gcs(image):
    epoch_time = int(time.time())
    destination_blob_name = "test/image-{}.jpg".format(epoch_time)

    blob = bucket.blob(destination_blob_name)
    rr = blob.upload_from_string(image,content_type='image/jpeg')
    print(
        "File uploaded to {} return code {}.".format(
             destination_blob_name, rr
        )
    )
    return 'OK'