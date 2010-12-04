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

import glob, os, unittest, sys
from distutils import version

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

   def test_03license(self):
      "GPL 3 Compliance"
      global project_root_dir
      # Iterate through the python files and check for compliance
      source_files = ['test/run.py', 'src/mesh.py', 'src/meshlib.py'] # It would be nice to dynamically find all source files instead of hard-code them here...
      for fname in source_files:
         header = open(os.path.join(project_root_dir, fname), 'r').read(100)
         self.assertTrue("# This file is part of Mesh." in header) # We could probably do a more thorough check...

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
      pass

if __name__ == '__main__':
   unittest.main()
