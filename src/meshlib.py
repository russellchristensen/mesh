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

import tempfile

def socket_url(transport):
   if transport == 'ipc':
      return "ipc:///" + tempfile.NamedTemporaryFile().name + '.ipc'
   else:
      raise("Invalid transport: " + str(transport))

def send_plugin_result(msg, socket):
   socket.send(msg)
