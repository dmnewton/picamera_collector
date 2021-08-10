import io
import importlib
import time

from flask import (Flask, Response,  render_template, send_file, request ,jsonify)

from flask_bootstrap import Bootstrap
from flask_httpauth import HTTPBasicAuth

#from werkzeug.datastructures import cache_property
from werkzeug.security import check_password_hash, generate_password_hash

from camerapi import Camera

from config import Configuration
cf = Configuration()

plugins = cf.config_data['plugins']

plugins_modules = [importlib.import_module(p) for p in plugins]


camera = Camera()

app = Flask(__name__)


app.config['SECRET_KEY'] = cf.config_data['flask']['secret']
app.config['TEMPLATES_AUTO_RELOAD'] = True


# simple security
auth = HTTPBasicAuth()
users = {k:generate_password_hash(v) for (k,v) in cf.config_data['users'].items()}
@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

# ring buffer for images

image_pos = 0
image_buffer_size = 10
image_buffer = [ None for i in range(image_buffer_size)]
last_image = 0

Bootstrap(app)

def take_picture():
    "take picture and store in ring buffer"
    global camera,image_buffer_size,image_buffer,image_pos,last_image
    t1 = round(time.time() * 1000)
    image_buffer[image_pos]=camera.take_still_picture()
    t2 = round(time.time() * 1000)
    app.logger.info('one photo elapsed %d',t2 - t1)
    frame=image_buffer[image_pos]
    last_image = image_pos
    image_pos += 1
    image_pos = image_pos % image_buffer_size
    return frame,last_image

def to_lookup(ll):
    " create drop down lookups"
    return [ {'name':x} for x in ll]

@app.route('/')
@auth.login_required
def index():
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
        jpegqualityList=jpegqualityList)

def sleep_gen(period):
    """use generator to create an accurate time intervals to send frames"""
    num = 0
    start_time = time.time()
    while True:
       sleeplength =  start_time + ( period * num ) - time.time()
       sleeplength = max(sleeplength,0)
       yield sleeplength
       num += 1


def takevideo():
    video_buffer=camera.take_video(10)
    if bsm:
        bsm.add_job((time.time(),video_buffer,'h264'))
    return jsonify({'status': 'OK'})

def takepicture(ts):
    sleeplength = sleep_gen(camera.cf['delay'])
    for i in range(camera.cf['numberimages']):
        sp = next(sleeplength)
        time.sleep(sp)
        app.logger.info('sleep  2 %f', sp)
        ts_server = round(time.time() * 1000)
        app.logger.info('time delay 2 %d',ts_server-ts)
        frame,last_image = take_picture()
        ts_pic = round(time.time() * 1000)
        app.logger.info('time delay 3 %d',ts_pic-ts_server)
        if bsm:
            bsm.add_job((time.time(),frame,'jpg'))
    return jsonify({'image index': str(last_image)})

@app.route("/api/v1/resources/takesend")
@auth.login_required
def takesend():
    ts_sensor = int(request.args.get('ts'))
    ts_server = round(time.time() * 1000)
    app.logger.info('time delay 1 %d',ts_server-ts_sensor)


    if camera.method == 'picture':
        return takepicture(ts_server)
    else:
        return takevideo()
    

@app.route('/api/v1/resources/saveconfig', methods=['GET'])
@auth.login_required
def api_saveconfig():
    camera_args = request.args.to_dict()
    #ddlMethod = request.args.get('ddlMethod')
    #ddlMode = request.args.get('ddlMode')
    #ddlISO =  request.args.get('ddlISO')
    #ddlResolution =  request.args.get('ddlResolution')
    #ddlJPEG = request.args.get('ddlJPEG')
    global camera
    camera.change_mode_if_required(camera_args)

    camera.save_camera_config(camera_args)
    return("config saved")


@app.route('/api/v1/resources/takepicture', methods=['GET'])
@auth.login_required
def api_start():
    camera_args = request.args.to_dict()
    #ddlMode = request.args.get('ddlMode')
    #ddlISO =  request.args.get('ddlISO')
    #ddlResolution =  request.args.get('ddlResolution')
    #ddlJPEG = request.args.get('ddlJPEG')
    global camera
    camera.change_mode_if_required(camera_args)
    frame,last_image = take_picture()
    return(str(last_image))

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

    plugins_instances = [p.PluginModule() for p in plugins_modules]

    bsm = None
    for p  in plugins_instances:
        p.activate(app)
        if hasattr(p, "add_job"):
            bsm = p


    app.run('::', threaded=True, debug=False,use_reloader=False)