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

import meshlib, time, sys, zmq

#------------------------------------------------------------------------------
# ZMQ Setup

# Context & sockets for communicator.py
zmq_context       = zmq.Context()
pull              = zmq_context.socket(zmq.PULL)
push_communicator = zmq_context.socket(zmq.PUSH)

def verbose(msg):
   print "port_assigner:", msg

if __name__ == '__main__':
   # command-line arguments
   config_file           = sys.argv[1]
   tcp_direction         = sys.argv[2] # 'inbound' or 'outbound'
   ip_or_domain          = sys.argv[3] # IP to bind or connect to.  '*' for inbound means bind all interfaces.
   port                  = sys.argv[4]
   communicator_pull_url = sys.argv[5]
   if not meshlib.is_socket_url(communicator_pull_url):
      print "Error: Invalid socket url: '%s'" % communicator_pull_url
      sys.exit(1)
   # Connect/Bind ZMQ sockets
   push_communicator.connect(communicator_pull_url)
   if tcp_direction == 'inbound':
      pull.bind('tcp://%s:%s' % (ip_or_domain, port))
   elif tcp_direction == 'outbound':
      pull.connect('tcp://%s:%s' % (ip_or_domain, port))
   else:
      print "Error: Invalid direction '%s'" % tcp_direction
      sys.exit(2)
   # Main Loop
   while True:
      msg = pull.recv()
      verbose("pull_proxy %s:%s:%s received: '%s'" % (tcp_direction, ip_or_domain, port))
      push_communicator.send(msg)
