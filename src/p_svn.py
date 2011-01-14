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

supported_os = ['linux2']
description = """
Watch for subversion commits on a repository.

Threshold: When ever a new commit is detected, an event is created.
"""

def configured():
   import sys, subprocess
   for repo in sys.argv[1:]:
      try: proc = subprocess.Popen(['svn', 'info', repo], stdout=subprocess.PIPE)
      except: return False
   return True

import subprocess, re

plugin_name = 'p_svn'
parse = re.compile(r'^[\w ]+: (.+)[\n\r]?', re.MULTILINE)

if __name__ == '__main__':
   svn_repos = sys.argv[1:]
   revisions = {}
   while 1:
      for repo in svn_repos:
         # Get the status of the repo
         proc = subprocess.Popen(['svn', 'info', repo], stdout=subprocess.PIPE)
         raw_info = proc.stdout.read()
         parsed_info = re.findall(parse, raw_info)

         last_revision = int(parsed_info[4])
         # Store the revision if it hasn't already been stored
         try: revisions[repo]
         except: revisions[repo] = last_revision
         # Compare and notify of changes
         if last_revision > revisions[repo]:
            meshlib.send_plugin_result('Notice: New revision %s on %s' % (str(last_revision), repo), push_master)
            meshlib.send_plugin_result('-'*25 + ' Revision %s ' % str(last_revision) + '-'*25, push_master)
            proc = subprocess.Popen(['svn', 'diff', repo, '-r', '%s:%s' % (str(last_revision), revisions[repo])], stdout=subprocess.PIPE)
            meshlib.send_plugin_result(proc.stdout.read(), push_master)
            meshlib.send_plugin_result('-'*60, push_master)
            revisions[repo] = last_revision
      time.sleep(5)

class TestPlugin(unittest.TestCase):
   def test_00svn_exists(self):
      '''Check that SVN is installed'''
      import subprocess
      proc = subprocess.Popen(['svn'], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
      if proc.stdout.read() != "Type 'svn help' for usage.\n":
         self.fail('SVN is not installed')
