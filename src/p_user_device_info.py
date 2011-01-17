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

supported_os=['linux2']

description= """
Check for unapproved SIP devices

Threshold: device not in list

'asterisk -rx sip show peer $extension' - the device is listed as Useragent
"""

devices = meshlib.get_config('p_user_device_info', 'devices', None)
asterisk_bin = meshlib.get_config('p_user_device_info', 'asterisk_bin', None)


def configured():
   import os
   if not devices:
      return False
   if not os.access(asterisk_bin, X_OK):
      return False
   return True

# /// Add description
# /// Get config items
# /// Description of where to get the device strings

import re, subprocess

if __name__=='__main__':
   while 1:
      users = []
      user_info = subprocess.Popen(['asterisk', '-rx', 'sip show peers'], stdout=subprocess.PIPE).communicate()[0].lstrip('\x1b[0;37m').rstrip('\x1b[0m').splitlines()
      for user in user_info:
         user = re.search('(\d\d\d\d)',user,re.DOTALL|re.MULTILINE)
         if user:
            users.append(user.groups(1))

      for user in users:
         device_info = subprocess.Popen(['asterisk', '-rx', 'sip show peer %s' %user], stdout=subprocess.PIPE).communicate()[0]
         device = re.search('\n  Useragent    : (.*)\n  Reg. Contact', device_info, re.DOTALL|re.MULTILINE)
         if device and not device.groups(0)[0] in devices:
            meshlib.send_plugin_result('%s in use by %s is not an approved device' % (device.groups(0)[0], user[0]), push_master)


class TestPlugin(unittest.TestCase):
   def test_00asteriskexists(self):
      return True
