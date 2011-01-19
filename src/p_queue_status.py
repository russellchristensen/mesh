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

description ="""
Check which queues are currently running

Threshold: Change in running queues
"""

configured_queues = meshlib.get_config('p_dovecot_login_fail', 'queues', None)
asterisk_bin = meshlib.get_config('p_dovecot_login_fail', 'asterisk_bin', None)

def configured():
   import os
   if not configured_queues:
      return False
   if not asterisk_bin:
      return False
   if not os.access(asterisk_bin, os.X_OK):
      return False
   return True

import re, subprocess, time

if __name__=='__main__':
  while 1:
    queues = []
    queue_info = subprocess.Popen(['asterisk', '-rx', 'queue show'], stdout=subprocess.PIPE).communicate()[0].lstrip('\x1b[0;37m').rstrip('\x1b[0m').splitlines()
    for line in queue_info:
      queue = re.search('(\w+q)',line,re.DOTALL|re.MULTILINE)
      if queue:
        queues.append(queue.group(1))

    if len(queues) < len(configured_queues):
      meshlib.send_plugin_result('One of the queues stopped functioning', push_master)
    time.sleep(60)

class TestPlugin(unittest.TestCase):
  def test_00asteriskexists(self):
     pass
