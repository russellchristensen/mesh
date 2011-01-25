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

import meshlib, sys, unittest

if __name__ == '__main__':
   zmq_context, push_master = meshlib.init_plugin(sys.argv)

supported_os = ['linux2']

description = """
Reports the room temperature of a "temperature@lert usb device in Celcius."

Threshold: If the temperature rises higher than the temperature, then we create
           an event.
"""
# //// Now get any config values you need
temperature_threshold = int(meshlib.get_config('p_temperature', 'temperature_threshold', '32'))

import subprocess, time

def configured():
   try: 
      subprocess.call("tempdemo")
      return true
   except:
      return false

def get_temp():
   proc = subprocess.Popen("tempdemo", stdout = subprocess.PIPE)
   temperature = proc.stdout.readline()
   if "Error" in temperature:
      subprocess.call(["udevd"])
      proc = subprocess.Popen("tempdemo", stdout = subprocess.PIPE)
      temperature = proc.stdout.readline()
      if "Error" in temperature:
         temperature = False
   temperature = float(temperature)
   temperature = (temperature - 32)/(9.0/5.0)
   return temperature

if __name__ == '__main__':
   while 1:
      temperature = get_temp()
      if temperature == False:
         meshlib.send_plugin_result("USB temperature device is non-responsive", push_master)
      if temperature > temperature_threshold:
         time.sleep(1)
         temperature = get_temp()
         if temperature > temperature_threshold:
            meshlib.send_plugin_result("Server room temperature is %d C")
      time.sleep(1)

# Unit Tests
class TestPlugin(unittest.TestCase):
   def test_00output(self):
      """Getting appropriate output"""
      import subprocess
      try: 
         proc = subprocess.Popen("tempdemo", stdout = subprocess.PIPE)
         try: 
            temperature = float(proc.stdout.readline())
         except:
            self.fail("couldn't convert to a float")
      except:
         self.fail("Command not working")
