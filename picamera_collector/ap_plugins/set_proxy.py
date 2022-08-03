import socket
import os

import logging
logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT,level=logging.INFO)

try:
  s=socket.getaddrinfo('www.google.com', 80)
except:
  logger.info("setting proxy")
  os.environ["http_proxy"] = 'http://internet.ford.com:83'
  os.environ["https_proxy"] = 'http://internet.ford.com:83'
  os.environ["no_proxy"] = 'localhost,127.0.0.1,.ford.com'