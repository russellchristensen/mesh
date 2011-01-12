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

# Remove the OSs your plugin doesn't support.
# Use meshlib.get_os() if you need to know what OS you're actually on.
supported_os = ['freebsd8']

if __name__ == '__main__':
# Connect a PUSH socket to master.py
   master_socket_url = sys.argv[1]
   zmq_context       = zmq.Context()
   push_master       = zmq_context.socket(zmq.PUSH)
   push_master.connect(master_socket_url)

# ////// Customized monitoring of...something  //////
import os, re, subprocess, smtplib

# Plugins will typically have an infinite main loop
if __name__ == '__main__':
   file = subprocess.Popen(['tail', '-f', '/var/log/maillog'],stdout=subprocess.PIPE)
   hostname = os.uname()[1]
   found = False
   while 1:
      start_time = time.time()
      outgoing = smtplib.SMTP('localhost')
      try:
         outgoing.sendmail('mailtest@%s' % hostname, 'blackhole@%s' % hostname, 'test email')
      except:
         meshlib.send_plugin_result('Message not sent!', push_master)
      while (time.time() - start_time) < 300:
         recent = file.stdout.readline()
         queued = re.search('.*?:.*?:.*?: (.*?):*mailtest*',recent,re.DOTALL|re.MULTILINE)
         if queued:
            print queued.groups()
            while (time.time() - start_time) < 300:
               recent = file.stdout.readline()
               if re.search('.*%s.*250 2.0.0 Ok.*' % queued.groups(1),recent,re.DOTALL|re.MULTILINE):
                  found = True
      if not found:
         meshlib.send_plugin_result('Message not sent within time!', push_master)

# Plugins communicate with master.py through meshlib.send_plugin_result()
# This is just an example, so we'll fake events by pausing.  Real loops usually block in I/O of some type.

# ////// Customized unit-testing of everything above.  It's common for unit tests to take _more_ code than the code they test.  //////
class TestPlugin(unittest.TestCase):
# First, test setup requirements (do files/commands/libraries exist, etc.)
   def test_00check_for_mail_log(self):
      """Check for maillog"""
      import os.path
      location='/var/log/maillog'
      if os.path.isfile(location):
         try:
            open(location).read()
            return True
         except:
            self.fail('Maillog file is not readable' % (location))
