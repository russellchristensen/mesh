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

import os, sys, tempfile

# We've got to find the root directory of the project to run tests!
global project_root_dir
project_root_dir = None
curr_root_dir = os.getcwd()
while not project_root_dir:
   curr_root_dir, last_element = os.path.split(curr_root_dir)
   if last_element == 'mesh':
      project_root_dir = os.path.join(curr_root_dir, 'mesh')
if not project_root_dir:
   print "Error, couldn't find the project root directory.  :-("
   sys.exit(1)

# For creating ZMQ URLs
def socket_url(transport):
   if transport == 'ipc':
      return "ipc:///" + tempfile.NamedTemporaryFile().name + '.ipc'
   else:
      raise("Invalid transport: " + str(transport))

# For plugins to send events to master.py
def send_plugin_result(msg, socket):
   socket.send(msg)
