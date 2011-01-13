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
supported_os = ['linux2', 'sunos5']

description = """
Checks to see if updates are available.

Threshold: If updates are available,
           then we create an event.
"""

if __name__ == '__main__':
   # Connect a PUSH socket to master.py
   master_socket_url = sys.argv[1]
   zmq_context       = zmq.Context()
   push_master       = zmq_context.socket(zmq.PUSH)
   push_master.connect(master_socket_url)

# Plugins will typically have an infinite main loop
import subprocess, os
if __name__ == '__main__':
   cmd = 0
   gentoo = False
   if sys.platform == 'sunos5':
      cmd = ["pkg", "image-update", "-n"]
   elif sys.platform == 'linux2':
      if os.path.exists('/usr/bin/yum'):
         cmd = ["yum", "check-update"]
      elif os.path.exists('/usr/bin/emerge'):
         gentoo = True
         cmd = ["emerge", "-tpvuD", "system"]
         cmd2 = ["emerge", "-tpvuD", "world"]
   if cmd == 0:
      sys.exit()
   while 1:
      check = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
      update = check.wait()
      if update != 0:
         update = True
      if gentoo == True:
         check = subprocess.Popen(cmd2, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
         update = check.wait()
         if update != 0:
            update = True
      if update == True:
         meshlib.send_plugin_result("Update(s) are available", push_master)
      time.sleep(3600)

# Unit Tests
class TestPlugin(unittest.TestCase):
   def test_00isroot(self):
      "User is root"
      import subprocess
      gotroot = subprocess.Popen("whoami", stdout = subprocess.PIPE)
      isroot = gotroot.communicate()[0]
      if isroot != 'root\n':
         self.fail("Must be root to run this plugin.")
