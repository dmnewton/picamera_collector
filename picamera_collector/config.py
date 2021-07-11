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
        return cls._instance