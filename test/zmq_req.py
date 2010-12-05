import zmq

context = zmq.Context()
req_socket = context.socket(zmq.REQ)
req_socket.connect("ipc://testreqrep.ipc")

message = "Are you there?"
req_socket.send(message)
print "Sent:", message
reply = req_socket.recv()
print "Received:", reply
