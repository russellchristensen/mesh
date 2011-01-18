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
Detect invalid Samba login attempts.

Threshold: If an invalid login attemp is found,
           then we create an event.
"""

global log_path; log_path = meshlib.get_config('p_samba_login', 'log_path', '/var/log/samba')

def configured():
   import os
   if os.path.exists(log_path) == False:
      return False
   logs = os.listdir(log_path)
   for test in logs:
      if os.access("%s/%s" % (logs, test), os.R_OK) == False:
         return False
   return True

import subprocess, os, re
if __name__ == '__main__':
   while 1:
      logs = os.listdir(log_path)
      log_count = len(logs)
      for log in logs:
         search_log = "%s/%s" % (log_path, log)
         tail = subprocess.Popen(["tail", "-f", search_log], stdout = subprocess.PIPE)
         while not re.search('FAILED', search_log):
            tail = subprocess.Popen(["tail", "-f", search_log], stdout = subprocess.PIPE)
            if len(os.listdir(logpath)) != log_count:
               break
         meshlib.send_plugin_result(segfault, push_master)

# Unit Tests
class TestPlugin(unittest.TestCase):
   def test00tail(self):
      '''Tail is working properly'''
      import subprocess
      logs = os.listdir(log_path)
      for test in logs:
         try: tail = subprocess.Popen(['tail', '-f', '%s/%s' % (log_path, test)], stdout=subprocess.PIPE)
         except:
            self.fail("%s could not be read" % location)
