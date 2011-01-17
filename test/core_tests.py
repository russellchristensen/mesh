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

import glob, os, sys, subprocess, time, unittest
from distutils import version

global gpl_header
gpl_header = """# This file is part of Mesh.

# Mesh is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Mesh is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Mesh.  If not, see <http://www.gnu.org/licenses/>."""

# We've got to find the root directory of the project to run tests!
global project_root_dir
project_root_dir = None
curr_root_dir = os.getcwd()
while not project_root_dir:
   curr_root_dir, last_element = os.path.split(curr_root_dir)
   if last_element == 'mesh':
      project_root_dir = os.path.join(curr_root_dir, 'mesh')
if not project_root_dir:
   print "Error, couldn't find the project root directory.  :-("
   sys.exit(1)

# Found the project root directory!  Make it available for the rest of the tests...
sys.path.append(os.path.join(project_root_dir, 'src'))
sys.path.append(os.path.join(project_root_dir, 'test'))

class Test00Dependencies(unittest.TestCase):
   def test_00banner(self):
      "[DEPENDENCY TESTS]"

   def test_01os(self):
      "Supported OS?"
      if sys.platform not in ['darwin', 'linux2']:
         self.fail("Unsupported OS: %s" % sys.platform)

   def test_03python_version(self):
      "Supported version of Python?"
      supported_version = version.StrictVersion('2.6')
      this_version = version.StrictVersion(str(sys.version_info[0]) + '.' + str(sys.version_info[1]))
      self.assertTrue(this_version >= supported_version)

   def test_09m2crypto(self):
      "Supported version of M2Crypto?"
      import M2Crypto
      supported_version = version.StrictVersion('0.20.2')
      this_version = version.StrictVersion(M2Crypto.version)
      self.assertTrue(this_version >= supported_version)

   def test_12zmq(self):
      "Supported version of ZeroMQ"
      import zmq
      supported_version = version.LooseVersion('2.0.10')
      this_version = version.LooseVersion(zmq.__version__)
      self.assertTrue(this_version >= supported_version)

   def test_15psutil(self):
      "Supported version of psutil"
      import psutil
      supported_version = version.StrictVersion('0.2.0')
      this_version = version.StrictVersion(".".join([str(x) for x in psutil.version_info]))
      self.assertTrue(this_version >= supported_version)

class Test01Code(unittest.TestCase):
   def test_00banner(self):
      "[CODE TESTS]"

   def test_03license(self):
      "GPL 3 Compliance"
      global project_root_dir
      # Iterate through the python files and check for compliance
      source_files = [os.path.join(project_root_dir, 'mesh')] + glob.glob(os.path.join(project_root_dir, 'test', '*.py')) + glob.glob(os.path.join(project_root_dir, 'src', '*.py'))
      failures = []
      for fname in source_files:
         header = open(os.path.join(project_root_dir, fname), 'r').read(1024)
         if not gpl_header in header:
            failures.append("The source file '%s' has a malformed or missing GPL header." % fname)
      if failures:
         self.fail('\n'+'\n'.join(failures))

class Test02Syntax(unittest.TestCase):
   def test_00banner(self):
      "[SYNTAX TESTS]"

   def test_03import(self):
      # /// need to try importing all the non-plugin files here
      pass
      
class Test02zmq(unittest.TestCase):
   def test_00banner(self):
      "[MESSAGING TESTS]"

   def test_01pubsub(self):
      "ZMQ Publish/Subscribe pattern works over ipc"
      global project_root_dir
      
      # Subscriber subprocess
      sub_command = ('/usr/bin/env', 'python', os.path.join(project_root_dir, 'test/zmq_sub.py'),)
      sub_process = subprocess.Popen(sub_command)

      # Publisher subprocess
      pub_command = ('/usr/bin/env', 'python', os.path.join(project_root_dir, 'test/zmq_pub.py'),)
      pub_process = subprocess.Popen(pub_command)

      # Watch only the subscriber,  publisher obviously works if the subscriber successfully gets the message
      sub_retcode = sub_process.poll()
      for i in range(100):
         if (sub_retcode != None):
            break
         time.sleep(.05)
         sub_retcode = sub_process.poll()
      sub_retcode = sub_process.poll()
      if sub_retcode == 0:
         return
      else:
         self.fail("ZMQ Publish/Subscribe pattern failed with retcodes %s/%s" % (str(sub_retcode), str(pub_retcode)))

   def test_03reqrep(self):
      "ZMQ Request/Reply pattern works over ipc"
      global project_root_dir

      # Reply subprocess
      rep_command = ('/usr/bin/env', 'python', os.path.join(project_root_dir, 'test/zmq_rep.py'),)
      rep_process = subprocess.Popen(rep_command)
      
      # Request subprocess
      req_command = ('/usr/bin/env', 'python', os.path.join(project_root_dir, 'test/zmq_req.py'),)
      req_process = subprocess.Popen(req_command)

      # Make sure both process exit successfully
      rep_retcode = rep_process.poll()
      req_retcode = req_process.poll()
      while (rep_retcode == None) or (req_retcode == None):
         time.sleep(.05)
         rep_retcode = rep_process.poll()
         req_retcode = req_process.poll()
      if (rep_retcode == 0) and (req_retcode == 0):
         return
      else:
         self.fail("ZMQ Request/Reply pattern failed with with retcodes %s/%s" % (str(rep_retcode), str(req_retcode)))

class Test03meshlib(unittest.TestCase):
   def setUp(self):
      import M2Crypto
      self.alice_key  = M2Crypto.RSA.load_key(os.path.join(project_root_dir, 'test', 'certs', 'alice.key'))
      self.alice_cert = M2Crypto.X509.load_cert(os.path.join(project_root_dir, 'test', 'certs', 'alice.cert'))
      self.bob_key    = M2Crypto.RSA.load_key(os.path.join(project_root_dir, 'test', 'certs', 'bob.key'))
      self.bob_cert   = M2Crypto.X509.load_cert(os.path.join(project_root_dir, 'test', 'certs', 'bob.cert'))
      self.ca_cert    = M2Crypto.X509.load_cert(os.path.join(project_root_dir, 'test', 'certs', 'test-ca-cert.pem'))

   def test_00banner(self):
      "[MESHLIB]"
      import meshlib

   def test_01m2verifycert(self):
      "(w/M2Crytpo [optional]) SSL certificates signed by the CA get verified correctly"
      import meshlib
      global project_root_dir
      # This certificate should be valid
      if not meshlib.verify_cert_m2crypto(cafile=os.path.join(project_root_dir, 'test', 'certs', 'test-ca-cert.pem'), certfile=os.path.join(project_root_dir, 'test', 'certs', 'alice.cert')):
         self.fail("A certificate that should be valid could not be verified.")

   def test_02m2verifycert_fail(self):
      "(w/M2Crypto [optional]) Self-signed SSL certificates do not get verified"
      import meshlib
      global project_root_dir
      # This certificate should not be valid
      if meshlib.verify_cert_m2crypto(cafile=os.path.join(project_root_dir, 'test', 'certs', 'test-ca-cert.pem'), certfile=os.path.join(project_root_dir, 'test', 'certs', 'test-self-sign.cert')):
         self.fail("A certificate that should not be valid was verified.")

   def test_03cliverifycert(self):
      "(w/CLI) SSL certificates signed by the CA get verified correctly"
      import meshlib
      global project_root_dir
      # This certificate should be valid
      if not meshlib.verify_cert_cli(cafile=os.path.join(project_root_dir, 'test', 'certs', 'test-ca-cert.pem'), certfile=os.path.join(project_root_dir, 'test', 'certs', 'alice.cert')):
         self.fail("A certificate that should be valid could not be verified.  Note that you can ignore this failure if the same test via the M2Crypto method succeeded.")

   def test_04cliverifycert_fail(self):
      "(w/CLI) Self-signed SSL certificates do not get verified"
      import meshlib
      global project_root_dir
      # This certificate should not be valid
      if meshlib.verify_cert_cli(cafile=os.path.join(project_root_dir, 'test', 'certs', 'test-ca-cert.pem'), certfile=os.path.join(project_root_dir, 'test', 'certs', 'test-self-sign.cert')):
         self.fail("A certificate that should not be valid was verified.  Note that you can ignore this failure if the same test via the M2Crypto method succeeded.")

   def test_06encrypt(self):
      "Encrypting a string using a public key seems to work"
      import meshlib, M2Crypto, os
      global project_root_dir
      data = 'Confidential data!'
      cryptogram = meshlib.encrypt(data, self.alice_cert)
      if cryptogram == data:
         self.fail('Encryption failed spectacularly')

   def test_09decrypt_known(self):
      "Decrypt a known pre-encrypted string"
      import meshlib, M2Crypto, os
      global project_root_dir
      cryptogram = """bvzkTmVVWmLfw6lvJtdrXIaXFTHoI8U+AWE906c9FC4ca7dfDiLB5TOOxhy6thDkhUw+J9AnrEoh
FFsRRoGACYRufjm84bBDqOHMkK0rjyRFvU2uttphOTjdgqHPZJnA7iWrV7mHTBHogiaM6MpJWLQO
uNSdEHxKxqpjg9BR1xj/cYm+iqD0OFfONz7BqFgao3NDTg4a5qpS8i9m4mqFcIuAIRkZG2mC+uBN
h3JvaGQ7Opua72ninJI79Hr2X2VWBXtA4eOQM1BsxxbHWxiLspHplStM34zvXkaUgwUdvHZjvwo5
Tp7tERNH08s4Wb7hvIj6p/EloWtb/CA01EfQwA==
"""
      message = meshlib.decrypt(cryptogram, self.alice_key)
      if message != 'Confidential data!':
         self.fail('Failed to decrypt an encrypted string.')

   def test_12encrypt_decrypt(self):
      "Encrypt and then decrypt a random string"
      import meshlib, M2Crypto, os, random, string
      # Generate a random string of 32 letters and numbers
      message = ''.join([random.choice(string.ascii_letters + string.digits) for x in range(32)])
      cryptogram = meshlib.encrypt(message, self.bob_cert)
      decrypted_message = meshlib.decrypt(cryptogram, self.bob_key)
      if message != decrypted_message:
         self.fail('Input string came back differently when decrypted: "%s" != "%s"' % (message, decrypted_message))

   def test_15socket_url(self):
      "Function socket_url works"
      import meshlib, zmq
      zmq_context = zmq.Context()
      push = zmq_context.socket(zmq.PUSH)
      pull = zmq_context.socket(zmq.PULL)
      url = meshlib.socket_url('ipc')
      push.connect(url)
      pull.bind(url)
      msg = "This is a test message"
      push.send(msg)
      output = pull.recv()
      if msg != output:
         self.fail("We weren't able to send/receive a message with a url created by socket_url.")

   def test_18is_socket_url(self):
      "Function is_socket_url works"
      import meshlib
      for i in xrange(10):
         url = meshlib.socket_url('ipc')
         if not meshlib.is_socket_url(url):
            self.fail("is_socket_url failed on '%s' created by socket_url('ipc')" % url)
      url = 'ipc:///tmp/goodurl.ipc'
      if not meshlib.is_socket_url(url):
         self.fail("is_socket_url failed on a known good url '%s'" % url)
      badurl = 'paosidfsadfsdfhncv'
      if meshlib.is_socket_url(badurl):
         self.fail("is_socket_url didn't detect bad url %s" % badurl)

   def test_21load_config(self):
      "Function load_config() works with a non-existent config file (defaults will be used)"
      import meshlib
      meshlib.load_config('/tmp/does_not_exist.conf')

   def test_24load_config(self):
      "Function load_config() works with default config file (defaults will be used if it doesn't exist)"
      import meshlib
      meshlib.load_config()
      
   def test_27load_config(self):
      "Function load_config() works with a real custom-provided config file"
      global project_root_dir
      import meshlib
      meshlib.load_config(os.path.join(project_root_dir, 'test', 'mesh_b.conf'))
      self.assertTrue(meshlib.get_config(None, 'port_assigner_port', None) == '5200')

   def test_30get_config(self):
      "Function get_config() works properly"
      import meshlib
      meshlib.load_config(os.path.join(project_root_dir, 'test', 'mesh_b.conf'))
      # Global options that aren't there return the default value
      self.assertTrue(meshlib.get_config(None, 'fake_option', 'the default value') == 'the default value')
      # Global options that are there return the real value
      self.assertTrue(meshlib.get_config(None, 'next_push_port', None) == '5205')
      # Plugin options that aren't there return the default value
      self.assertTrue(meshlib.get_config('fake_plugin', 'another_fake_option', 'the default value') == 'the default value')
      # Plugin options that are there return the real value
      self.assertTrue(meshlib.get_config('p_template', 'banana_threshold', None) == '1')
      # Plugin option overrides global options
      self.assertTrue(meshlib.get_config('p_template', 'duplicate_option', None) == 'plugin_value')
      # Missing plugin option falls back to global option
      self.assertTrue(meshlib.get_config('p_template', 'inbound_pull_proxy_port', None) == '5201')

   def test_33get_identifer(self):
      "Function get_identifier() returns something."
      import meshlib
      meshlib.load_config()
      self.assertTrue(meshlib.get_identifier())

class Test04master(unittest.TestCase):
   def setUp(self):
      pass

   def test_00banner(self):
      "[MASTER]"
      import master

   def test_06create_zmq_context(self):
      "ZMQ context was created"
      import master, zmq
      self.assertTrue(type(master.zmq_context) == zmq.core.context.Context)

   def test_09create_push_communicator(self):
      "Function create_push_communicator() works"
      import master, zmq
      master.create_push_communicator()
      if type(master.push_communicator) != zmq.core.socket.Socket:
         self.fail("push_communicator socket is wrong type: %s" % str(type(master.push_communicator)))

   def test_12create_pull(self):
      "Function create_pull() works"
      import master, zmq
      master.create_pull()
      if type(master.pull) != zmq.core.socket.Socket:
         self.fail("pull socket is wrong type: %s" % str(type(master.pull)))

#    def test_15start_port_assigner(self):
#       "Function start_port_assigner works"
#       import master
#       master.start_port_assigner()

#    def test_18start_communicator(self):
#       "Function start_communicator works"
#       import master
#       master.start_communicator()

#    def test_21start_inbound_pull_proxy(self):
#       "Function start_inbound_pull_proxy works"
#       import master
#       master.start_inbound_pull_proxy()

#    def test_24start_outbound_pull_proxy(self):
#       "Function start_outbound_pull_proxy works"
#       import master
#       master.start_outbound_pull_proxy('test')

#    def test_27process_message(self):
#       "Function process_message works"
#       import master, sys, StringIO
#       fake_stdout = StringIO.StringIO()
#       real_stdout = sys.stdout
#       sys.stdout = fake_stdout
#       msg = "test message"
#       master.process_message(msg)
#       sys.stdout = real_stdout
#       if fake_stdout.getvalue() != ('Received: %s\n' % msg):
#          self.fail("Unexpected output by process_message()")

class Test05communicator(unittest.TestCase):
   def test_00banner(self):
      "[COMMUNICATOR]"
      import communicator

template_header = """
import meshlib, sys, time, unittest, zmq

if __name__ == '__main__':
   # Connect a PUSH socket to master.py
   master_socket_url = sys.argv[1]
   zmq_context       = zmq.Context()
   push_master       = zmq_context.socket(zmq.PUSH)
   push_master.connect(master_socket_url)"""

class Test06plugins(unittest.TestCase):
   def test_00banner(self):
      "[PLUGINS]"

   def test_02template_header(self):
      "All plugins have the template header"
      import glob
      global project_root_dir
      failures = []
      for plugin_file in glob.glob(os.path.join(project_root_dir, 'src', 'p_*py')):
         plugin = os.path.split(plugin_file)[1][:-3]
         plugin_contents = open(plugin_file).read()
         if template_header not in plugin_contents:
            failures.append("Plugin '%s' has a missing or malformed template section." % plugin)
      if failures:
         self.fail('\n'+'\n'.join(failures))

   def test_03supported_os(self):
      "All plugins define supported_os"
      import glob
      global project_root_dir
      failures = []
      for plugin_file in glob.glob(os.path.join(project_root_dir, 'src', 'p_*py')):
         plugin = os.path.split(plugin_file)[1][:-3]
         module = __import__(plugin)
         supported_os = getattr(module, 'supported_os', None)
         if supported_os == None:
            failures.append("Plugin '%s' does not define supported_os." % plugin)
         elif type(supported_os) != list:
            failures.append("Plugin '%s' defined supported_os as a '%s' instead of a list!" % (plugin, type(supported_os)))
      if failures:
         self.fail('\n'+'\n'.join(failures))
            
   def test_06description(self):
      "All plugins define a description with summary and threshold"
      import glob
      global project_root_dir
      failures = []
      for plugin_file in glob.glob(os.path.join(project_root_dir, 'src', 'p_*py')):
         plugin = os.path.split(plugin_file)[1][:-3]
         module = __import__(plugin)
         description = getattr(module, 'description', None)
         if description == None:
            failures.append("Plugin '%s' does not define description." % plugin)
            continue
         if type(description) != str:
            failures.append("Plugin '%s' defined description as a '%s' instead of a string!" % (plugin, type(description)))
            continue
         desc_lines = description.strip().split('\n')
         if len(desc_lines) > 1:
            if desc_lines[1].strip():
               failures.append("Plugin '%s' does not have an empty second line in the description." % plugin)
         if 'threshold' not in description.lower():
            failures.append("Plugin '%s' does not describe the threshold conditions" % plugin)
      if failures:
         self.fail('\n'+'\n'.join(failures))

   def test_09configured(self):
      "All plugins define a configured function"
      import glob
      global project_root_dir
      failures = []
      for plugin_file in glob.glob(os.path.join(project_root_dir, 'src', 'p_*py')):
         plugin = os.path.split(plugin_file)[1][:-3]
         module = __import__(plugin)
         configured = getattr(module, 'configured', None)
         if configured == None:
            failures.append("Plugin '%s' does not define configured." % plugin)
            continue
         if type(configured) != type(lambda x: x):
            failures.append("Plugin '%s' defined configured as a '%s' instead of a function!" % (plugin, type(configured)))
            continue
      if failures:
         self.fail('\n'+'\n'.join(failures))
