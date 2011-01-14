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

Threshold: Change in virtual machines
"""
xen_path = meshlib.get_config('p_xen_list', 'xen_path', '/usr/sbin/xm')

# /// Add description
# /// Add config items (paths to xm, etc.)

import re, subprocess

if __name__=='__main__':
   current_vms = []
   while 1:
      vms = []
      vm_info = subprocess.Popen(['xm', 'list'], stdout=subprocess.PIPE).communicate()[0].splitlines()
      for line in vm_info:
         vm.append(queue.group(1))

   # /// Oops!  Fix the loop.
   if len(current_vms) == 0:
      current_vms = vms

   missing_vm = set(current_vms).difference(set(vms))
   if missing_vm:
      meshlib.send_plugin_result('%s is no longer functioning' % missing_vm, push_master)

   # /// Polling too fast!

# Unit Tests
class TestPlugin(unittest.TestCase):
   def test_00asteriskexists(self):
      "Check if xen"
      import os.path
      location = '/usr/sbin/xm'
      self.assertTrue(os.path.exists(location))

   def test_01asteriskrunning(self):
      "Check if asterisk is running"
      import os.path
      location = '/var/run/xend.pid'
      self.assertTrue(os.path.exists(location))
