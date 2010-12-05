import zmq

context = zmq.Context()
rep_socket = context.socket(zmq.REP)
rep_socket.bind("ipc://testreqrep.ipc")

incoming_message = rep_socket.recv()
print "Received:", incoming_message
reply = "Yes, I'm here"
rep_socket.send(reply)
print "Sent:", reply
