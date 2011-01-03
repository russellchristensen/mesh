#! /usr/bin/env python

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
from os import path
from atexit import register
from re import findall, compile, MULTILINE
from subprocess import Popen, PIPE
from sys import exit, argv
from datetime import datetime

global log_location; log_location = '/var/log/secure.log'
global parse; parse = compile(r'(.{15}) ([\w\d-]+) sshd\[(\d+)\]: ((?:Failed password)|(?:.*?))\s(.+)', MULTILINE)
global proc;

# Try to set the log file, otherwise, pass to keep the default
try:    log_location = argv[1]
except: pass

# Tail the log file
if path.isfile(log_location):
   proc = Popen(['tail', '-f', log_location], stdout=PIPE)
else:
   print 'Log file does not exist.'
   exit(1)

# Setup function to kill the child process at exit
try:
   @register
   def kill_child():
      '''Kill child process at exit'''
      print 'Killing child:', proc.pid
      proc.kill()
except:
   print 'Could not create the atexit function to kill the child process'
   print 'This is not fatal, but you may have rogue "tail" processes running'
   print "if this plugin doens't close properly"

while True:
   # Get a line from proc
   line = proc.stdout.readline()
   # Make sure the line is an ssh log line
   if 'ssh' not in str(line): continue
   # Parse the line
   # [0] at the end is because re.findall returns a list
   timestamp, server_name, num, line_type, line_contents = findall(parse, line)[0]

   print timestamp, server_name, num, line_type, line_contents
