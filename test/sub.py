import zmq

context = zmq.Context()
sub_socket = context.socket(zmq.SUB)
sub_socket.connect("ipc://testpublisher.ipc")

sub_socket.setsockopt(zmq.SUBSCRIBE, "")

count = 0
while count < 10:
   count += 1
   my_message = sub_socket.recv()
   print "message from publisher is", my_message
