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

plugin_name = 'p_sshlog'
supported_os = ['darwin']
description = """
Check for invalid SSH logins.

Threshold: Every time an invalid SSH login is detect, an event is created.
"""

import os, re, subprocess, sys

global log_location; log_location = meshlib.get_config(plugin_name, 'log_locaiton', '/var/log/secure.log')
global parse; parse = re.compile(r'(.{15}) ([\w\d-]+) sshd\[(\d+)\]: ((?:Failed password)|(?:.*?))\s(.+)', re.MULTILINE)
global proc;

def configured():
   import os
   if not os.path.exists(log_location) or not os.access(log_location, os.R_OK): return False
   return True

if __name__ == '__main__':
   for line in meshlib.tail(log_location):
      # Make sure the line is an ssh log line
      if 'ssh' in str(line):
         # Parse the line
         # [0] at the end is because re.findall returns a list
         timestamp, server_name, num, line_type, line_contents = re.findall(parse, line)[0]

         meshlib.send_plugin_result('%s %s %s %s %s' % (timestamp, server_name, num, line_type, line_contents), push_master)

class TestPluginSSH(unittest.TestCase):
   def test_00tail_exists(self):
      '''Command tail exists'''
      import subprocess
      try: proc = subprocess.Popen(['tail'], stdout=subprocess.PIPE)
      except:
         self.fail('Command "tail" does not exist.')
      proc.kill()

   def test_02tail_read(self):
      '''Tail can read the contents of the log file'''
      import subprocess

      log_location = '/var/log/secure.log'

      try: proc = subprocess.Popen(['tail', '-f', log_location], stdout=subprocess.PIPE)
      except:
         self.fail('Could not read the log file "%s"' % (log_location))
      proc.kill()
