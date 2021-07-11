import picamera
import time
import io

stream = io.BytesIO()

with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    start = time.time()
    camera.start_recording(stream,format='h264')
    camera.wait_recording(10)
    camera.stop_recording()
    stop = time.time()

print(stop-start)

temporarylocation="my_video.h264"
with open(temporarylocation,'wb') as out: 
    out.write(stream.getbuffer()) 