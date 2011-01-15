#!/usr/bin/env python

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

if __name__ == '__main__':
   # IPC urls (passed in at startup from master.py)
   config_file, communicator_pull_url, port_requestor_pull_url = sys.argv[1:]
   for url in sys.argv[2:]:
      if not meshlib.is_socket_url(url):
         print "Error: Invalid socket url: '%s'" % url
         sys.exit(1)
   # Connect ZMQ sockets
   pull.bind(port_requestor_pull_url)
   push_communicator.connect(communicator_pull_url)
   # Main Loop
   while True:
      msg = pull.recv()
      verbose(msg)
      command, ip, port = msg.split(':')
      temp_req_socket = zmq_context.socket(zmq.REQ)
      temp_req_socket.connect("tcp://%s:%s" % (ip, port))
      temp_req_socket.send("request_ports")
      reply = temp_req_socket.recv()
      del temp_req_socket
      push_communicator.send("port_requestor:%s" % reply)
