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
supported_os = ['darwin', 'linux2', 'freebsd8', 'sunos5']

if __name__ == '__main__':
   # Connect a PUSH socket to master.py
   master_socket_url = sys.argv[1]
   zmq_context       = zmq.Context()
   push_master       = zmq_context.socket(zmq.PUSH)
   push_master.connect(master_socket_url)

# ////// Customized monitoring of...something  //////

# Use meshlib.send_plugin_result('some message', push_master) to communicate
# with master.py

# END TEMPLATE -- Customize below.

# Plugins will typically have an infinite main loop
import subprocess
if __name__ == '__main__':
   while 1:
      cmd = subprocess.Popen("uptime", stdout = subprocess.PIPE)
      uptime = cmd.communicate()[0]
      meshlib.send_plugin_result(uptime, push_master)
      time.sleep(1)

# ////// Customized unit-testing of everything above.  It's common for unit tests to take _more_ code than the code they test.  //////
class TestPlugin(unittest.TestCase):
   def test_00output(self):
      "Check for output"
      import subprocess
      cmd = subprocess.Popen("uptime", stdout = subprocess.PIPE)
      uptime = cmd.communicate()[0]
      if uptime == '':
         self.fail("Uptime is returning no output, something is very very wrong")
