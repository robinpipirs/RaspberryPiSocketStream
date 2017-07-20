## Introduction to the task: 'Streaming video from raspberryPi to computer'

We're going to stream the video of the picam to our desktop computer, reason for this is to speed up processing with opencv. If you try processing with opencv on the raspberryPi you will see a decrease in framerate. Low framerate makes object tracking and people counting hard.  
Server and client side code was taken from a project written by `zhengwang` which involves selfdriving cars.

## Basic setup

Make sure ports are open and that you have the libraries used.
On my desktop computer im running python through an Anaconda2 install, and also Opencv 3 downloaded from opencv.


## Client setup (raspberryPi)

The code that will be running on the raspberryPi:

```python
import io
import socket
import struct
import time
import picamera


# create socket and bind host
host = 'the ip of the host desktop computer'
port = '8887'
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))
connection = client_socket.makefile('wb')

try:
    with picamera.PiCamera() as camera:
        camera.resolution = (320, 240)      # pi camera resolution
        camera.framerate = 10               # 10 frames/sec
        time.sleep(2)                       # give 2 secs for camera to initilize
        start = time.time()
        stream = io.BytesIO()
        
        # send jpeg format video stream
        for foo in camera.capture_continuous(stream, 'jpeg', use_video_port = True):
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            stream.seek(0)
            connection.write(stream.read())
            if time.time() - start > 600:
                break
            stream.seek(0)
            stream.truncate()
    connection.write(struct.pack('<L', 0))
finally:
    connection.close()
    client_socket.close()
```

## Server setup (desktop computer)

The code that will be running on the desktop computer:


```python
import threading
import SocketServer
import cv2
import numpy as np

class VideoStreamHandler(SocketServer.StreamRequestHandler):

    def handle(self):

        stream_bytes = ' '

        # stream video frames one by one
        try:

            print ("thread started")

            while True:
                stream_bytes += self.rfile.read(1024)
                first = stream_bytes.find('\xff\xd8')
                last = stream_bytes.find('\xff\xd9')
                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last+2]
                    stream_bytes = stream_bytes[last+2:]
                    gray = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

                    # lower half of the image
                    half_gray = gray[120:240, :]

                    cv2.imshow('image', image)
                    #cv2.imshow('mlp_image', half_gray)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

            cv2.destroyAllWindows()

        finally:
            print "Connection closed on thread 1"

class ThreadServer(object):

    def server_thread(host, port):
        server = SocketServer.TCPServer((host, port), VideoStreamHandler)
        server.serve_forever()

    print ("starting")
    video_thread = threading.Thread(target=server_thread('', 8887))
    video_thread.start()

if __name__ == '__main__':
    ThreadServer()
```
