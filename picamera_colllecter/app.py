import io

from flask import (Flask, Response,  render_template, send_file, request)

from flask_bootstrap import Bootstrap
from flask_httpauth import HTTPBasicAuth
from werkzeug.datastructures import cache_property
from werkzeug.security import check_password_hash, generate_password_hash

from camerapi import Camera

from to_gcs import send_picture_to_gcs

import yaml
with open(r'app_settings.yaml') as file:
    config_data = yaml.load(file, Loader=yaml.FullLoader)

import logging
logging.basicConfig(level=logging.INFO) 

camera = Camera()

app = Flask(__name__)
app.config['SECRET_KEY'] = config_data['flask']['secret']
app.config['TEMPLATES_AUTO_RELOAD'] = True

auth = HTTPBasicAuth()

users = {k:generate_password_hash(v) for (k,v) in config_data['users'].items()}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

image_pos = 0
image_buffer_size = 10
image_buffer = [ None for i in range(image_buffer_size)]
last_image = 0

Bootstrap(app)

@app.route('/')
@auth.login_required
def index():
    return render_template('index.html',modeList=[{'name':'auto'}, {'name':'sports'}],
        isoList=[{'name':'100'}, {'name':'200'},{'name':'400'},{'name':'800'},{'name':'1600'}])

@app.route('/api/v1/resources/takepicture', methods=['GET'])
@auth.login_required
def api_start():
    ddlMode = request.args.get('ddlMode')
    ddlISO = int(request.args.get('ddlISO'))
    global camera,image_buffer_size,image_buffer,image_pos,last_image
    image_buffer[image_pos]=camera.take_still_picture(ddlMode,ddlISO)
    retval = str(image_pos)
    last_image = image_pos
    image_pos += 1
    image_pos = image_pos % image_buffer_size
    return(retval)

@app.route('/api/v1/resources/send_to_gcs/<int:pid>', methods=['GET'])
@auth.login_required
def image_to_gcs(pid):
    global image_buffer
    frame=image_buffer[pid]
    rr = send_picture_to_gcs(frame)
    return(rr)

@app.route('/images/<int:pid>', methods=['GET'])
def image_frombuff(pid):
    global image_buffer
    frame=image_buffer[pid]
    return send_file(io.BytesIO(frame),
                     attachment_filename=str(pid)+'.jpg',
                     mimetype='image/jpg',
                     cache_timeout=-1)

@app.route('/api/v1/resources/lastpicture', methods=['GET'])
@auth.login_required
def api_lastpicturea():
    global last_image
    return(str(last_image))

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
@auth.login_required
def video_feed():
    global camera
    camera.start_camera()
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    #app.run('0.0.0.0',threaded=True)
    app.run('::', threaded=True, debug=False)