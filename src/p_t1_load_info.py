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

supported_os = ['linux2']

# Connect a PUSH socket to master.py
if __name__=='__main__':
  master_socket_url = sys.argv[1]
  zmq_context       = zmq.Context()
  push_master       = zmq_context.socket(zmq.PUSH)
  push_master.connect(master_socket_url)

# Use meshlib.send_plugin_result('some message', push_master) to communicate
# with master.py

# END TEMPLATE -- Customize below.

import re, subprocess

class TestPlugin(unittest.TestCase):
  def test_00asteriskexists(self):
    "Check if asterisk exists"
    import os.path
    location = '/usr/sbin/asterisk'
    self.assertTrue(os.path.exists(location))

if __name__=='__main__':
   while 1:
      used_channels = 0
      chan_info = subprocess.Popen(['asterisk', '-rx', 'dahdi show channels'], stdout=subprocess.PIPE).communicate()[0].lstrip('\x1b[0;37m').rstrip('\x1b[0m').splitlines()
      chan_info.pop(0)
      chan_info.pop(0)
      available_channels=len(chan_info)
      chan_usage = available_channels * .9
      for chan in chan_info:
         inuse = re.search('\d (\d+) .*?',chan,re.DOTALL|re.MULTILINE)
         if inuse:
            used_channels += 1

      if used_channels >= chan_usage:
         meshlib.send_plugin_result("High T1 usage reported, %s out of %s" %(used_channels, available_channels),push_master)
