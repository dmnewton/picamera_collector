import socket
import os

try:
  s=socket.getaddrinfo('www.google.com', 80)
except:
  os.environ["http_proxy"] = 'http://internet.ford.com:83'
  os.environ["https_proxy"] = 'http://internet.ford.com:83'
  os.environ["no_proxy"] = 'localhost,127.0.0.1,.ford.com'