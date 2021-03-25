import os
import picamera
from flask import Flask, render_template, redirect, url_for, Response ,send_file
from flask_bootstrap import Bootstrap
import time
import io

pi_camera = picamera.PiCamera()

from camera import Camera

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['TEMPLATES_AUTO_RELOAD'] = True

image_pos = 0
image_buffer_size = 10
image_buffer = [ None for i in range(image_buffer_size)]

Bootstrap(app)

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1/resources/start', methods=['GET'])
def api_start():
    stream = io.BytesIO()
    pi_camera.capture(stream, format='jpeg')
    global image_buffer_size,image_buffer,image_pos
    image_buffer[image_pos]=stream.getvalue()
    retval = str(image_pos)
    image_pos += 1
    image_pos = image_pos % image_buffer_size
    return(retval)

@app.route('/images/<int:pid>', methods=['GET'])
def image_frombuff(pid):
    global image_buffer
    frame=image_buffer[pid]
    return send_file(io.BytesIO(frame),
                     attachment_filename=str(pid)+'.jpg',
                     mimetype='image/jpg')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run('0.0.0.0')