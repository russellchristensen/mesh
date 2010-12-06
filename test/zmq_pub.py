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

import time, zmq

context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind("ipc://testpublisher.ipc")

for i in range(3):
   pub_socket.send("Now is the time for all good men to come to the aid of their country.")
   time.sleep(1)
   
