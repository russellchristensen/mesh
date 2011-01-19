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

supported_os = ['darwin', 'sunos5']
plugin_name = 'p_disk'
description = """
Checks for disk usage.

Threshold: Disk usage above 90% causes an event.
"""
threshold = meshlib.get_config(plugin_name, 'threshold', '90')

def configured():
   try: int(threshold)
   except: return False
   return True

import subprocess, re, time

global parse; parse = re.compile(r'^(.+)[\n\r]? +(\d+) +(\d+) +(\d+) +(\d+)% +([a-zA-Z/_\-\.\d]+)', re.MULTILINE)

if __name__ == '__main__':
   # Main Loop
   while True:
      proc = subprocess.Popen(['df'], stdout=subprocess.PIPE)
      # Get df output
      df_out = proc.stdout.read()
      # Iterate through the parsed output of df
      for fs, blocks, used, available, percent, mounted in re.findall(parse, df_out):
         # Convert the parsed data for ease of use later
         fs, blocks, used, available, percent, mounted =  fs.strip(), int(blocks.strip()), int(used.strip()), int(available.strip()), int(percent.strip()), mounted.strip()
         if percent > threshold:
            meshlib.send_plugin_result('%s %s %s %s %s %s' % (fs, blocks, used, available, percent, mounted), push_master)
      time.sleep(int(threshold))

class TestPlugin(unittest.TestCase):
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
         re.findall(parse, proc.stdout.read())
      except:
         self.fail('df output was not as expected, and could not be parsed.')
      proc.kill()
