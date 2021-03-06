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
Monitors current T1 loads

Threshold: 90
"""

t1_threshold = int(meshlib.get_config('p_t1_load_info', 't1_threshold', '90'))
asterisk_bin = meshlib.get_config('p_t1_load_info', 'asterisk_bin', None)

def configured():
   import os
   if not t1_threshold:
      return False
   if not asterisk_bin:
      return False
   if not os.access(asterisk_bin, os.X_OK):
      return False
   return True

import re, subprocess, time

if __name__=='__main__':
   while 1:
      used_channels = 0
      chan_info = subprocess.Popen(['asterisk', '-rx', 'dahdi show channels'], stdout=subprocess.PIPE).communicate()[0].lstrip('\x1b[0;37m').rstrip('\x1b[0m').splitlines()
      chan_info.pop(0)
      chan_info.pop(0)
      available_channels=len(chan_info)
      chan_usage = available_channels * (t1_threshold/100)
      for chan in chan_info:
         inuse = re.search('\d (\d+) .*?',chan,re.DOTALL|re.MULTILINE)
         if inuse:
           used_channels += 1

      if used_channels >= chan_usage:
         meshlib.send_plugin_result("High T1 usage reported, %s out of %s" %(used_channels, available_channels),push_master)
      time.sleep(60)

class TestPlugin(unittest.TestCase):
   def test_00asteriskexists(self):
      "Check if asterisk exists"
      pass
