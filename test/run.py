#!/usr/bin/env python

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

import glob, os, optparse, sys, subprocess, time, unittest
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
      source_files = glob.glob(os.path.join(project_root_dir, 'test', '*.py')) + glob.glob(os.path.join(project_root_dir, 'src', '*.py'))
      for fname in source_files:
         header = open(os.path.join(project_root_dir, fname), 'r').read(1024)
         if not "# This file is part of Mesh." in header:
            self.fail("The source file %s has a malformed or missing GPL header." % fname)

class Test02Syntax(unittest.TestCase):
   def test_00banner(self):
      "[SYNTAX TESTS]"

   def test_03main(self):
      "Can import the main mesh file"
      global project_root_dir
      sys.path.append(os.path.join(project_root_dir, 'src'))
      import mesh

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

class Test03crypto(unittest.TestCase):
   def setUp(self):
      import M2Crypto
      self.alice_key  = M2Crypto.RSA.load_key(os.path.join(project_root_dir, 'test', 'certs', 'alice.key'))
      self.alice_cert = M2Crypto.X509.load_cert(os.path.join(project_root_dir, 'test', 'certs', 'alice.cert'))
      self.bob_key    = M2Crypto.RSA.load_key(os.path.join(project_root_dir, 'test', 'certs', 'bob.key'))
      self.bob_cert   = M2Crypto.X509.load_cert(os.path.join(project_root_dir, 'test', 'certs', 'bob.cert'))
      self.ca_cert    = M2Crypto.X509.load_cert(os.path.join(project_root_dir, 'test', 'certs', 'test-ca-cert.pem'))

   def test_00banner(self):
      "[CRYPTOGRAPHY TESTS]"

   def test_01m2verifycert(self):
      "(w/M2Crytpo [optional]) SSL certificates signed by the CA get verified correctly"
      import communicator
      global project_root_dir
      # This certificate should be valid
      if not communicator.verify_cert_m2crypto(cafile=os.path.join(project_root_dir, 'test', 'certs', 'test-ca-cert.pem'), certfile=os.path.join(project_root_dir, 'test', 'certs', 'alice.cert')):
         self.fail("A certificate that should be valid could not be verified.")

   def test_02m2verifycert_fail(self):
      "(w/M2Crypto [optional]) Self-signed SSL certificates do not get verified"
      import communicator
      global project_root_dir
      # This certificate should not be valid
      if communicator.verify_cert_m2crypto(cafile=os.path.join(project_root_dir, 'test', 'certs', 'test-ca-cert.pem'), certfile=os.path.join(project_root_dir, 'test', 'certs', 'test-self-sign.cert')):
         self.fail("A certificate that should not be valid was verified.")

   def test_03cliverifycert(self):
      "(w/CLI) SSL certificates signed by the CA get verified correctly"
      import communicator
      global project_root_dir
      # This certificate should be valid
      if not communicator.verify_cert_cli(cafile=os.path.join(project_root_dir, 'test', 'certs', 'test-ca-cert.pem'), certfile=os.path.join(project_root_dir, 'test', 'certs', 'alice.cert')):
         self.fail("A certificate that should be valid could not be verified.  Note that you can ignore this failure if the same test via the M2Crypto method succeeded.")

   def test_04cliverifycert_fail(self):
      "(w/CLI) Self-signed SSL certificates do not get verified"
      import communicator
      global project_root_dir
      # This certificate should not be valid
      if communicator.verify_cert_cli(cafile=os.path.join(project_root_dir, 'test', 'certs', 'test-ca-cert.pem'), certfile=os.path.join(project_root_dir, 'test', 'certs', 'test-self-sign.cert')):
         self.fail("A certificate that should not be valid was verified.  Note that you can ignore this failure if the same test via the M2Crypto method succeeded.")

   def test_06encrypt(self):
      "Encrypting a string using a public key seems to work"
      import communicator, M2Crypto, os
      global project_root_dir
      data = 'Confidential data!'
      cryptogram = communicator.encrypt(data, self.alice_cert)
      if cryptogram == data:
         self.fail('Encryption failed spectacularly')

   def test_09decrypt_known(self):
      "Decrypt a known pre-encrypted string"
      import communicator, M2Crypto, os
      global project_root_dir
      cryptogram = """bvzkTmVVWmLfw6lvJtdrXIaXFTHoI8U+AWE906c9FC4ca7dfDiLB5TOOxhy6thDkhUw+J9AnrEoh
FFsRRoGACYRufjm84bBDqOHMkK0rjyRFvU2uttphOTjdgqHPZJnA7iWrV7mHTBHogiaM6MpJWLQO
uNSdEHxKxqpjg9BR1xj/cYm+iqD0OFfONz7BqFgao3NDTg4a5qpS8i9m4mqFcIuAIRkZG2mC+uBN
h3JvaGQ7Opua72ninJI79Hr2X2VWBXtA4eOQM1BsxxbHWxiLspHplStM34zvXkaUgwUdvHZjvwo5
Tp7tERNH08s4Wb7hvIj6p/EloWtb/CA01EfQwA==
"""
      message = communicator.decrypt(cryptogram, self.alice_key)
      if message != 'Confidential data!':
         self.fail('Failed to decrypt an encrypted string.')

   def test_12encrypt_decrypt(self):
      "Encrypt and then decrypt a random string"
      import communicator, M2Crypto, os, random, string
      # Generate a random string of 32 letters and numbers
      message = ''.join([random.choice(string.ascii_letters + string.digits) for x in range(32)])
      cryptogram = communicator.encrypt(message, self.bob_cert)
      decrypted_message = communicator.decrypt(cryptogram, self.bob_key)
      if message != decrypted_message:
         self.fail('Input string came back differently when decrypted: "%s" != "%s"' % (message, decrypted_message))
      
class Test04ssh(unittest.TestCase):
   def test_00banner(self):
      "[SSH TESTS]"

   def test_01sshisrunning(self):
      "Check if sshd is running"
      import subprocess
      possible_ssh_names = ['/usr/bin/ssh-agent -l', '/usr/sbin/sshd']
      # Get process list, pull only those with ssh
      proc1 = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
      proc2 = subprocess.Popen(['grep', 'ssh'], stdin=proc1.stdout, stdout=subprocess.PIPE) 
      # Run through each line searching for any of the possible names
      # If a name is found, sshd is running
      for line in proc2.stdout.readlines():
         for name in possible_ssh_names:
            if name in line:return True
      self.fail('No sshd process was found.')

   def test_03sshlogexists(self):
      "Check if the ssh log file exists and is readable"
      import os.path
      log_locations = ['/var/log/secure.log', '/var/log/secure']
      # Check if either log file exists
      for location in log_locations:
         if os.path.isfile(location):
            try:
               open(location).read()
               return True
            except:
               self.fail('SSH log file "%s" is not readable' % (location))
      self.fail('No ssh log file found!')

   def test_04asterisklogexists(self):
      "Check if asterisk log file exists and is readable"
      import os.path
      location = '/var/log/asterisk/messages'
      if os.path.isfile(location):
         try:
            open(location).read()
            return True
         except:
            self.fail('SSH log file "%s" is not readable' % (location))
      self.fail('No ssh log file found!')

if __name__ == '__main__':
   # Parse command-line arguments
   parser = optparse.OptionParser()
   parser.add_option('-a', '--test-all',     help='Test everything.',               action='store_true', dest='test_all', default=False)
   parser.add_option('-c', '--test-core',    help='(DEFAULT) Test mesh core only.', action='store_true', dest='test_core', default=False)
   parser.add_option('-p', '--test-plugins', help='Test all plugins.',              action='store_true', dest='test_plugins', default=False)
   parser.add_option('-t', '--test-plugin',  help='Test a specific plugin only.',   action='store', dest='test_plugin', default='')
   parser.add_option('-v', '--verbose',      help='Verbose output',                 action='store_true', dest='verbose', default=False)
   (options, args) = parser.parse_args()

   # Set verbosity
   if options.verbose:
      verbosity = 2
   else:
      verbosity = 1

   # Run selected unit tests
   suite_list = []
   if options.test_all or options.test_core:
      pass                      # /// FINISH THIS!!!
#       for item in globals():
#          if item.startswith('Test'):
#             suite_list.append(unittest.loadTestsFromTestCase(
   if options.test_plugins:
      for plugin in glob.glob(os.path.join(project_root_dir, 'src', 'p_*')):
         print plugin
         module_to_test = __import__(plugin)
         suite = unittest.TestLoader().loadTestsFromModule(module_to_test)
         unittest.TextTestRunner(verbosity=verbosity).run(suite)         
   elif options.test_plugin:
      module_to_test = __import__(options.test_plugin)
      suite = unittest.TestLoader().loadTestsFromModule(module_to_test)
      unittest.TextTestRunner(verbosity=verbosity).run(suite)
   
