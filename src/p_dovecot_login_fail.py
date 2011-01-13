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

supported_os = ['freebsd8']

description ="""
Detect Dovecot Failed Login Attempts

Threshold: Any failed attempt
"""

failed_threshold = int(meshlib.get_config('p_dovecot_login_fail', 'failed_threshold', '0'))
log_location = meshlib.get_config('p_dovecot_login_fail', 'log_location', '/var/log/dovecot')

if __name__ == '__main__':
# Connect a PUSH socket to master.py
   master_socket_url = sys.argv[1]
   zmq_context       = zmq.Context()
   push_master       = zmq_context.socket(zmq.PUSH)
   push_master.connect(master_socket_url)

# ////// Customized monitoring of...something  //////
import re, time, subprocess

# Plugins will typically have an infinite main loop
if __name__ == '__main__':
   fh = open(log_location, 'r')
   while 1:
      recent = fh.readline()
      curTime = time.strftime("%Y-%m-%d-%H:%M")
      user_info = re.search('Disconnected .*?: user=<(.*?)>, method=PLAIN, rip=(.*?), lip=70.102.57.181, TLS',recent,re.DOTALL|re.MULTILINE)
      if user_info and re.search(curTime,recent,re.DOTALL|re.MULTILINE):
         user    = user_info.group(1)
         ip      = user_info.group(2)
         meshlib.send_plugin_result('%s failed login from %s' %(user,ip), push_master)

      
# Plugins communicate with master.py through meshlib.send_plugin_result()
# This is just an example, so we'll fake events by pausing.  Real loops usually block in I/O of some type.

# ////// Customized unit-testing of everything above.  It's common for unit tests to take _more_ code than the code they test.  //////
class TestPlugin(unittest.TestCase):
# First, test setup requirements (do files/commands/libraries exist, etc.)
   def test_00check_for_dovecoti_log(self):
      """Check for dovecot log"""
      import os.path
      if os.path.isfile(log_location):
         try:
            open(location).read()
            return True
         except:
            self.fail('Dovectcot log file "%s" is not readable' % (location))
