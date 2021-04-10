import io
import importlib

from flask import (Flask, Response,  render_template, send_file, request)

from flask_bootstrap import Bootstrap
from flask_httpauth import HTTPBasicAuth
from werkzeug.datastructures import cache_property
from werkzeug.security import check_password_hash, generate_password_hash

from camerapi import Camera

from config import Configuration
cf = Configuration()

event_module = cf.config_data['plugins']['event']
store_module = cf.config_data['plugins']['store']

ev = importlib.import_module(event_module)
sm = importlib.import_module(store_module)

import logging
logging.basicConfig(level=logging.INFO) 

camera = Camera()

app = Flask(__name__)
app.config['SECRET_KEY'] = cf.config_data['flask']['secret']
app.config['TEMPLATES_AUTO_RELOAD'] = True

auth = HTTPBasicAuth()

users = {k:generate_password_hash(v) for (k,v) in cf.config_data['users'].items()}

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

def to_lookup(ll):
    return [ {'name':x} for x in ll]

@app.route('/')
@auth.login_required
def index():
    modeList=to_lookup(cf.config_data['modeList'])
    isoList=to_lookup(cf.config_data['isoList'])
    resolutionList=to_lookup(cf.config_data['resolution'])
    jpegqualityList=to_lookup(cf.config_data['jpegquality'])
    return render_template('index.html',
        modeList=modeList,
        isoList=isoList,
        resolutionList=resolutionList,
        jpegqualityList=jpegqualityList)

@app.route('/api/v1/resources/takepicture', methods=['GET'])
@auth.login_required
def api_start():
    ddlMode = request.args.get('ddlMode')
    ddlISO =  request.args.get('ddlISO')
    ddlResolution =  request.args.get('ddlResolution')
    ddlJPEG = request.args.get('ddlJPEG')
    global camera,image_buffer_size,image_buffer,image_pos,last_image
    camera.change_mode_if_required(ddlMode,ddlISO,ddlResolution,ddlJPEG)
    image_buffer[image_pos]=camera.take_still_picture()
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
    rr = sm.store_action(frame)
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
    bb =ev.TriggerEvent(cf)
    app.run('::', threaded=True, debug=False)