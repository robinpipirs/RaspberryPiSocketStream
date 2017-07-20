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
