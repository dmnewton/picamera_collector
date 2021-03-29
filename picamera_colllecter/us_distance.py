from gpiozero import DigitalInputDevice,DigitalOutputDevice
import time
from statemachine import StateMachine, State

import asyncio

import event_to_gcs as ee

loop = None

class ImageCaptueMachine(StateMachine):
    nocar = State('nocar', initial=True)
    near = State('near')
    photo = State('photo')
    shortwait = State('wait')

    car_seen = nocar.to(near)
    right_distance = near.to(photo)
    photo_taken = photo.to(shortwait)
    startagain= shortwait.to(nocar)

    def on_car_seen(self):
        print('on_car_seen')

    def on_right_distance(self):
        print('on_right_distance.')


    def on_photo_taken(self):
        print('on_photo_taken.')
    
    def on_startagain(self):
        print('on_startagain.')

icm = ImageCaptueMachine()

start_val = None

def calc_distance(start,stop):
    elapsed = stop-start

    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s)
    distancet = elapsed * 34300

    # That was the distance there and back so halve the value
    distance = distancet / 2

    if distance < 300:
        print  ("Distance :", distance, " cm ")
        return distance
    return None

def start():
    global start_val
    start_val = time.time()

@asyncio.coroutine
async def photo_loop():
    ee.release_action()
    icm.photo_taken()
    await asyncio.sleep(10)
    icm.startagain()

def take_photo():
    asyncio.Task(photo_loop())

def stop():
    stop_val = time.time()
    global start_val
    if stop_val:
        distance = calc_distance(start_val, stop_val)
        if distance is not None:
            if (distance < 22) and (icm.current_state.identifier == 'nocar'):
                icm.car_seen()
            if (distance >= 22) and (icm.current_state.identifier == 'near'):
                icm.right_distance()
                loop.call_soon_threadsafe(take_photo)
                #asyncio.run(take_photo())
        start_val = None

a = DigitalInputDevice(24)
a.when_activated = start
a.when_deactivated = stop
trigger = DigitalOutputDevice(23)


async def myWork():

    while True:
    # Send 10us pulse to trigger
        print('exposure speed',ee.exposure_speed())
        start_val = None
        trigger.on()
        time.sleep(0.00001)
        trigger.off()
        await asyncio.sleep(0.1)

if __name__ == '__main__':
    #ee.configure_camera_sport()
    ee.configure_camera_std()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(myWork())
    finally:
        loop.close()
