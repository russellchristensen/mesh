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

import meshlib, subprocess, sys, time, unittest, zmq

# Connect a PUSH socket to master.py
master_socket_url = sys.argv[1]
zmq_context       = zmq.Context()
push_master       = zmq_context.socket(zmq.PUSH)
push_master.connect(master_socket_url)

location = '/var/log/messages'
class TestPlugin:
  def test_00logexists(self):
    "Check if messages file exists and is readable"
    import os.path
    if os.path.isfile(location):
      try:
        open(location).read()
        return True
      except:
        self.fail('Messages file "%s" is not readable' % (location))
    self.fail('No messages file found!')

while 1:
   tail = subprocess.Popen( ('/usr/bin/env', 'bash', '-c', 'tail /var/log/messages | grep segfault'), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
   segfault = tail.communicate()[0]
   meshlib.send_plugin_result(segfault, push_master)
   time.sleep(1)
 

      


