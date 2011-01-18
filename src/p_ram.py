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
Monitors ram usage.

Threshold: If ram usage is greater than ram_threshold,
           then we create an event.
"""

ram_threshold = int(meshlib.get_config('p_ram', 'ram_threshold', '25'))

def configured():
   try:
      import psutil
   except:
      return False
   return True


import psutil

def available_mem():
   return psutil.avail_phymem() / 1024 / 1024

def used_mem():
   return psutil.used_phymem() / 1024 / 1024

if __name__ == '__main__':
   total = psutil.TOTAL_PHYMEM / 1024 / 1024
   percentage = ".%d * %s" % (ram_threshold, total)
   while 1:
      if available_mem() < percentage:
         meshlib.send_plugin_result("|Total: %s| |Available: %s| |Used: %s|" % (total, available_mem(), used_mem()), push_master)
      time.sleep(1)

# Unit Tests
class TestPlugin(unittest.TestCase):
   def test_00available_mem(self):
      "available_mem() returns memory in megabytes"
      amount = available_mem()
      if amount <= 0:
         self.fail("Got unrealistic result.")
      elif amount != psutil.avail_phymem() / 1024 / 1024:
         self.fail("It's not in megabytes!")

   def test_01used_mem(self):
      "used_mem() returns memory in megabytes"
      amount = used_mem()
      if amount <= 0:
         self.fail("Got unrealistic result.")
      elif amount != psutil.used_phymem() / 1024 / 1024:
         self.fail("It's not in megabytes!")
