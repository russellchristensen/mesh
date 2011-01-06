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

zmq_context = zmq.Context()
push_master = zmq_context.socket(zmq.PUSH)

def connect_push_master(url):
   push_master.connect(url)
   push_master.send("communicator.py is alive")

if __name__ == '__main__':
   master_pull_url = sys.argv[1]
   if not meshlib.is_socket_url(master_pull_url):
      print "Invalid socket url to connect to master.py: %s" % master_pull_url
      sys.exit(1)
   connect_push_master(master_pull_url)
