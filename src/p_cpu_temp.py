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
Monitor the temperature of machines that have sensors.

Threshold: If the temperature goes higher than the threshold,
           then we create an event.
"""
temp_threshold = int(meshlib.get_config('p_cpu_temp', 'temp_threshold','80'))

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
      sensors = subprocess.Popen( ('/usr/bin/env', 'bash', '-c', 'sensors | grep CPU'), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
      temperature = sensors.communicate()[0]
      temperature = re.sub('\(.*?\)', '', temperature)
      temperature = temperature.split()
      for result in temperature:
         if 'CPU' in result:
            cpu = result
         elif '+' in result:
            temp = result
            if temp > temp_threshold:
               meshlib.send_plugin_result("%s: %s" % (cpu, temp), push_master)
      time.sleep(60)

# Unit Tests
class TestPlugin(unittest.TestCase):
   import subprocess, re
   sensors = subprocess.Popen( ('/usr/bin/env', 'bash', '-c', 'sensors | grep CPU'), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
   temperature = sensors.communicate()[0]
   temperature = re.sub('\(.*?\)', '', temperature)
   def test_00hyst_detect(self):
      """Is there unwanted data"""
      if "hyst" in temperature:
         self.fail("Regular expression failed to remove unwanted data")
   def test_04detect_reading(self):
      """Is there a temperature reading"""
      temperature = temperature.split()
      for result in temperature:
         if '+' in result:
               temp = result
         if result < 1:
            self.fail("Not getting a reading over 0")
