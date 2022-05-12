import cv2
import numpy as np
import urllib.request

url = 'http://picamera02.local:5000/video_feed'

# If you would like to request Authorization header for Digest Authentication,
# replace HTTPBasicAuthHandler object to HTTPDigestAuthHandler
passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None, url, 'admin', 'admin')
authhandler = urllib.request.HTTPBasicAuthHandler(passman)
opener = urllib.request.build_opener(authhandler)
urllib.request.install_opener(opener)

stream=urllib.request.urlopen(url)

font = cv2.FONT_HERSHEY_SIMPLEX

bytes=b''
while True:
    bytes+=stream.read(1024)
    a = bytes.find(b'\xff\xd8') # JPEG start
    b = bytes.find(b'\xff\xd9') # JPEG end
    if a!=-1 and b!=-1:
        jpg = bytes[a:b+2] # actual image
        bytes= bytes[b+2:] # other informations

        # decode to colored image ( another option is cv2.IMREAD_GRAYSCALE )
        img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR) 
        brightness = '%.3f' % np.average(img)

        cv2.putText(img, brightness, (10,300), font, 3, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow('Window name',img) # display image while receiving data
        if cv2.waitKey(1) ==27: # if user hit esc
            exit(0) # exit program