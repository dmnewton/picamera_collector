import time
import picamera
import io

with picamera.PiCamera() as camera:

    time.sleep(2)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g

    print("start")
    camera.framerate = 1


    frame_no = 10
    outputs = [io.BytesIO() for i in range(frame_no)]
    start = time.time()
    camera.capture_sequence(outputs, 'jpeg', use_video_port=True)
    stop = time.time()

    for i in range(frame_no):
        # Write the stuff
        with open('image%02d.jpg' % i, "wb") as f:
            f.write(outputs[i].getbuffer())



    print(stop-start)