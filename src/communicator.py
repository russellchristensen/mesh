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
zmq_context         = zmq.Context()
pull                = zmq_context.socket(zmq.PULL)
push_master         = zmq_context.socket(zmq.PUSH)
push_port_requestor = zmq_context.socket(zmq.PUSH)
push_port_assigner  = zmq_context.socket(zmq.PUSH)
push_nodes          = {}

if __name__ == '__main__':
   # IPC urls (passed in at startup from master.py)
   config_file, master_pull_url, communicator_pull_url, port_assigner_pull_url, port_requestor_pull_url = sys.argv[1:]
else:
   config_file = None
meshlib.load_config(config_file)

# Config values
inbound_pull_proxy_port = meshlib.get_config(None, 'inbound_pull_proxy_port', '4201')
next_push_port          = meshlib.get_config(None, 'next_push_port',          '4205')

def verbose(msg):
   print "communicator:", msg

if __name__ == '__main__':
   verbose("""
next_push_port:          %s
""" %  next_push_port)

   for url in sys.argv[2:]:
      if not meshlib.is_socket_url(url):
         print "Error: Invalid socket url: '%s'" % url
         sys.exit(1)
   # Connect ZMQ sockets
   pull.bind(communicator_pull_url)
   push_master.connect(master_pull_url)
   push_port_requestor.connect(port_requestor_pull_url)
   push_port_assigner.connect(port_assigner_pull_url)
   # Main Loop
   while True:
      msg = pull.recv()
      msg_parts = msg.split(':')
      if msg_parts[0] == 'info':
         verbose("Received info message: '%s'" % msg)
      elif msg_parts[0] == 'connect_node':
         verbose("Passing the connect_node message up to port_requestor: '%s'" % msg)
         push_port_requestor.send(msg)
      elif msg_parts[0] == 'port_requestor':
         verbose("Received message from port_requestor: %s" % msg)
         
      elif msg_parts[0] == 'port_assigner':
         verbose("Received request through port_assigner: %s" % msg)
         # set up inbound push connection
         push_port = next_push_port
         next_push_port = str(int(next_push_port) + 1)
         # tell port_assigner which ports to reply with
         push_port_assigner.send('pull_proxy_port:%s:push_port:%s' % (inbound_pull_proxy_port, push_port))
