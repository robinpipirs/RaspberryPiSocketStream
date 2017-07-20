## Introduction to the task: 'Streaming video from raspberryPi to computer'

We're going to stream the video of the picam to our desktop computer, reason for this is to speed up processing with opencv. If you try processing with opencv on the raspberryPi you will see a decrease in framerate. Low framerate makes object tracking and people counting hard.

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
