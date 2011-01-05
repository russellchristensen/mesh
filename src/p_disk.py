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

import subprocess
import time
import re

# Plugins will typically have an infinite main loop
if __name__ == '__main__':
   while True:
      proc = subprocess.Popen(['df'], stdout=subprocess.PIPE)
      # Get df output
      df_out = proc.stdout.read()
      parse = re.compile(r'^(.+)[\n\r]? +(\d+) +(\d+) +(\d+) +(\d+)% +([a-zA-Z/_\-\.\d]+)', re.MULTILINE)
      # Iterate through the parsed output of df
      for fs, blocks, used, available, percent, mounted in re.findall(parse, df_out):
         # Convert the parsed data for ease of use later
         fs, blocks, used, available, percent, mounted =  fs.strip(), int(blocks.strip()), int(used.strip()), int(available.strip()), int(percent.strip()), mounted.strip()
         meshlib.send_plugin_result('%s %s %s %s %s %s' % (fs, blocks, used, available, percent, mounted), push_master)
      time.sleep(1)

# ////// Customized unit-testing of everything above.  It's common for unit tests to take _more_ code than the code they test.  //////
class TestPlugin(unittest.TestCase):
   # First, test setup requirements (do files/commands/libraries exist, etc.)
   def test_00import_subprocess(self):
      '''Can import subprocess'''
      import subprocess

   def test_01df_exists(self):
      '''"df" command exists'''
      import subprocess
      proc = subprocess.Popen(['df'], stdout=subprocess.PIPE)
      if 'Filesystem' not in proc.stdout.read():
         self.fail('df failed to run properly.')
      proc.kill()

   def test_02df_output_parsed(self):
      '''"df" command output can be parsed as expected'''
      import subprocess, re
      proc = subprocess.Popen(['df'], stdout=subprocess.PIPE)
      try:
         parse = re.compile(r'^(.+)[\n\r]? +(\d+) +(\d+) +(\d+) +(\d+)% +([a-zA-Z/_\-\.\d]+)', re.MULTILINE)
         re.findall(parse, proc.stdout.read())
      except:
         self.fail('df output was not as expected, and could not be parsed.')
      proc.kill()
