# Straightforward implementation of the Singleton Pattern

import yaml


class Configuration(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print('Creating the object')
            cls._instance = super(Configuration, cls).__new__(cls)
            # Put any initialization here.
            with open(r'app_settings.yaml') as file:
                cls.config_data = yaml.load(file, Loader=yaml.FullLoader)
        return cls._instance