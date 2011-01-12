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
import subprocess, re

# Remove the OSs your plugin doesn't support.
# Use meshlib.get_os() if you need to know what OS you're actually on.
supported_os = ['linux2']
plugin_name = 'p_svn'
parse = re.compile(r'^[\w ]+: (.+)[\n\r]?', re.MULTILINE)

if __name__ == '__main__':
   # Connect a PUSH socket to master.py
   master_socket_url = sys.argv[1]
   zmq_context       = zmq.Context()
   push_master       = zmq_context.socket(zmq.PUSH)
   push_master.connect(master_socket_url)

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
            print 'Notice: New revision %s on %s' % (str(last_revision), repo)
            print '-'*25 + ' Revision %s ' % str(last_revision) + '-'*25
            proc = subprocess.Popen(['svn', 'diff', repo, '-r', '%s:%s' % (str(last_revision), revisions[repo])], stdout=subprocess.PIPE)
            print proc.stdout.read()
            print '-'*60
            revisions[repo] = last_revision
      time.sleep(5)

class TestPlugin(unittest.TestCase):
   def test_00svn_exists(self):
      import subprocess
      proc = subprocess.Popen(['svn'], stdout=subprocess.PIPE)
      if proc.stdout.read() != "Type 'svn help' for usage.":
         self.fail('SVN is not installed')
