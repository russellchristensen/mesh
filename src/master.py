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

import os, subprocess, tempfile, zmq


#------------------------------------------------------------------------------
# ZMQ sockets

# Socket objects

zmq_context  = None
push_comm    = None
pull_general = None

# Names of interprocess sockets to bind/connect to.
master_socket_name        = "ipc:///" + tempfile.NamedTemporaryFile().name + '-master.ipc'
communicator_socket_name  = "ipc:///" + tempfile.NamedTemporaryFile().name + '-communicator.ipc'
port_assigner_socket_name = "ipc:///" + tempfile.NamedTemporaryFile().name + '-port_assigner.ipc'
print """Sockets:
master_socket_name:        %s
communicator_socket_name:  %s
port_assigner_socket_name: %s""" % (
   master_socket_name,
   communicator_socket_name,
   port_assigner_socket_name)

# Needs to be called first ... unless we're unit-testing.
def create_zmq_context():
   global zmq_context
   zmq_context = zmq.Context()

# Calls all socket creation functions
def create_zmq_sockets():
   create_push_comm()
   create_pull_general()

def create_push_comm():
   global push_comm
   push_comm = zmq_context.socket(zmq.PUSH)
   push_comm.connect(communicator_socket_name)
   push_comm.send("master alive")

def create_pull_general():
   global pull_general
   pull_general = zmq_context.socket(zmq.PULL)
   pull_general.bind(master_socket_name)

#------------------------------------------------------------------------------
# Child-process stuff

# Process objects:
port_assigner      = None
communicator       = None
inbound_pull_proxy = None       # pull_proxy.py with the 'inbound' option
outbound_pull_proxies = {}      # pull_proxy.py instances with the 'outbound' option

def start_port_assigner():
   global port_assigner
   port_assigner = subprocess.Popen(('/usr/bin/env', 'python', 'port_assigner.py'))

def start_communicator():   
   global communicator
   communicator = subprocess.Popen(('/usr/bin/env', 'python', 'communicator.py'))
   
def start_inbound_pull_proxy():
   global inbound_pull_proxy
   inbound_pull_proxy = subprocess.Popen(('/usr/bin/env', 'python', 'pull_proxy.py', 'inbound'))

def start_outbound_pull_proxy(unique_name):
   if outbound_pull_proxies.has_key(unique_name):
      return "'%s' is already taken!!!"
   else:
      outbound_pull_proxies[unique_name] = subprocess.Popen(
         ('/usr/bin/env', 'python', 'pull_proxy.py', 'outbound', unique_name))

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
   
