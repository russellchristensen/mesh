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

import M2Crypto, os, Queue, re, smtplib, subprocess, sys, tempfile, zmq
import ConfigParser

#------------------------------------------------------------------------------
# CONSTANTS

release_version = '0.2alpha'

# Nodes with the same comm_version can talk to each other
comm_version = '1'

# COMM FORMATS - so the sender and receiver can use the same format
assigned_ports     = "assigned_ports:%(identifier)s:%(pull_port)s:%(push_port)s"
error              = "error:%(message)s"
request_ports      = "request_ports:%(identifier)s"
assigned_ports_pat = re.compile(r'^(?P<command>assigned_ports):(?P<pull_port>.*?):(?P<push_port>.*?)$')
error_pat          = re.compile(r'^(?P<command>error):(?P<message>.*?)$')
request_ports_pat  = re.compile(r'^(?P<command>request_ports):(?P<identifier>.*?)$')

port_assigner_patterns = [request_ports_pat]

# Where's that pesky etc directory?
etc_locations = {
   'darwin'   : '/usr/local/etc', # OS X
   'linux2'   : '/etc',           # Linux (w/2.x kernel)
   'freebsd8' : '/usr/local/etc', # FreeBSD 8.x
   'sunos5'   : '/etc',           # OpenSolaris
}

# Where's mesh!?
# We've got to find the root directory of the project to run tests!
global project_root_dir
project_root_dir = None
curr_root_dir = __file__
while not project_root_dir:
   curr_root_dir, last_element = os.path.split(curr_root_dir)
   if os.path.isfile(os.path.join(curr_root_dir, 'mesh')):
      project_root_dir = curr_root_dir
      break
   if not last_element:
      break
# If we didn't find it yet, perhaps we were imported from live python
if not project_root_dir:
   curr_root_dir = os.getcwd()
   while not project_root_dir:
      curr_root_dir, last_element = os.path.split(curr_root_dir)
      if os.path.isfile(os.path.join(curr_root_dir, 'mesh')):
         project_root_dir = curr_root_dir
         break
      if not last_element:
         break
if not project_root_dir:
   print "Error, couldn't find the project root directory.  :-("
   sys.exit(1)

# Used by the config functions later on
config_parser = None
config_file = None

#------------------------------------------------------------------------------
# CONFIGURATION FUNCTIONS

def get_os():
   "What OS are we on?  Used to find /etc, define plugin compatibility, etc."
   return sys.platform

def load_config(file_path = None):
   "Get the config file loaded"
   global config_parser
   global config_file
   config_parser = ConfigParser.ConfigParser()
   if file_path:
      config_file = file_path
   else:
      config_file = os.path.join(etc_locations[sys.platform],'mesh.conf')
   config_parser.read(config_file)      

def get_config(plugin, option, default):
   "Get a value from the config file (you should probably call load_config first)"
   global config_parser
   if not config_parser:
      load_config()
   # First try the plugin section if it was indicated
   if plugin:
      try:
         return config_parser.get(plugin, option)
      except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
         pass
   # Then fall back to the global section
   try:
      return config_parser.get('global', option)
   except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
      pass
   # Finally, fall back to the default
   return default

def get_identifier():
   "Return the unique identifier for this instance of mesh.  Currently, meshlib.load_config() must have been already called first."
   global config_parser
   if not config_parser:
      raise "Call meshlib.load_config() first."
   return "%s-%s" % (os.uname()[1], get_config(None, 'inbound_pull_proxy_port', '4201'))
   
def socket_url(transport):
   "For creating ZMQ URLs"
   if transport == 'ipc':
      return "ipc://" + tempfile.NamedTemporaryFile().name + '.ipc'
   else:
      raise("Invalid transport: " + str(transport))

def is_socket_url(url):
   if (url[:7] == 'ipc:///') and (url[-4:] == '.ipc'):
      return True
   return False

#------------------------------------------------------------------------------
# PLUGIN SUPPORT

def init_plugin(argv):
   """
We want plugin template to be as lean as possible, so most of the plugin
boilerplate stuff goes here.

argv -> sys.argv from the plugin.

Returns a tuple (zmq_context, push_master)
"""
   config_file       = sys.argv[1]
   load_config(config_file)
   master_socket_url = sys.argv[2]
   zmq_context       = zmq.Context()
   push_master       = zmq_context.socket(zmq.PUSH)
   push_master.connect(master_socket_url)
   return (zmq_context, push_master)

# For plugins to send events to master.py
def send_plugin_result(msg, socket):
   socket.send("plugin_result|"+msg)

def tail_iterator(filename):
   """
Returns an iterator for use in a for loop.

Plugins should use this instead of doing their own tailing.

Future versions of this function will (hopefully) use various
file-system monitoring libraries on various operating systems.

Example:
for line in meshlib.tail_iterator('/var/lob/messages'):
   # ...process line
"""
   # First choice, use a filesystem monitoring tool or framework...
   # ...none implemented
   # TO DO: Implement a REAL interrupt-driven blocking read on...
   #        Linux - http://pyinotify.sourceforge.net/
   #        Mac - http://pypi.python.org/pypi/pyobjc-framework-FSEvents/2.2b2
   #        Windows - http://timgolden.me.uk/python/win32%5Fhow%5Fdo%5Fi/watch%5Fdirectory%5Ffor%5Fchanges.html
   #  (all from http://stackoverflow.com/questions/1475950/tail-f-in-python-with-no-time-sleep )

   # Second choice, use tail if available
   try:
      p = subprocess.Popen(['tail']) # If it's not here, this throws an OSError exception.
      p.kill()
      tail_process = subprocess.Popen(["tail", "-n", "0", "-f", filename], stdout = subprocess.PIPE)
      line = True
      while line:
         line = tail_process.stdout.readline()
         yield line
   except OSError:
      # No tail
      pass

   # Third choice, imitate the behavior of tail in pure python
   import time
   fh = open(filename)
   fh.seek(0,2)
   while True:
      line = fh.readline()
      if not line:
         time.sleep(0.1)
         continue
      yield line

#------------------------------------------------------------------------------
# ENCRYPTION FUNCTIONS

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

#------------------------------------------------------------------------------
# EMAIL FUNCTIONS

def send_plain_email(to_addr, from_addr, subj, body):
   smtp_server = smtplib.SMTP('localhost')
   msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" % (from_addr, to_addr, subj, body))
   smtp_server.sendmail(from_addr, to_addr, msg)
   smtp_server.quit()

#------------------------------------------------------------------------------
# send_email(to_addrs, from_addr, subj, body, ...)
#
# The easiest way to send a few fancy emails.  Very customizable.
# See the VolumeEmailer class if you need to send a lot of emails.
#------------------------------------------------------------------------------

def send_email(to_addrs, from_addr, subj, body, attach=[], delattach=False, replyto_addr="", smtp_server='localhost', **kwargs):
   """
   to_addrs  - email address or list of email addresses
               'joe@example.com'
               ['joe@example.com', 'Jane <jane@example.com']
   from_addr - email address of sender
   subj      - Subject
   body      - Body of email.  Can be blank string.
   attach    - filename of file to attach, filename:mode to attach, or list
               of filename or filname:modes to attach.  Mode is 'inline' or
               'attachment'.  Default is 'attachment'
               '/some/file.pdf'
               '/some/file.txt:inline'
               ['/some/file.jpg:inline', '/other/file.png']
   delattach - True/False.  Default False.  Whether to delete the attachment
               files after sending the email.
   smtp_server- IP address or domain name of the smtp server to use. Default localhost.
   **kwargs  - Any keyword arguments will be added as extra headers
   """
   from email import Encoders
   from email.Message import Message
   from email.MIMEAudio import MIMEAudio
   from email.MIMEBase import MIMEBase
   from email.MIMEMultipart import MIMEMultipart
   from email.MIMEImage import MIMEImage
   from email.MIMEText import MIMEText
   # A great deal of this was pulled from the python reference doc examples
   # Listify vars that need it
   if type(attach) != type([]):
      attach = [attach]
   if type(to_addrs) != type([]):
      to_addrs = [to_addrs]
   # Start the message
   outer = MIMEMultipart()
   # BODY Guarantee the body of the message ends in a newline if there's a body
   if body:
      if (body[-1] != '\n'):
         body += '\n'
      bodypart = MIMEText(body)
      bodypart.add_header('Content-Disposition', 'inline')
      outer.attach(bodypart)
   # HEADERS
   outer['To'] = ", ".join(to_addrs)
   outer['From'] = from_addr
   outer['Subject'] = subj
   if replyto_addr:
      outer['Reply-To'] = replyto_addr
   outer.preamble = 'Please use a MIME-aware mail reader for this message.'
   # Guarantees the multi-part message ends in a newline
   outer.epilogue = ''

   for filename in attach:
      mode = 'attachment'
      # Strip off any mode information
      if filename.find(':') > -1:
         mode     = filename[filename.find(':')+1:]
         filename = filename[:filename.find(':')]
      # Make sure the mode is valid
      if (mode != 'attachment') and (mode != 'inline'):
         mode = 'attachment'
      # Get the bare filename without the path
      if filename.rfind('/') == -1:
         pretty_filename = filename
      else:
         # Just grab the filename without the full path
         pretty_filename = filename[filename.rfind('/')+1:]
      # Make sure we have the full path if we were passed a relative one
      path = os.path.abspath(filename)
      # Skip if the file doesn't exist
      if not os.path.isfile(path):
         continue
      ctype, encoding = mimetypes.guess_type(path)
      if ctype is None or encoding is not None:
         # No guess could be made, or the file is encoded (compressed), so
         # use a generic bag-of-bits type.
         ctype = 'application/octet-stream'
      maintype, subtype = ctype.split('/', 1)
      if maintype == 'text':
         fp = open(path)
         # Note: we should handle calculating the charset
         msg = MIMEText(fp.read(), _subtype=subtype)
         fp.close()
      elif maintype == 'image':
         fp = open(path, 'rb')
         msg = MIMEImage(fp.read(), _subtype=subtype)
         fp.close()
      elif maintype == 'audio':
         fp = open(path, 'rb')
         msg = MIMEAudio(fp.read(), _subtype=subtype)
         fp.close()
      else:
         fp = open(path, 'rb')
         msg = MIMEBase(maintype, subtype)
         msg.set_payload(fp.read())
         fp.close()
         # Encode the payload using Base64
         Encoders.encode_base64(msg)
      # Set the filename parameter
      msg.add_header('Content-Disposition', mode, filename=pretty_filename)
      outer.attach(msg)

   # Send the email
   server = smtplib.SMTP(smtp_server)
   server.sendmail(from_addr, to_addrs, outer.as_string())
   server.quit()
   # Remove the attachments if delattach is True (default: False)
   if delattach:
      for filename in attach:
         if os.path.isfile(filename):
            os.remove(filename)
