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

supported_os = ['freebsd8']

description = """
Verify that message are being sent within the threshold

Threshold: 300s
"""

send_threshold = int(meshlib.get_config('p_mail_send', 'failed_threshold', '300'))
log_location = meshlib.get_config('p_mail_send', 'log_location', None)
from_address = meshlib.get_config('p_mail_send', 'from_address', None)
to_address   = meshlib.get_config('p_mail_send', 'to_address', None)

def configured():
   import os
   if not os.access(log_location, os.R_OK):
      return False
   elif not send_thrsehold.isdigit():
      return False
   if not from_address or not to_address:
      return False
   else:
      return True


import os, re, subprocess, smtplib

queue_pattern = re.compile('.*?:.*?:.*?: (.*?):*%s*'% from_address,re.DOTALL|re.MULTILINE)

# Plugins will typically have an infinite main loop
if __name__ == '__main__':
   file = subprocess.Popen(['tail', '-f', log_location],stdout=subprocess.PIPE)
   found = False
   while 1:
      start_time = time.time()
      outgoing = smtplib.SMTP('localhost')
      try:
         outgoing.sendmail(from_address, to_address, 'test')
      except:
         meshlib.send_plugin_result('Message not sent!', push_master)
      while (time.time() - start_time) < send_threshold:
         recent = file.stdout.readline()
         queued = re.search(queue_pattern,recent)
         if queued:
            while (time.time() - start_time) < send_threshold:
               recent = file.stdout.readline()
               if re.search('.*%s.*250 2.0.0 Ok.*' % queued.groups(1),recent,re.DOTALL|re.MULTILINE):
                  found = True
      if not found:
         meshlib.send_plugin_result('Message not sent within time!', push_master)
      time.sleep(60)


class TestPlugin(unittest.TestCase):
# First, test setup requirements (do files/commands/libraries exist, etc.)
   def test_00check_for_mail_log(self):
      """Check for maillog"""
      import os.path
      location= log_location
      if os.path.isfile(location):
         try:
            open(location).read()
            return True
         except:
            self.fail('Maillog file is not readable' % (location))
