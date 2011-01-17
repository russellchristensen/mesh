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

def verbose(msg):
   print "port_requestor:", msg

def connect_request(ip, port):
   temp_req_socket = zmq_context.socket(zmq.REQ)
   temp_req_socket.connect("tcp://%s:%s" % (ip, port))
   temp_req_socket.send(meshlib.request_ports % {'identifier':meshlib.get_identifier()})
   reply = temp_req_socket.recv()
   del temp_req_socket
   return reply

if __name__ == '__main__':
   # IPC urls (passed in at startup from master.py)
   config_file, communicator_pull_url, port_requestor_pull_url = sys.argv[1:]
   meshlib.load_config(config_file)
   for url in [communicator_pull_url, port_requestor_pull_url]:
      if not meshlib.is_socket_url(url):
         print "Error: Invalid socket url: '%s'" % url
         sys.exit(1)
   # Connect ZMQ sockets
   pull.bind(port_requestor_pull_url)
   push_communicator.connect(communicator_pull_url)
   # Main Loop
   while True:
      msg = pull.recv()
      msg_parts = msg.split(':')
      if msg_parts[0] == 'connect_node':
         verbose("Handling connect_node command: '%s'" % msg)
         command, ip, port = msg_parts
         reply = connect_request(ip, port)
         match = meshlib.error_pat.search(reply)
         if match:
            verbose("Got an error reply: '%s'" % reply)
            continue
         match = meshlib.assigned_ports_pat.search(reply)
         if match:
            verbose("Got assigned ports: '%s' from %s:%s" % (reply, ip, port))
            push_communicator.send("port_requestor:got_node_ports:%s:%s:%s:%s" % (ip, port, match.group('pull_port'), match.group('push_port')))
      else:
         verbose("Invalid command: '%s'" % msg)
