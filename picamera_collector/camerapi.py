import io
from async_timeout import timeout
import picamera
import time
import eventlet

import logging
logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT,level=logging.INFO)

from picamera_collector import config

class Camera(object):
    """ manage all communication with PI camaera.
    eventlet is use as concurrent processing framework 
    while it works nicely with flask"""

    def __init__(self):
        self.thread = None
        self.last_access = 0
        self.frame = None

        self.qq = eventlet.Semaphore()

        self.break_stop = None

        self.camera = picamera.PiCamera()
        self.state  = -1
        self.cf = config.Configuration().current_config
        self.iso = self.cf['iso']
        self.exposure_mode = self.cf['exposure_mode']
        self.resolution = self.cf['resolution']
        self.jpegquality = self.cf['jpegquality']
        self.method = self.cf['method']
        self.shutter_speed = self.cf['shutter_speed']
        if self.cf['vflip']:
            logger.info("vertical flip enabled")
        if self.cf['hflip']:
            logger.info("horizontal flip enabled")
        self.set_camera()
    
    def set_camera(self):
        """ initialise camera setting """
        self.camera.resolution=self.to_res(self.resolution)
        self.camera.iso = self.iso
        self.camera.meter_mode = self.cf['meter_mode']
        self.camera.exposure_mode = self.exposure_mode
        self.camera.vflip = self.cf['vflip']
        self.camera.hflip = self.cf['hflip']
        self.camera.shutter_speed = int(self.shutter_speed)*1000
        self.camera.framerate = int(self.cf.get('framerate'))
    
    @staticmethod
    def to_res(s):
        return [ int(x) for x in s.split('x')]

    def start_camera(self):
        """ start background thread to stream video as mjpeg """
        if self.state < 1:
            self.camera.resolution = self.to_res(self.resolution)
            if self.camera.resolution[0]>3000:
                self.camera.framerate = 5
            else:    
                self.camera.framerate = 10
            self.last_access = time.time()
            self.thread = eventlet.spawn(self._thread)
            eventlet.sleep(0)
            self.state = 1
    
    def frames(self):
        """ get next frame and yield """
        stream = io.BytesIO()
        for _ in self.camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
            # return current frame
            stream.seek(0)
            yield stream.read()
            # reset stream for next frame
            stream.seek(0)
            stream.truncate()
    
    def _thread(self):
        """Camera background thread."""
        logger.info('Starting camera thread.')
        frames_iterator = self.frames()
        self.break_stop = False
        for frame in frames_iterator:
            self.frame = frame
            # if client wants a frame release one
            if self.qq.balance<1:
                self.qq.release()

            eventlet.sleep(0)

            if self.break_stop:
                logger.info('Stopping due to break')
                frames_iterator.close()
                break

            # if there hasn't been any request for frames in
            # the last 5 seconds then stop the thread
            if time.time() - self.last_access > 5:
                frames_iterator.close()
                logger.info('Stopping camera thread due to 5 seconds of inactivity.')
                break

        self.thread = None

    def get_frame(self):
        """Return the current camera frame."""

        # remember when frame was sent for timeout
        self.last_access = time.time()

        # wait for a signal from the camera thread
        # send old image if no signal

        self.qq.acquire(blocking=True,timeout=1)

        return self.frame

    def save_camera_config(self,camera_args):
        config.Configuration().save_current(camera_args)

    def change_mode_if_required(self,camera_args):
        
        no_change = True
        if self.state == 1:
            logger.info("stop_recording")
            self.break_stop = True
            self.state = 0
            no_change = False

        if camera_args != None:
            if camera_args.get('ddlMode') != None:
                ddlISO=int(camera_args.get('ddlISO'))
                if ((self.exposure_mode != camera_args.get('ddlMode')) or 
                    (self.iso != ddlISO) or
                    (self.resolution != camera_args.get('ddlResolution')) or
                    (self.method != camera_args.get('ddlMethod')) or
                 (self.shutter_speed != camera_args.get('ddlShutterSpeed'))
                    ) :
                        self.exposure_mode = camera_args.get('ddlMode')
                        self.iso = ddlISO
                        self.resolution = camera_args.get('ddlResolution')
                        self.method = camera_args.get('ddlMethod')
                        self.shutter_speed = camera_args.get('ddlShutterSpeed')
                        no_change = False
                if self.jpegquality != int(camera_args.get('ddlJPEG')):
                    self.jpegquality = int(camera_args.get('ddlJPEG'))
            if self.state == -1:
                self.state = 0
                no_change = False

        if no_change:
            return
  
        self.set_camera()
        eventlet.sleep(2)   

    def take_still_picture(self):
        stream = io.BytesIO()
        start = time.time()
        self.camera.capture(stream, format='jpeg',quality=self.jpegquality,use_video_port=False)
        end = time.time()
        info = self.camera_info()
        elapsed = end-start
        info['elapsed'] = elapsed
        return (stream.getvalue(),info)

    def take_picture_series(self):

        frames = int(self.cf.get('numberimages'))
        outputs = [io.BytesIO() for i in range(frames)]

        start = time.time()
        self.camera.capture_sequence(outputs, 'jpeg', use_video_port=True, quality=self.jpegquality)
        end = time.time()
        
        info = self.camera_info()
        elapsed = end-start
        info['elapsed'] = elapsed
        fps =  (frames / (end - start))
        info['fps'] = fps
        res = [x.getvalue() for x in outputs]
        return (res,info)

    def take_video(self,duration):
        stream = io.BytesIO()
        self.camera.start_recording(stream,format='h264')
        self.camera.wait_recording(duration)
        self.camera.stop_recording()
        return stream.getvalue()

    def camera_info(self):
        """copy current camera settings to dict"""
        o = [float(a) for a in self.camera.awb_gains]
        info = {
            "iso":self.camera.iso,
            "exposure":self.camera.exposure_speed,
            "shutterspeed":self.camera.shutter_speed,
            "analog_gain":self.camera.analog_gain,
            "digital_gain":self.camera.digital_gain,
            "awb_gains ":o
        }
        return info

    def gen(self):
        """ package image in multipart/x-mixed-replace  """
        self.start_camera()
        while True:
            frame = self.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

if __name__ == '__main__':
    camera = Camera()

    time.sleep(2)

    camera.start_camera()

    cnt = 0
    start =time.time()
    for i in range(20):
        frame = camera.get_frame()
        logger.info("inf %s", camera.camera_info())
        with open('frame.jpg', 'wb') as file_obj:
                 file_obj.write(frame)
        cnt+=1
        if cnt==20:
            break
    end = time.time()
    logger.info("elapsed %s",end-start)
    camera.break_stop = True