import io
import picamera
import threading
import time

import logging
logger = logging.getLogger(__name__)

from picamera_collector import config



class Frame:
    def __init__(self):
        self.frame = None

class SplitFrames(object):
    def __init__(self,frame,reset_message):
        self.output = None
        self.frame = frame
        self.reset_message = reset_message

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # Start of new frame; close the old one (if any) and
            # open a new output
            if self.output:
                self.frame.frame = self.output.getvalue()
                with self.reset_message:
                        self.reset_message.notifyAll()
            # reset stream for next frame
            self.output =io.BytesIO()
        self.output.write(buf)

class Camera(object):

    def __init__(self):
        self.frame =  Frame()
        self.reset_message = threading.Condition()
        self.camera = picamera.PiCamera()
        self.state  = -1
        self.cf = config.Configuration().current_config
        self.iso = self.cf['iso']
        self.mode = self.cf['mode']
        self.resolution = self.cf['resolution']
        self.jpegquality = self.cf['jpegquality']
        self.method = self.cf['method']
        if self.cf['vflip']:
            logger.info("vertical flip enabled")
        if self.cf['hflip']:
            logger.info("horizontal flip enabled")
        self.set_camera()
    
    def set_camera(self):
        self.camera.resolution=self.to_res(self.resolution)
        self.camera.iso = self.iso
        self.camera.meter_mode = 'spot'
        self.camera.exposure_mode = self.mode
        self.camera.vflip = self.cf['vflip']
        self.camera.hflip = self.cf['hflip']
    
    @staticmethod
    def to_res(s):
        return [ int(x) for x in s.split('x')]

    def start_camera(self):
        if self.state < 1:
            self.camera.resolution = self.to_res(self.resolution)
            if self.camera.resolution[0]>3000:
                self.camera.framerate = 15
            else:    
                self.camera.framerate = 30
            output = SplitFrames(self.frame,self.reset_message)
            self.camera.start_recording(output, format='mjpeg',quality=self.jpegquality)
            self.state = 1

    def save_camera_config(self,camera_args):
        config.Configuration().save_current(camera_args)

    def change_mode_if_required(self,camera_args):

        no_change = True
        if self.state == 1:
            self.camera.stop_recording()
            self.state = 0
            no_change = False
        
        if camera_args.get('ddlMode') != None:
            ddlISO=int(camera_args.get('ddlISO'))
            if ((self.mode != camera_args.get('ddlMode')) or 
                (self.iso != ddlISO) or
                (self.resolution != camera_args.get('ddlResolution')) or
                (self.method != camera_args.get('ddlMethod'))
                ) :
                    self.mode = camera_args.get('ddlMode')
                    self.iso = ddlISO
                    self.resolution = camera_args.get('ddlResolution')
                    self.method = camera_args.get('ddlMethod')
                    no_change = False
            if self.jpegquality != int(camera_args.get('ddlJPEG')):
                self.jpegquality = int(camera_args.get('ddlJPEG'))
        if self.state == -1:
            self.state = 0
            no_change = False

        if no_change:
            return
    
        self.set_camera()
        
        time.sleep(2)
    
    def get_frame(self):
        with self.reset_message:
            self.reset_message.wait()
        return self.frame.frame
     
    def take_still_picture(self):
        stream = io.BytesIO()
        self.camera.capture(stream, format='jpeg',quality=self.jpegquality)
        logger.info("shutter speed %d", self.camera.exposure_speed)
        return stream.getvalue()

    def take_picture_series(self):
        self.camera.framerate = int(self.cf.get('framerate'))
        frames = int(self.cf.get('numberimages'))
        outputs = [io.BytesIO() for i in range(frames)]
        # fix camera exposure
        self.camera.shutter_speed = self.camera.exposure_speed
        ex_mode = self.camera.exposure_mode 
        self.camera.exposure_mode = 'off'
        g = self.camera.awb_gains
        awb = self.camera.awb_mode 
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = g
        start = time.time()
        self.camera.capture_sequence(outputs, 'jpeg', use_video_port=True)
        finish = time.time()
        # switch off
        self.camera.exposure_mode = ex_mode
        self.camera.awb_mode = awb
        logger.info('Captured at %.2f fps', (frames / (finish - start)))
        logger.info("shutter speed %d", self.camera.exposure_speed)
        res = [x.getvalue()for x in outputs]
        return res

    def take_video(self,duration):
        stream = io.BytesIO()
        #self.camera.resolution = (640, 480)
        self.camera.start_recording(stream,format='h264')
        self.camera.wait_recording(duration)
        self.camera.stop_recording()
        return stream.getvalue()
    
    def stop_camera(self):
        self.camera.stop_recording()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

if __name__ == '__main__':
    camera = Camera()
    camera.start_camera()
    cnt = 0
    start =time.time()
    for frame in gen(camera):
        print(len(frame))
        cnt+=1
        if cnt==120:
            break
    end = time.time()
    print(end-start)
    camera.stop_camera()