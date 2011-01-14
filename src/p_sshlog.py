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

plugin_name = 'p_sshlog'
supported_os = ['darwin']
description = """
Check for invalid SSH logins.

Threshold: Every time an invalid SSH login is detect, an event is created.
"""

global log_location; log_location = meshlib.get_config(plugin_name, 'log_locaiton', '/var/log/secure.log')
global parse; parse = re.compile(r'(.{15}) ([\w\d-]+) sshd\[(\d+)\]: ((?:Failed password)|(?:.*?))\s(.+)', re.MULTILINE)
global proc;

def configured():
   import os
   if not os.path.exist(log_location) or not os.acess(log_location, os.R_OK): return False
   return True

import os, atexit, re, subprocess, sys

# /// Use meshlib to get config stuff like file locations
# /// ^- do that out here in global scope

if __name__ == '__main__':
   # Tail the log file
   if os.path.isfile(log_location):
      proc = subprocess.Popen(['tail', '-f', log_location], stdout=subprocess.PIPE)
   else:
      meshlib.send_plugin_result('Error: Log file does not exist. "%s"' % (log_location), push_master)
      sys.exit(1)

   # Setup function to kill the child process at exit
   try:
      @atexit.register
      def kill_child():
         '''Kill child process at exit'''
         meshlib.send_plugin_result('Notice: Killing child: %s' % (proc.pid), push_master)
         proc.kill()
   except:
      # /// Nah, just have it crash for now.
      meshlib.send_plugin_result('Error: Could not create the atexit function to kill the child process\nThis is not fatal, but you may have rogue "tail" processes running\nif this plugin doens\'t close properly', push_master)

   while True:
      # Get a line from proc
      line = proc.stdout.readline()
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
