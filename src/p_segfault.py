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

import meshlib, sys, time, unittest, zmq

# Remove the OSs your plugin doesn't support.
# Use meshlib.get_os() if you need to know what OS you're actually on.
supported_os = ['linux2', 'freebsd8', 'sunos5']

description = """
Detect segfaults.

Threshold: If a segfault is detected in the logs,
           then we create an event.
"""


if __name__ == '__main__':
   # Connect a PUSH socket to master.py
   master_socket_url = sys.argv[1]
   zmq_context       = zmq.Context()
   push_master       = zmq_context.socket(zmq.PUSH)
   push_master.connect(master_socket_url)

location = meshlib.get_config('p_segf', 'messages_file_location', '/var/log/messages')

import subprocess
if __name__ == '__main__':
   while 1:
      # /// Redo with interrupt-driven design!!!  (tail -f)
      tail = subprocess.Popen( ('/usr/bin/env', 'bash', '-c', 'tail %s | grep segfault' % location), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
      segfault = tail.communicate()[0]
      if segfault:
         meshlib.send_plugin_result(segfault, push_master)
         time.sleep(1)

# Unit Tests
class TestPlugin(unittest.TestCase):
   def test_00logexists(self):
      "Messages file exists and is readable"
      import os.path
      # /// Use readable() from somewhere instead
      if os.path.isfile(location):
         try:
            open(location).read()
            return True
         except:
            self.fail('Messages file "%s" is not readable' % (location))
      self.fail('No messages file found!')
