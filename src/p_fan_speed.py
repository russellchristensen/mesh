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

supported_os = ['linux2']

description = """
Monitors fan speed on machines that have sensors.

Threshold: If fan speed is lower than min_threshold or higher than max_threshold,
           then we create an event.
"""
min_threshold = int(meshlib.get_config('p_fan_speed', 'min_threshold', '700'))
max_threshold = int(meshlib.get_config('p_fan_speed', 'max_threshold', '9500'))

def configured():
   import os, subprocess
   if os.path.exists("/usr/bin/sensors") == False:
      return False
   sensors = subprocess.Popen("sensors", stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
   if"sensors-detect" in sensors:
      return False
   return True

import subprocess, re
if __name__ == '__main__':
   while 1:
      sensors = subprocess.Popen( ('/usr/bin/env', 'bash', '-c', 'sensors | grep fan'), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
      fan = sensors.communicate()[0]
      fan = re.sub('\(.*?\)', '', fan)
      fan = fan.split()
      for result in fan:
         if 'fan' in result:
            fan = result
         elif result.isdigit():
            speed = result
            if speed > max_threshold:
               meshlib.send_plugin_result("%s: %s" % (fan, speed), push_master)
            elif speed < min_threshold:
               if speed == 0:
                  meshlib.send_plugin_result("%s is either unresponsive or lm_sensors is misconfigured" % fan, push_master)
               else:
                  meshlib.send_plugin_result("%s: %s" % (fan, speed), push_master)
      time.sleep(60)

# Unit Tests
class TestPlugin(unittest.TestCase):
   import subprocess, re
   sensors = subprocess.Popen( ('/usr/bin/env', 'bash', '-c', 'sensors | grep CPU'), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
   fan = sensors.communicate()[0]
   fan = re.sub('\(.*?\)', '', fan)
   def test_00hyst_detect(self):
      """Is there unwanted data"""
      if "min" in temperature:
         self.fail("Regular expression failed to remove unwanted data")
