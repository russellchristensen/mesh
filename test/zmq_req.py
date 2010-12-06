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

import sys, zmq

context = zmq.Context()
req_socket = context.socket(zmq.REQ)
req_socket.connect("ipc://testreqrep.ipc")

req_socket.send("Are you there?")
reply = req_socket.recv()
if reply == "Yes, I'm here":
   sys.exit(0)
else:
   sys.exit(1)
