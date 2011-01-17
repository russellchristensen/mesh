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

if __name__ == '__main__':
   # Connect a PUSH socket to master.py
   master_socket_url = sys.argv[1]
   zmq_context       = zmq.Context()
   push_master       = zmq_context.socket(zmq.PUSH)
   push_master.connect(master_socket_url)

supported_os = ['linux2', 'freebsd8', 'sunos5']

description = """
Detect segfaults.

Threshold: If a segfault is detected in the logs,
           then we create an event.
"""

global location; location = meshlib.get_config('p_segfault', 'location', '/var/log/messages')

def configured():
   import os
   if os.path.exists(location) or not os.access(location, os.R_OK): return False
   return True

import subprocess, re
if __name__ == '__main__':
   tail = subprocess.Popen(["tail", "-f", location], stdout = subprocess.PIPE)
   segfault = tail.stdout.readline()
   while 1:
      while not re.search('segfault', segfault):
         segfault = tail.stdout.readline()
      meshlib.send_plugin_result(segfault, push_master)

# Unit Tests
class TestPlugin(unittest.TestCase):
   def test00tail(self):
      '''Tail is working properly'''
      import subprocess

      try: tail = subprocess.Popen(['tail', '-f', location], stdout=subprocess.PIPE)
      except:
         self.fail("%s could not be read" % location)
