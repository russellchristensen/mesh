import zmq
import time

context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind("ipc://testpublisher.ipc")

for i in range(20):
   pub_socket.send(str(i))
   time.sleep(1)
   
