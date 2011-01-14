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

supported_os = ['linux2']

description = """
Check for running Xen virtual machines

Threshold: Less vm's running than expexted
"""

xen_path = meshlib.get_config('p_xen_list', 'xen_path', '/usr/sbin/xm')
running_vms = int(meshlib.get_config('p_xen_list', 'running_vms', '1')

def configured():
   import os
   return os.access(xen_path, os.X_OK)


import subprocess

if __name__=='__main__':
   while 1:
      vm_info = subprocess.Popen(['xm', 'list'], stdout=subprocess.PIPE).communicate()[0].splitlines()
      vm_info.pop(0)

      if len(vm_info) < running_vms:
         meshlib.send_plugin_result('There are less virtual machines running than expected!', push_master)
      time.sleep(60)

# Unit Tests
class TestPlugin(unittest.TestCase):
   def test_01krunning(self):
      "Check if xen is running"
      import os.path
      location = '/var/run/xend.pid'
      self.assertTrue(os.path.exists(location))
