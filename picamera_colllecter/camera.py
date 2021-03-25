from time import time
from pathlib import Path

class Camera(object):
    def __init__(self):
        p = Path('images')
        files = p.glob('*.jpg')
        self.frames = [open(f, 'rb').read() for f in files]

    def get_frame(self):
        return self.frames[int(time()) % 3]

if __name__ == '__main__':
    camera=Camera()