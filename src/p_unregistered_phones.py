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

import meshlib, sys, time, zmq

# Connect a PUSH socket to master.py
master_socket_url = sys.argv[1]
zmq_context       = zmq.Context()
push_master       = zmq_context.socket(zmq.PUSH)
push_master.connect(master_socket_url)

# Use meshlib.send_plugin_result('some message', push_master) to communicate
# with master.py

# END TEMPLATE -- Customize below.

import re
from time import *

fh = open('/var/log/asterisk/messages')

while 1:
  recent = fh.readline()
  phone = re.search("chan_sip.c: Registration from '<sip:(\d+)",recent, re.MULTILINE|re.DOTALL)
  if phone:
    curTime = strftime("%b %d %H:%M").split(' ')
    curTime = '%s  %s %s' %(curTime[0], curTime[1].lstrip('0'), curTime[2])
    if re.search(curTime,recent, re.MULTILINE|re.DOTALL):
      meshlib.send_plugin_result('%s failed registration' % phone.group(1), push_master)
