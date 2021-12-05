import io
import importlib
import time

from flask import (Flask, Response,  render_template, send_file, request ,jsonify)

from flask_bootstrap import Bootstrap
from flask_httpauth import HTTPBasicAuth

from flask_socketio import SocketIO

from werkzeug.security import check_password_hash, generate_password_hash

import logging
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT,level=logging.INFO)

#from werkzeug.serving import WSGIRequestHandler

from picamera_collector import camerapi
from picamera_collector import ring_buffer


from picamera_collector import config
cf = config.Configuration()

plugins = cf.config_data['plugins']

plugins_modules = [importlib.import_module(p) for p in plugins]

camera = camerapi.Camera()

app = Flask(__name__)

app.config['SECRET_KEY'] = cf.config_data['flask']['secret']
app.config['TEMPLATES_AUTO_RELOAD'] = True

sio = SocketIO(app)

# simple security
auth = HTTPBasicAuth()
users = {k:generate_password_hash(v) for (k,v) in cf.config_data['users'].items()}
@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

# ring buffer for images

rb =ring_buffer.RingBuffer(20)

Bootstrap(app)

def take_picture():
    "take picture and store in ring buffer"
    global camera,rb
    t1 = round(time.time() * 1000)
    image=camera.take_still_picture()
    t2 = round(time.time() * 1000)
    app.logger.info('one photo elapsed %d',t2 - t1)
    return image

def to_lookup(ll):
    " create drop down lookups"
    return [ {'name':x} for x in ll]

@app.route('/')
@auth.login_required
def index():
    global camera
    methodList=to_lookup(cf.config_data['methodList'])
    modeList=to_lookup(cf.config_data['modeList'])
    isoList=to_lookup(cf.config_data['isoList'])
    resolutionList=to_lookup(cf.config_data['resolution'])
    jpegqualityList=to_lookup(cf.config_data['jpegquality'])
    return render_template('index.html',
        methodList=methodList,
        modeList=modeList,
        isoList=isoList,
        resolutionList=resolutionList,
        jpegqualityList=jpegqualityList,
        cMethod=camera.method,
        cResolution=camera.resolution,
        cMode=camera.exposure_mode,
        cISO=camera.iso,
        cJPEG=camera.jpegquality,
        cShutterSpeed=camera.shutter_speed
        )


def takevideo():
    video_buffer=camera.take_video(10)
    if bsm:
        bsm.add_job((time.time(),0,video_buffer,'h264'))
    return 0

def takepicture(single_picture):
    global camera,rb
    epoch_time = int(time.time()*1000)
    if (camera.cf['numberimages']==1) or single_picture:
        app.logger.info('taking sngle pictue')
        frame = take_picture()
        rb.add_to_buffer(frame)
        if bsm:
            bsm.add_job((epoch_time,0,frame,'jpg'))
        return rb.get_state()
    else:
        app.logger.info('taking series of pictures')
        images = camera.take_picture_series()
        for image in images:
            last_image = rb.add_to_buffer(image)
        if bsm:
           [bsm.add_job((epoch_time,x,images[x],'jpg')) for x in range(len(images))]
        return rb.get_state()

@app.route("/api/v1/resources/takesend")
#@auth.login_required
def takesend():
    global camera
    ts_sensor = int(request.args.get('ts'))
    ts_server = round(time.time() * 1000)
    app.logger.info('time delay 1 %d',ts_server - ts_sensor)
    app.logger.info('camera method %s',camera.method)
    if camera.method == 'picture':
        last =  takepicture(single_picture=False)
    else:
        last = takevideo()
    return jsonify({'image index': str(last)})

@sio.event
def takephoto(ts_sensor):
    global camera
    ts_server = round(time.time() * 1000)
    app.logger.info('time delay 1 %d',ts_server - ts_sensor)
    app.logger.info('camera method %s',camera.method)
    if camera.method == 'picture':
        last =  takepicture(single_picture=False)
    else:
        last = takevideo()
    

@app.route('/api/v1/resources/saveconfig', methods=['GET'])
@auth.login_required
def api_saveconfig():
    global camera
    camera_args = request.args.to_dict()
    camera.change_mode_if_required(camera_args)
    camera.save_camera_config(camera_args)
    return("config saved")


@app.route('/api/v1/resources/takepicture', methods=['GET'])
@auth.login_required
def api_start():
    app.logger.info('takepicture')
    global camera
    camera_args = request.args.to_dict()
    camera.change_mode_if_required(camera_args)
    if camera.method == 'picture':
        last=takepicture(single_picture=True)
    else:
        last=takevideo()
    return jsonify(last)

    #frame,last_image = take_picture()
    #return(str(last_image))

@app.route('/images/<int:pid>', methods=['GET'])
def image_frombuff(pid):
    global rb
    frame=rb.get(pid)
    return send_file(io.BytesIO(frame),
                     attachment_filename=str(pid)+'.jpg',
                     mimetype='image/jpg',
                     cache_timeout=-1)

@app.route('/api/v1/resources/lastpicture', methods=['GET'])
@auth.login_required
def api_lastpicturea():
    global rb
    return jsonify(rb.get_state())


@app.route('/video_feed')
@auth.login_required
def video_feed():
    global camera
    app.logger.info('video_feed')
    return Response(camerapi.Camera.gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@sio.event
def connect(sid):
    app.logger.info('connect %s', sid)

@sio.event
def disconnect():
    app.logger.info('disconnect ') 

if __name__ == '__main__':

    plugins_instances = [p.PluginModule() for p in plugins_modules]

    bsm = None
    for p  in plugins_instances:
        p.activate(app)
        if hasattr(p, "add_job"):
            bsm = p

    #WSGIRequestHandler.protocol_version = "HTTP/1.1"
    
    #app.run('0.0.0.0', threaded=True, debug=False, use_reloader=False)
    sio.run(app, host='0.0.0.0', port=5000,  debug=False, use_reloader=False)
    