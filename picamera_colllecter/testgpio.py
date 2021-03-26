from gpiozero import Button
from time import sleep
from signal import pause
import picamera
import time

import io
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/gdiaunicorn-a4464e10106e.json"

from google.cloud import storage

button = Button(17)

camera = picamera.PiCamera()

storage_client = storage.Client()
bucket = storage_client.bucket("roof_images")

def take_picture():
    stream = io.BytesIO()
    camera.resolution = (800, 600)
    camera.capture(stream, format='jpeg')
    return stream.getvalue()

def send_picture_to_gcs(image):
    epoch_time = int(time.time())
    destination_blob_name = "test/image-{}.jpg".format(epoch_time)

    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(image,content_type='image/jpeg')
    print(
        "File uploaded to {}.".format(
             destination_blob_name
        )
    )

def release_action():
    start=time.time()
    print('release')
    image = take_picture()
    send_picture_to_gcs(image)
    end=time.time()
    print("process time", end-start)

button.when_released = release_action

pause()

