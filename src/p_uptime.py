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

supported_os = ['darwin', 'linux2', 'freebsd8', 'sunos5']

plugin_name = 'p_uptime'
description = """
Displays results of uptime command. Including uptime, users logged in and average load.

Threshold: report when the uptime is over a year
"""
frequency = meshlib.get_config(plugin_name, 'frequency', '60')
threshold = meshlib.get_config(plugin_name, 'threshold', '365')

def configured():
   import os
   try: int(frequency_threshold)
   except: return False
   if not os.access('/bin/uptime', os.X_OK): return False

import subprocess, time, datetime, re
if __name__ == '__main__':
   while 1:
      cmd = subprocess.Popen("uptime", stdout = subprocess.PIPE)
      uptime = cmd.communicate()[0]
      current_time, days_up, time_up, users, avg1, avg5, avg15 = re.findall(re.compile(r'((?:\d+:\d\d)|(?:\d+\.\d+)|(?:\d))'), uptime)
      if int(int(days_up) % int(threshold)) == 0:
         meshlib.send_plugin_result(uptime, push_master)
      time.sleep(int(frequency))

# Unit Tests
class TestPlugin(unittest.TestCase):
   def test_00output(self):
      "Check for output"
      import subprocess
      cmd = subprocess.Popen("uptime", stdout = subprocess.PIPE)
      uptime = cmd.communicate()[0]
      if uptime == '':
         self.fail("Uptime is returning no output, something is very very wrong")
