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

import zmq

context = zmq.Context()
sub_socket = context.socket(zmq.SUB)
sub_socket.connect("ipc://testpublisher.ipc")

sub_socket.setsockopt(zmq.SUBSCRIBE, "")

count = 0
while count < 10:
   count += 1
   my_message = sub_socket.recv()
   print "message from publisher is", my_message
