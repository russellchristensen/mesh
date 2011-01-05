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
   parser.add_option('-t', '--try-plugin', help='Name of single plugin (without .py) to run to test.', action='store', dest='test_plugin', default=None)
   parser.add_option('-v', '--verbose',    help='Verbose mode.', action='store_true', dest='verbose', default=False)
   (options, args) = parser.parse_args()

   # Vebose mode?
   if options.test_plugin:
      print "Note: --test_plugin implies --verbose"
      options.verbose = True

   if options.verbose:
      def verbose(msg):
         print msg

#------------------------------------------------------------------------------
# ZMQ sockets

# Socket objects

zmq_context  = zmq.Context()
push_comm    = None
pull_general = None

# Names of interprocess sockets to bind/connect to.
master_socket_url        = meshlib.socket_url('ipc')
communicator_socket_url  = meshlib.socket_url('ipc')
port_assigner_socket_url = meshlib.socket_url('ipc')

verbose ("""Sockets:
master_socket_url:        %s
communicator_socket_url:  %s
port_assigner_socket_url: %s""" % (
   master_socket_url,
   communicator_socket_url,
   port_assigner_socket_url))

# Calls all socket creation functions
def create_zmq_sockets():
   create_push_comm()
   create_pull_general()

def create_push_comm():
   global push_comm
   push_comm = zmq_context.socket(zmq.PUSH)
   push_comm.connect(communicator_socket_url)
   push_comm.send("master alive")

def create_pull_general():
   global pull_general
   pull_general = zmq_context.socket(zmq.PULL)
   pull_general.bind(master_socket_url)

#------------------------------------------------------------------------------
# For plugin trial runs

if __name__ == '__main__':
   if options.test_plugin:
      create_zmq_context()
      create_pull_general()
      print "Running in TRY PLUGIN mode.  We will run until either '%s' detects an event or dies.\n" % options.test_plugin
      plugin_process = subprocess.Popen(('/usr/bin/env', 'python', options.test_plugin + '.py', master_socket_url))
      while 1:
         retcode = plugin_process.poll()
         if retcode != None:
            print "Plugin exited with retcode", retcode
            sys.exit()
         try:
            msg = pull_general.recv(flags=zmq.NOBLOCK)
            print "Received message from plugin '%s':\n-----------------------------\n%s" % (options.test_plugin, msg)
            plugin_process.send_signal(9)
            sys.exit()
         except zmq.core.error.ZMQError, zmq_error:
            if zmq_error == 'Resource temporarily unavailable':
               pass                # That's what we expect when polling
         time.sleep(.1)

#------------------------------------------------------------------------------
# Child-process stuff

# Process objects:
port_assigner      = None
communicator       = None
inbound_pull_proxy = None       # pull_proxy.py with the 'inbound' option
outbound_pull_proxies = {}      # pull_proxy.py instances with the 'outbound' option

def start_port_assigner():
   global port_assigner
   port_assigner = subprocess.Popen(('/usr/bin/env', 'python', os.path.join(meshlib.project_root_dir, 'src', 'port_assigner.py')))

def start_communicator():   
   global communicator
   communicator = subprocess.Popen(('/usr/bin/env', 'python', os.path.join(meshlib.project_root_dir, 'src', 'communicator.py')))
   
def start_inbound_pull_proxy():
   global inbound_pull_proxy
   inbound_pull_proxy = subprocess.Popen(('/usr/bin/env', 'python', os.path.join(meshlib.project_root_dir, 'src', 'pull_proxy.py'), 'inbound'))

def start_outbound_pull_proxy(unique_name):
   if outbound_pull_proxies.has_key(unique_name):
      return "'%s' is already taken!!!"
   else:
      outbound_pull_proxies[unique_name] = subprocess.Popen(
         ('/usr/bin/env', 'python', os.path.join(meshlib.project_root_dir, 'src', 'pull_proxy.py'), 'outbound', unique_name))

def start_children():
   start_port_assigner()
   start_communicator()
   start_inbound_pull_proxy()

def check_children():
   # Check port_assigner
   if port_assigner:
      print "port_assigner", port_assigner.poll()
   else:
      print "port_assigner: no process object"
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

#------------------------------------------------------------------------------
# Message processing

def process_message(inbound_msg):
   print "Received:", inbound_msg

#------------------------------------------------------------------------------
# "MAIN"

# About the only thing we can't unittest is this main loop, so we'll hide it here.
if __name__ == '__main__':
   create_zmq_context()
   create_zmq_sockets()
   start_children()
   while 1:
      inbound_msg = pull_general.recv()
      process_message(inbound_msg)
      check_children()
   
