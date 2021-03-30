from setuptools import setup, find_packages

import os
thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

setup(name='picamera_colllecter',
      version='0.0.1',
      description='AI data Collection using PI Camera',
      url='https://github.com/dmnewton/picamera_colllecter.git',
      author='david newton',
      author_email='dmndmn@hotmail.de',
      license='mit',
      install_requires=install_requires,
      packages=find_packages(),
      zip_safe=False)
