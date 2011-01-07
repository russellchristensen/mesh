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

import subprocess, re, time
from datetime import datetime

supported_os = ['sunos5', 'darwin']

def iterate_list(l):
   'Iterate through a list, yield a tuple of "count, item"'
   c = 0
   while c < len(l):
      yield c, l[c]
      c += 1

if __name__ == '__main__':
   protected_users = set(['root', 'svn', 'reboot', 'shutdown', 'wtmp'])

   parse_last = re.compile(r'^(\w+).+(\w{3} \w{3} (?: )?\d+ \d+:\d+)', re.MULTILINE)
   parse_dscacheutil = re.compile(r'name: (.+)[\r\n]password: (.+)[\r\n]gid: (.+)[\r\n]users: (.+)')

   # Get login history
   proc = subprocess.Popen(['last'], stdout=subprocess.PIPE)
   output = proc.stdout.read()
   proc.kill()

   # Get existing users
   existing_users = set()
   # Get OpenSolaris users
   if meshlib.get_os() == 'sunos5':
      for entry in open('/etc/shadow', 'r').read().split('\n'):
              username = entry.split(':')[0]
              if username: existing_users.add(username)
   # Get Mac OSX users
   elif meshlib.get_os() == 'darwin':
      # Mac only variables
      mac_user_groups = set(['_appserverusr', '_appserveradm', '_lpadmin'])
      proc = subprocess.Popen(['dscacheutil',  '-q', 'group'], stdout=subprocess.PIPE)

      # Add unknown users
      for group, password, gid, users in re.findall(parse_dscacheutil, proc.stdout.read()):
         if group in mac_user_groups:
            users = users.split(' ')
            for user in users:
               if user: existing_users.add(user)
      proc.kill()
   else:
      error = 'Error: Your operating system is not supported!'
      meshlib.send_plugin_result(error, push_master)
      print error

   # Parse and store "last" entries
   last_users = {}
   oldest_entry = datetime.now()
   for user, d in re.findall(parse_last, output):
      # Convert date to a usable format, using the current year
      d = datetime.strptime(d.split('-')[0], '%a %b %d %H:%M').replace(year=datetime.now().year)
      # If the month is from the future; decrement the year
      if d.month > datetime.now().month:
          d = d.replace(year=datetime.now().year-1)
      # Make sure the user is in last_users
      try: last_users[user]
      except: last_users[user] = datetime.min
      # If entry is newer, save it
      if d > last_users[user]:
         last_users[user] = d
      # If entry is oldest, store it
      if d < oldest_entry:
         oldest_entry = d

   # Bubble sort the user's by their login times
   sorted_users = list(set(last_users.keys()).difference(protected_users))
   error = True
   while error:
      error = False
      for count, user in iterate_list(sorted_users):
         try:
            # Compare current and next user
            if last_users[user] > last_users[sorted_users[count+1]]:
               error = True
               sorted_users.append(sorted_users[count])
               sorted_users.pop(count)
         except: pass

   # Show user's who aren't official in the system, or haven't logged in within the history of "last"
   for user in sorted(set(existing_users).difference(set(last_users))):
      notice = 'User: %s is not an existing user and has not logged in in over %s days.' % (user, str((datetime.now() - oldest_entry).days))
      meshlib.send_plugin_result(notice, push_master)
      print notice
   # Show the latest login for each user, organized from oldest to newest
   for user in sorted_users:
      notice = 'User: %s Last Login: %s' % (user, last_users[user])
      meshlib.send_plugin_result(notice, push_master)
      print notice

class TestPlugin(unittest.TestCase):
   def test_00if_mac(self):
      '''Mac OS has needed tools'''
      import meshlib, subprocess, sys
      if meshlib.get_os() == 'darwin':
         try:
            proc = subprocess.Popen(['dscacheutil'], stdout=subprocess.PIPE)
            proc.stdout.read()
            proc.kill()
         except:
            self.fail('Could not call "dscacheutil"')

   def test_01if_sun(self):
      '''Solaris has needed tools'''
      import meshlib, os.path, sys
      if meshlib.get_os() == 'sunos5' and not os.path.isfile('/etc/shadow'):
         self.fail("No shadow file to pull users's from!")

   def test_01last(self):
      '''"last" command is in the format expected.'''
      import subprocess
      proc = subprocess.Popen(['last'], stdout=subprocess.PIPE)
      last_content = proc.stdout.read()
      parse_last = re.compile(r'^(\w+) +([\w\/]+) +([\d\.:]+)? +([\w :\-]+)(?: - )? +\((.+)\)', re.MULTILINE)
      if len(re.findall(parse_last, last_content)) == 1:
         self.fail('"last" output was not as expected')
