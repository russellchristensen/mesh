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

plugin_name = 'p_apache_error'
supported_os = ['darwin', 'linux2', 'freebsd8', 'sunos5']
description = """
Look for some kind of apache error or something like that.

Threshold: If there's an error, we create an event.
"""
import subprocess, sys, re
from datetime import datetime

apache_ssl_error_log = meshlib.get_config(plugin_name, 'apache_ssl_error_log', '/var/log/apache2/ssl_error_log')

parse_ssl_error_log = re.compile(r'^\[([\w \d:]+)\] \[error\] \[client ([\d\.]+)\] (.+)', re.MULTILINE)
date_format = '%a %b %d %H:%M:%S %Y'

def configured():
   import os
   if not os.path.exists(apache_ssl_error_log) or os.access(apache_ssl_error_log, os.R_OK): return False
   return True

if __name__ == '__main__':
   proc = subprocess.Popen(['tail', '-f', apache_ssl_error_log], stdout=subprocess.PIPE)

   while 1:
      # Parse data from tail
      date, ip, error = re.findall(parse_ssl_error_log, proc.stdout.readline())[0]
      # Convert date to usable format
      date = datetime.strptime(date, date_format)
      # Return results
      meshlib.send_plugin_result(str('%s %s %s' % (date, ip, error)), push_master)

class TestPlugin(unittest.TestCase):
   def test_00apache_file_exists(self):
      '''Apache file exists'''
      import os.path
      if not os.path.isfile(apache_ssl_error_log):
         self.fail('Apache error log file not found! %s' % (apache_ssl_error_log))
   
   def test_01apache_file_readable(self):
      '''Apache file is readable by script'''
      import os
      if not os.access(apache_ssl_error_log, os.W_OK) or not os.access(apache_ssl_error_log, os.R_OK):
         self.fail('Apache error log file is not readable! %s' % (apache_ssl_error_log))
