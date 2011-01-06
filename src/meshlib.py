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

import M2Crypto, os, Queue, subprocess, sys, tempfile
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

def get_os():
   return sys.platform

# For creating ZMQ URLs
def socket_url(transport):
   if transport == 'ipc':
      return "ipc:///" + tempfile.NamedTemporaryFile().name + '.ipc'
   else:
      raise("Invalid transport: " + str(transport))

def is_socket_url(url):
   if (url[:7] == 'ipc:///') and (url[-4:] == '.ipc'):
      return True
   return False

# For plugins to send events to master.py
def send_plugin_result(msg, socket):
   socket.send(msg)

#------------------------------------------------------------------------------
# Encryption stuff

def encrypt(data, cert):
   "Encrypt a string using a cert"
   pubkey = cert.get_pubkey().get_rsa()
   return pubkey.public_encrypt(data, M2Crypto.RSA.pkcs1_padding).encode('base64')

def decrypt(data, key):
   "Decrypt an encrypted string using a private key"
   return key.private_decrypt(data.decode('base64'), M2Crypto.RSA.pkcs1_padding)

# --- verify_cert functions ---

# Helper stuff for verify_cert_m2crypto
global _verify_queue; _verify_queue = Queue.Queue()
def _callback(ok, store):
   global _verify_queue
   if ok:
      _verify_queue.put(True)
   else:
      _verify_queue.put(False)

# A fast, but complicated implementation
def verify_cert_m2crypto(cafile, certfile):
   global ca_store_dict, _verify_queue
   # Cache the ca_store in global scope for performance reasons.
   if not 'ca_store_dict' in globals():
      ca_store_dict = {}
   if not ca_store_dict.has_key(cafile):
      ca_store = M2Crypto.X509.X509_Store()
      ca_store.add_x509(M2Crypto.X509.load_cert(cafile))
      ca_store.set_verify_callback(_callback)
      ca_store_dict[cafile] = ca_store      # Cache it!
   cert = M2Crypto.X509.load_cert(certfile)
   # Instead of returning a useful value, verify_cert() launches a callback to
   # the appropriately named "_callback()"
   ca_store_dict[cafile].verify_cert(cert)  # Pull the ca_store from the cache.
   # _callback() has been called now, so...
   return _verify_queue.get()

# A slow, but simple implementation
def verify_cert_cli(cafile, certfile):
   command = ('/usr/bin/env', 'openssl', 'verify', '-CAfile', cafile, certfile)
   proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   stdout, stderr = proc.communicate()
   if (stderr == "") and (stdout.strip() == "%s: OK" % certfile):
      return True
   return False

def verify_cert(cafile, certfile):
   """
   cafile   = Path to file containing CA certificate
   certfile = Path to file containing certificate

   Returns True if the certificate has been signed by the CA, False otherwise.
   Paths may be absolute or relative.
   """
   if 'verify_cert' in dir(M2Crypto.X509.X509_Store):
      # Preferred - do cert verification with M2Crypto - should perform faster
      return verify_cert_m2crypto(cafile, certfile)
   else:
      # M2Crypto <= 0.20.2 (unpatched) has no verify_cert(), so we punt and do 
      # cert verification by calling a subprocess to "openssl verify"
      return verify_cert_cli(cafile, certfile)

# --- end verify_cert functions ---
