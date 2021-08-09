# Straightforward implementation of the Singleton Pattern

import yaml
import pathlib
#import picamera_colllecter

class Configuration(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
            # Put any initialization here.
            path =pathlib.Path(__file__).parent
            with open(path / 'app_settings.yaml') as file:
                cls.config_data = yaml.load(file, Loader=yaml.FullLoader)
            with open(path / 'app_current.yaml') as file:
                cls.current_config = yaml.load(file, Loader=yaml.FullLoader)
        return cls._instance


    def save_current(cls,camera_args):
        cls.current_config['iso']=int(camera_args.get('ddlISO'))
        cls.current_config['mode']=camera_args.get('ddlMode')
        cls.current_config['resolution']=camera_args.get('ddlResolution')
        cls.current_config['jpegquality']=int(camera_args.get('ddlJPEG'))
        cls.current_config['method']=camera_args.get('ddlMethod')
        path =pathlib.Path(__file__).parent
        with open(path / 'app_current.yaml',"w") as file:
            yaml.dump(cls.current_config, file)
