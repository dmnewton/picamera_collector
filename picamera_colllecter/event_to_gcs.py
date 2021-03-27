from gpiozero import Button
from time import sleep
from signal import pause
import picamera
import time
import yaml
import io
import os
from fractions import Fraction
from google.cloud import storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/gdiaunicorn-a4464e10106e.json"

storage_client = storage.Client()
bucket = storage_client.bucket("roof_images")


button = Button(17)

camera = picamera.PiCamera()

def print_camera_settings():
    print("iso",camera.ISO)
    print("awb_gains",camera.awb_gains)
    print("shutter_speed microseconds",camera.shutter_speed)

def configure_camera_std():
    camera.resolution=(1280, 720)
    camera.framerate=30
    camera.iso = 100
    sleep(2)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    camera.iso = 200
    camera.shutter_speed = 10000


def configure_camera():
    with open(r'app_settings.yaml') as file:
        camera_settings = yaml.load(file, Loader=yaml.FullLoader)['camera-settings']

    for cmd in camera_settings: 
        print(cmd)
        try:
            exec(cmd,globals(),locals())
        except:
            pass


def take_picture():
    stream = io.BytesIO()
    print_camera_settings()
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

configure_camera()

button.when_released = release_action

pause()

