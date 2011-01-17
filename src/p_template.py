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

# //// Delete all comments that start with "////" from real plugins!

import meshlib, sys, time, unittest, zmq

if __name__ == '__main__':
   # Connect a PUSH socket to master.py
   master_socket_url = sys.argv[1]
   zmq_context       = zmq.Context()
   push_master       = zmq_context.socket(zmq.PUSH)
   push_master.connect(master_socket_url)

# //// Remove the OSs your plugin doesn't support.
# //// Use meshlib.get_os() if you need to know what OS you're actually on.
supported_os = ['darwin', 'linux2', 'freebsd8', 'sunos5']
# //// First line of description is 80-char or less summary.
# //// Second line is always blank.
# //// Then you define the threshold, and anything else you want to talk about.
description = """
Detect rogue bananas in ambient python strings.

Threshold: If more than banana_threshold bananas are encountered, then we create
           an event
"""
# //// Now get any config values you need
banana_threshold = int(meshlib.get_config('p_template', 'banana_threshold', '0'))

# //// You MUST define this function that tells whether or not you now have
#      enough configuration information to be able to run.
def configured():
   if type(banana_threshold) == int:
      return True
   return False

# //// Most "real" functionality should be functions, for easy unit testing.
def banana_detected(msg, threshold):
   if (type(msg) == str) and (msg.count('banana') > threshold):
      return True
   return False

# //// Your code must be wrapped in this 'if' statement.
if __name__ == '__main__':
   # //// You will typically wrap your functionality in an infinite loop.
   # //// master.py will send the plugin a kill signal when it wants it to stop.
   while 1:
      msg = "Templates love bananas"
      if banana_detected("Templates love bananas", banana_threshold):
         # Plugins communicate with master.py through meshlib.send_plugin_result()
         meshlib.send_plugin_result("Banana detected in the following message: %s" % msg, push_master)
      # This is just an example, so we'll fake events by pausing.  Real loops usually block in I/O of some type.
      time.sleep(1)

# //// Customized unit-testing of everything above.  It's common for unit tests to take _more_ code than the code they test.
# Unit Tests
class TestPlugin(unittest.TestCase):
   # First, test setup requirements (do files/commands/libraries exist, etc.)
   def test_00search_strings(self):
      """We can search strings."""
      self.assertTrue('substring' in 'this long string has a substring in it')
      
   # Next, test all functionality
   def test_03banana_detected(self):
      """We can detect a banana where it exists"""
      msg1 = "May I have a banana, please?"
      msg2 = "I love bananas"
      for item in [msg1, msg2]:
         if not banana_detected(item, banana_threshold):
            self.fail("Oh dear, we were unable to detect a banana in: '%s'" % item)

   def test_06banana_not_detected(self):
      """We don't find a banana where it doesn't exist"""
      not_even_a_string = 500
      msg = "What a lovely apple!"
      for item in [not_even_a_string, msg]:
         if banana_detected(item, banana_threshold):
            self.fail("Found a banana where none exists: %s" % str(item))
