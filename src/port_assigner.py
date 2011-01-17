# This file is part of Mesh.

# Mesh is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Mesh is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Mesh.  If not, see <http://www.gnu.org/licenses/>.

import meshlib, sys, zmq

#------------------------------------------------------------------------------
# ZMQ Setup

# Context & sockets for communicator.py
zmq_context       = zmq.Context()
pull              = zmq_context.socket(zmq.PULL)
push_communicator = zmq_context.socket(zmq.PUSH)
reply             = zmq_context.socket(zmq.REP)

if __name__ == '__main__':
   config_file, communicator_pull_url, port_assigner_pull_url = sys.argv[1:]
else:
   config_file = None
meshlib.load_config(config_file)

port_assigner_port      = meshlib.get_config(None, 'port_assigner_port', '4200')
port_assigner_reply_url = "tcp://*:%s" % port_assigner_port

def verbose(msg):
   print "port_assigner:", msg

if __name__ == '__main__':
   # IPC urls (passed in at startup from master.py)
   verbose("\nport_assigner_reply_url: %s" % port_assigner_reply_url)
   for url in sys.argv[2:]:
      if not meshlib.is_socket_url(url):
         print "Error: Invalid socket url: '%s'" % url
         sys.exit(1)
   # Connect ZMQ sockets
   pull.bind(port_assigner_pull_url)
   push_communicator.connect(communicator_pull_url)
   reply.bind(port_assigner_reply_url)
   # Main Loop
   while True:
      verbose("waiting for a request")
      request = reply.recv()
      # do we like this request?
      if request.split(':')[0] != 'request_ports':
         verbose("received bad request: '%s'" % request)
         reply.send("error:invalid request format")
         continue
      verbose("received request, sending to communicator: '%s'" % request)
      push_communicator.send("port_assigner:"+request)
      verbose("waiting for message from communicator")
      msg = pull.recv()
      verbose("received message from communicator, sending back as reply: '%s'" % msg)
      reply.send("ok:"+msg)
