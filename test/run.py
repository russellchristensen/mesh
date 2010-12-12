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

import glob, os, unittest, sys, subprocess, time
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

class Test00Prerequisites(unittest.TestCase):
   def setUp(self):
      pass

   def tearDown(self):
      pass

   def test_00banner(self):
      "STARTING PREREQUISITE TESTS"

   def test_01os(self):
      "Supported OS?"
      self.assertTrue(sys.platform in ['darwin'])

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
      supported_version = version.LooseVersion('2.0.9')
      this_version = version.LooseVersion(zmq.__version__)
      self.assertTrue(this_version >= supported_version)


global project_root_dir; project_root_dir = None ; # Gotta be a way better than a global...

class Test01Code(unittest.TestCase):
   def setUp(self):
      pass

   def tearDown(self):
      pass

   def test_00banner(self):
      "STARTING CODE TESTS"

   def test_01projectrootdir(self):
      "Can find the project root directory"
      global project_root_dir
      curr_root_dir = os.getcwd()
      while not project_root_dir:
         curr_root_dir, last_element = os.path.split(curr_root_dir)
         if last_element == 'mesh':
            project_root_dir = os.path.join(curr_root_dir, 'mesh')
         self.assertTrue(last_element) # Once we've made it down to the root and not found mesh, it's time to fail
      # Found the project root directory!  Make it available for the rest of the tests...
      sys.path.append(os.path.join(project_root_dir, 'src'))

   def test_03license(self):
      "GPL 3 Compliance"
      global project_root_dir
      # Iterate through the python files and check for compliance
      source_files = glob.glob('test/*.py') + glob.glob('src/*.py')
      for fname in source_files:
         header = open(os.path.join(project_root_dir, fname), 'r').read(1024)
         if not "# This file is part of Mesh." in header:
            self.fail("The source file %s has a malformed or missing GPL header." % fname)

class Test02Syntax(unittest.TestCase):
   def test_00banner(self):
      "STARTING SYNTAX TESTS"

   def test_03main(self):
      "Can import the main mesh file"
      global project_root_dir
      sys.path.append(os.path.join(project_root_dir, 'src'))
      import mesh

class Test02zmq(unittest.TestCase):
   def test_00pubsub(self):
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

   def test_00verifycert(self):
      "SSL certificates signed by the CA get verified correctly"
      import communicator
      global project_root_dir
      # This certificate should be valid
      if not communicator.verify_cert(cafile=os.path.join(project_root_dir, 'test', 'certs', 'test-ca-cert.pem'), certfile=os.path.join(project_root_dir, 'test', 'certs', 'alice.cert')):
         self.fail("A certificate that should be valid could not be verified.")

   def test_03verifycert_fail(self):
      "SSL certificates not signed by the CA do not get verified"
      import communicator
      global project_root_dir
      # This certificate should not be valid
      if communicator.verify_cert(cafile=os.path.join(project_root_dir, 'test', 'certs', 'test-ca-cert.pem'), certfile=os.path.join(project_root_dir, 'test', 'certs', 'test-self-sign.cert')):
         self.fail("A certificate that should not be valid was verified.")

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
      

if __name__ == '__main__':
   unittest.main()
