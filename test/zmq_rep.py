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
rep_socket = context.socket(zmq.REP)
rep_socket.bind("ipc://testreqrep.ipc")

incoming_message = rep_socket.recv()
if incoming_message == "Are you there?":
   rep_socket.send("Yes, I'm here")
   sys.exit(0)
else:
   rep_socket.send("Wrong question")
   sys.exit(1)
