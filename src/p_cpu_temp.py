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
supported_os = ['linux2']

description = """
Monitor the temperature of machines that have sensors.

Threshold: If the temperature goes higher than the threshold,
           then we create an event.
"""
#///Currently this plugin passes a string not an integer need to figure out what and how to set for this threshold
temp_threshold = int(meshlib.get_config('p_cpu_temp', 'temp_threshold',

if __name__ == '__main__':
   # Connect a PUSH socket to master.py
   master_socket_url = sys.argv[1]
   zmq_context       = zmq.Context()
   push_master       = zmq_context.socket(zmq.PUSH)
   push_master.connect(master_socket_url)

import subprocess
if __name__ == '__main__':
   while 1:
      sensors = subprocess.Popen( ('/usr/bin/env', 'bash', '-c', 'sensors -f | grep CPU'), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
      temperature = sensors.communicate()[0]
      meshlib.send_plugin_result(temperature, push_master)
      time.sleep(60)

# Unit Tests
class TestPlugin(unittest.TestCase):
   def test_00sensors_installed(self):
      """Is lm_sensors installed and configured"""
      import os
      if os.path.exists("/usr/bin/sensors") == False:
         self.fail("lm_sensors is not installed")

   def test_03sensors_configured(self):
      import subprocess
      sensors = subprocess.Popen("sensors", stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
      if"sensors-detect" in sensors:
         self.fail("lm_sensors is not configured, run sensors-detect on the machine you are trying to monitor")
