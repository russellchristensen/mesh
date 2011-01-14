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

supported_os = ['darwin', 'linux2', 'freebsd8', 'sunos5']

description = """
Monitor CPU usage

Threshold: If cpu is more than cpu_threshold, then we create
           an event
"""
# ///Figure out what and how to get the cpu threshold we want to use
# monitor cpu usage, send it up constantly
import psutil 
if __name__ == '__main__':
   while 1:
      cpu = psutil.cpu_percent(interval=1)  
      meshlib.send_plugin_result("CPU: %s" % cpu, push_master)
      time.sleep(1)

# Unit Tests
class TestPlugin(unittest.TestCase):
   def test_00no_output(self):
      "Is there output?"
      if psutil.cpu_percent(interval=0) == '':
         self.fail("psutil.cpu_percent is returning no results")
