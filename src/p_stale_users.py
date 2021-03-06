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

plugin_name = 'p_stale_users'
supported_os = ['sunos5', 'darwin']
description = """
Detect when a user has not logged in for a very long time.

Threshold: Users that haven't logged in in a month
"""
threshold = meshlib.get_config(plugin_name, 'threshold', '-30')

import subprocess, re, time, datetime

def configured():
   import os
   if not os.path.exists('/bin/last') or not os.access('/bin/last', os.X_OK): return False
   try: int(threshold)
   except: return False
   return True


def get_sun_users():
   existing_users = set()
   for entry in open('/etc/shadow', 'r').read().split('\n'):
     username = entry.split(':')[0]
     if username: existing_users.add(username)
   return existing_users

def get_mac_users():
   existing_users = set()
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
   return existing_users


if __name__ == '__main__':
   protected_users = set(['root', 'svn', 'reboot', 'shutdown', 'wtmp'])

   parse_last = re.compile(r'^(\w+).+(\w{3} \w{3} (?: )?\d+ \d+:\d+)', re.MULTILINE)
   parse_dscacheutil = re.compile(r'name: (.+)[\r\n]password: (.+)[\r\n]gid: (.+)[\r\n]users: (.+)')

   # Get login history
   proc = subprocess.Popen(['last'], stdout=subprocess.PIPE)
   output = proc.stdout.read()
   proc.kill()

   # Get system users
   if meshlib.get_os() == 'sunos5':
      existing_users = get_sun_users()
   elif meshlib.get_os() == 'darwin':
      existing_users = get_mac_users()
   else:
      error = 'Error: Your operating system is not supported!'
      meshlib.send_plugin_result(error, push_master)

   # Parse and store "last" entries
   last_users = {}
   oldest_entry = datetime.datetime.now()
   for user, d in re.findall(parse_last, output):
      # Convert date to a usable format, using the current year
      d = datetime.datetime.strptime(d.split('-')[0], '%a %b %d %H:%M').replace(year=datetime.datetime.now().year)
      # If the month is from the future; decrement the year
      if d.month > datetime.datetime.now().month:
          d = d.replace(year=datetime.datetime.now().year-1)
      # Make sure the user is in last_users
      try: last_users[user]
      except: last_users[user] = datetime.datetime.min
      # If entry is newer, save it
      if d > last_users[user]:
         last_users[user] = d
      # If entry is oldest, store it
      if d < oldest_entry:
         oldest_entry = d

   # Show user's who aren't official in the system, or haven't logged in within the history of "last"
   for user in sorted(set(existing_users).difference(set(last_users))):
      notice = 'User: %s is not an existing user and has not logged in in over %s days.' % (user, str((datetime.datetime.now() - oldest_entry).days))
      meshlib.send_plugin_result(notice, push_master)
   # Show the latest login for each user, organized from oldest to newest
   for user in sorted(last_users, key=lambda x: last_users[x]):
      if user in protected_users or last_users[user] > (datetime.datetime.now() + datetime.timedelta(days=int(threshold))): continue
      notice = 'User: %s Last Login: %s' % (user, last_users[user])
      meshlib.send_plugin_result(notice, push_master)

# /// After splitting special-cased functionality into functions, unit test the functions!
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

