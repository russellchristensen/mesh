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

import time, subprocess

if __name__ == '__main__':
   while 1:
      uptime = subprocess.Popen(['uptime'], stdout=subprocess.PIPE)
      hostname = subprocess.Popen(['hostname'], stdout=subprocess.PIPE)

      meshlib.send_plugin_result(str(hostname.stdout.read() +' '+ uptime.stdout.read()), push_master)

      uptime.kill()
      hostname.kill()

      time.sleep(5)

class TestPlugin(unittest.TestCase):
   def test_00import_subprocess(self):
      '''Can import subprocess'''
      import subprocess

   def test_01import_time(self):
      '''Can import time'''
      import time

   def test_04uptime_exists(self):
      '''"uptime" command exists'''
      import subprocess
      proc = subprocess.Popen(['uptime'], stdout=subprocess.PIPE)
      proc.kill()

   def test_04hostname_exists(self):
      '''"hostname" command exists'''
      import subprocess
      proc = subprocess.Popen(['hostname'], stdout=subprocess.PIPE)
      proc.kill()
