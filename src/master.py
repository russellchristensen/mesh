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

import meshlib, optparse, os, subprocess, sys, tempfile, time, zmq

# This can be overridden by command-line arguments
def verbose(msg):
   pass

#------------------------------------------------------------------------------
# Command-line arguments

if __name__ == '__main__':
   parser = optparse.OptionParser()
   parser.add_option('-c', '--config-file', help = 'Config file to use instead of $ETC/mesh.conf', action = 'store', dest = 'config_file', default = None)
   parser.add_option('-t', '--try-plugin',  help = 'Name of single plugin (without .py) to run to try.', action = 'store', dest = 'try_plugin', default = None)
   parser.add_option('-v', '--verbose',     help = 'Verbose mode.', action = 'store_true', dest = 'verbose', default = False)
   (options, args) = parser.parse_args()

   # Vebose mode?
   if options.try_plugin:
      print "Note: --try-plugin implies --verbose"
      options.verbose = True

   if options.verbose:
      def verbose(msg):
         print "master:", msg

   meshlib.load_config(options.config_file)
else:
   meshlib.load_config()

#------------------------------------------------------------------------------
# Config items
inbound_pull_proxy_port = meshlib.get_config(None, 'inbound_pull_proxy_port', '4201')
identifier              = meshlib.get_identifier()

#------------------------------------------------------------------------------
# ZMQ Setup

# Context & sockets for master.py
zmq_context       = zmq.Context()
pull              = None
push_communicator = None

# IPC urls for everything
master_pull_url         = meshlib.socket_url('ipc')
communicator_pull_url   = meshlib.socket_url('ipc')
port_assigner_pull_url  = meshlib.socket_url('ipc')
port_requestor_pull_url = meshlib.socket_url('ipc')

def create_pull():
   global pull
   pull = zmq_context.socket(zmq.PULL)
   pull.bind(master_pull_url)

def create_push_communicator():
   global push_communicator
   push_communicator = zmq_context.socket(zmq.PUSH)
   push_communicator.connect(communicator_pull_url)
   push_communicator.send("master alive")

#------------------------------------------------------------------------------
# Try Plugin?

if __name__ == '__main__' and options.try_plugin:
   create_pull()
   print "Running in TRY PLUGIN mode.  We will run until either '%s' detects an event or dies.\n" % options.try_plugin
   plugin_process = subprocess.Popen(('/usr/bin/env', 'python', options.try_plugin + '.py', master_pull_url))
   while True:
      retcode = plugin_process.poll()
      if retcode != None:
         print "Plugin exited with retcode", retcode
         sys.exit()
      try:
         msg = pull.recv(flags=zmq.NOBLOCK)
         print "Received message from plugin '%s':\n-----------------------------\n%s" % (options.try_plugin, msg)
         plugin_process.send_signal(9)
         sys.exit()
      except zmq.core.error.ZMQError, zmq_error:
         if zmq_error == 'Resource temporarily unavailable':
            pass                # That's what we expect when polling
      time.sleep(.1)
   sys.exit()

#------------------------------------------------------------------------------
# Child-process stuff

# Process objects:
communicator       = None
inbound_pull_proxy = None       # pull_proxy.py with the 'inbound' option
outbound_pull_proxies = {}      # pull_proxy.py instances with the 'outbound' option
port_assigner      = None
port_requestor     = None

def start_communicator():   
   global communicator
   communicator = subprocess.Popen(
      ('/usr/bin/env', 'python', os.path.join(meshlib.project_root_dir, 'src', 'communicator.py'), 
       meshlib.config_file, master_pull_url, communicator_pull_url, port_assigner_pull_url, port_requestor_pull_url))
   
def start_port_assigner():
   global port_assigner
   port_assigner = subprocess.Popen(
      ('/usr/bin/env', 'python', os.path.join(meshlib.project_root_dir, 'src', 'port_assigner.py'),
       meshlib.config_file, communicator_pull_url, port_assigner_pull_url))

def start_port_requestor():
   global port_requestor
   port_requestor = subprocess.Popen(
      ('/usr/bin/env', 'python', os.path.join(meshlib.project_root_dir, 'src', 'port_requestor.py'),
       meshlib.config_file, communicator_pull_url, port_requestor_pull_url))

def start_inbound_pull_proxy():
   global inbound_pull_proxy
   inbound_pull_proxy = subprocess.Popen(
      ('/usr/bin/env', 'python', os.path.join(meshlib.project_root_dir, 'src', 'pull_proxy.py'), 
       meshlib.config_file, 'inbound', '*', inbound_pull_proxy_port, communicator_pull_url))

def start_outbound_pull_proxy(target, port):
   if outbound_pull_proxies.has_key(target):
      return "'%s' is already taken!!!"
   else:
      outbound_pull_proxies[target] = subprocess.Popen(
         ('/usr/bin/env', 'python', os.path.join(meshlib.project_root_dir, 'src', 'pull_proxy.py'), 
          meshlib.config_file, 'outbound', target, port, communicator_pull_url))

def check_children():
   print "\nProcess Report:"
   # Check communicator
   if communicator:
      print "communicator", communicator.poll()
   else:
      print "communicator: no process object"
   # Check inbound_pull_proxy
   if inbound_pull_proxy:
      print "inbound_pull_proxy", inbound_pull_proxy.poll()
   else:
      print "inbound_pull_proxy: no process object"
   # Check port_assigner
   if port_assigner:
      print "port_assigner", port_assigner.poll()
   else:
      print "port_assigner: no process object"
   # Check port_requestor
   if port_requestor:
      print "port_requestor", port_requestor.poll()
   else:
      print "port_requestor: no process object"

#------------------------------------------------------------------------------
# Message processing

def process_message(msg):
   # Manual intervention
   msg_parts = msg.split(':')
   msg_type = msg_parts[0]
   if msg_type == 'man':
      verbose("Handling a manual message: '%s'" % msg)
      if msg_parts[1] == 'connect_node':
         push_communicator.send(':'.join(msg_parts[1:]))
         return
   # Malformed message, apparently
   verbose("Malformed message: %s" % msg)
   
#------------------------------------------------------------------------------
# Main Loop

if __name__ == '__main__':
   verbose ("""IPC URLs
identifier:              %s
master_pull_url:         %s
communicator_pull_url:   %s
port_assigner_pull_url:  %s
port_requestor_pull_url: %s

Config items:
inbound_pull_proxy_port: %s
""" % (
   identifier,
   master_pull_url,
   communicator_pull_url,
   port_assigner_pull_url,
   port_requestor_pull_url,
   inbound_pull_proxy_port))
   # Create our sockets
   create_push_communicator()
   create_pull()
   # Start the rest of the processes
   start_communicator()
   start_inbound_pull_proxy()
   start_port_assigner()
   start_port_requestor()
   # Main loop
   while True:
      inbound_msg = pull.recv()
      if inbound_msg == 'quit':
         break
      else:
         verbose(inbound_msg)
         process_message(inbound_msg)
      time.sleep(.5)
      check_children()
   # Shutting down...
   print "Received 'quit' -- sending children kill signal and exiting."
   # Kill child processes
   for child in [port_assigner, communicator, inbound_pull_proxy, port_requestor]:
      if child.poll() == None:
         child.send_signal(subprocess.signal.SIGTERM)
   time.sleep(.1)
   # Try cleaning up IPC files
   for url in [master_pull_url, communicator_pull_url, port_assigner_pull_url, port_requestor_pull_url]:
      try:
         os.remove(url[6:])
      except:
         pass
