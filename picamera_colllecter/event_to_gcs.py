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

camera = picamera.PiCamera()

def print_camera_settings():
    print("iso",camera.ISO)
    print("awb_gains",camera.awb_gains)
    print("shutter_speed microseconds",camera.shutter_speed)

def configure_camera_std():
    camera.resolution=(1332, 990)
    camera.iso = 800
    camera.meter_mode = 'spot'
    sleep(2)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    

def configure_camera_sport():
    print("configuring sports")
    camera.resolution=(1332, 990)
    camera.iso = 800
    camera.meter_mode = 'spot'
    camera.exposure_mode = 'sports'
    sleep(2)
    print("configured sports")

def exposure_speed():
    return (camera.exposure_speed,camera.brightness)

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

def prepare_action():
    global state
    print("prepared")
    state = 1
    time.sleep(1)

def release_action():
    global state
    print('release')
    if state == 2:
        start=time.time()
        print('release')
        image = take_picture()
        send_picture_to_gcs(image)
        end=time.time()
        print("process time", end-start)
        state = 0
        time.sleep(1)

if __name__ == '__main__':
    configure_camera_sport()

    state = 0

    button = Button(17)

    button.when_activated = prepare_action
    button.when_deactivated = release_action

    pause()