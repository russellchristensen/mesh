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

import subprocess

def verify_cert(cafile, certfile):
   command = ('/usr/bin/env', 'openssl', 'verify', '-CAfile', cafile, certfile)
   proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   stdout, stderr = proc.communicate()
   if (stderr == "") and (stdout.strip() == "%s: OK" % certfile):
      return True
   return False
   
def encrypt_with_cert(pkey, toencrypt):
   "Encrypt a string using a cert"
   import M2Crypto as m2
   pubkey = m2.X509.load_cert(pkey).get_pubkey().get_rsa()
   return pubkey.public_encrypt(toencrypt, m2.RSA.pkcs1_padding)

def decrypt_with_private_key(key, encrypted):
   "Decrypt an encrypted string using a private key"
   import M2Crypto as m2
   private = m2.RSA.load_key(key)
   return private.private_decrypt(encrypted, m2.RSA.pkcs1_padding)
