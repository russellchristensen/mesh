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
Check for sip phones that try to register, but fail.

Threshold: Every time a sip phone fails registration, an event is created.
"""

log_location = meshlib.get_config('p_unregistered_phones', 'log_location', None)

def configured():
   if not log_location:
      return False
   return True

import re, subprocess
from time import *

if __name__=='__main__':
   while 1:
      for line in meshlib.tail(log_location):
         phone = re.search("chan_sip.c: Registration from '<sip:(\d+)",log_stat, re.MULTILINE|re.DOTALL)
         if phone:
            meshlib.send_plugin_result('%s failed registration' % phone.group(1), push_master)

class TestPlugin(unittest.TestCase):
   def test_00logexists(self):
      return True
