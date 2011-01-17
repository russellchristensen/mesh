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
identifier              = meshlib.get_identifier()

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
      verbose("\nPush Nodes:" + "\n".join(sorted(push_nodes)))
      msg = pull.recv()
      verbose("processing message: '%s'" % msg)
      msg_parts = msg.split(':')
      if msg_parts[0] == 'master':
         verbose("Processing message from master: '%s'" % msg)
         if msg_parts[1] == 'connect_node':
            verbose("Passing the connect_node message up to port_requestor: '%s'" % msg)
            push_port_requestor.send(':'.join(msg_parts[1:]))
         elif msg_parts[1] == 'send_node':
            foreign_identifier, message_to_send = msg_parts[2:]
            if push_nodes.has_key(foreign_identifier):
               verbose("Sending node '%s' the message: '%s'" % (foreign_identifier, message_to_send))
               push_nodes[foreign_identifier].send(message_to_send)
            else:
               verbose("Not connected to node '%s', can't send it: '%s'" % (foreign_identifier, message_to_send))
      # ...from port_requestor
      elif msg_parts[0] == 'port_requestor':
         verbose("Received message from port_requestor: %s" % msg)
         if msg_parts[1] == 'got_node_ports':
            ip, port, foreign_identifier, pull_port, push_port = msg_parts[2:]
            # First create the push socket, since that's easy
            push_nodes[foreign_identifier] = zmq_context.socket(zmq.PUSH)
            push_nodes[foreign_identifier].connect('tcp://%s:%s' % (ip, pull_port))
            # Now ask master to set up the outbound pull socket process
            push_master.send('communicator:pull_proxy:%s:%s' % (ip, push_port))
         else:
            verbose("Invalid message from port_requestor: '%s'" % msg)
      # ...from port_assigner
      elif msg_parts[0] == 'port_assigner':
         verbose("Received request through port_assigner: %s" % msg)
         # request for ports
         if msg_parts[1] == 'request_ports':
            foreign_identifier = msg_parts[2]
            # Node already connected?
            if push_nodes.has_key(foreign_identifier):
               push_port_assigner.send(meshlib.error % {'message':'already connected'})
               continue
            # Setup inbound push connection
            push_port = next_push_port
            next_push_port = str(int(next_push_port) + 1)
            push_nodes[foreign_identifier] = zmq_context.socket(zmq.PUSH)
            push_nodes[foreign_identifier].bind('tcp://*:%s' % push_port)
            # tell port_assigner which ports to reply with
            push_port_assigner.send(meshlib.assigned_ports % {'identifier':identifier, 'pull_port':inbound_pull_proxy_port, 'push_port':push_port})
      else:
         verbose("Ignored invalid message: '%s'" % msg)
