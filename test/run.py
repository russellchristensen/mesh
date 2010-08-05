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
      "==> Starting Prerequisite Tests"

   def test_01os(self):
      "Supported OS?"
      self.assertTrue(sys.platform in ['darwin'])

   def test_03python_version(self):
      "Supported version of Python?"
      supported_version = version.StrictVersion('2.6')
      this_version = version.StrictVersion(str(sys.version_info[0]) + '.' + str(sys.version_info[1]))
      self.assertTrue(this_version >= supported_version)

   def test_06twisted(self):
      "Supported version of Twisted?"
      import twisted
      supported_version = version.StrictVersion('9.0')
      this_version = version.StrictVersion(twisted.__version__)
      self.assertTrue(this_version >= supported_version)

   def test_09pyopenssl(self):
      "Supported version of pyOpenSSL?"
      import OpenSSL
      supported_version = version.StrictVersion('0.7')
      this_version = version.StrictVersion(OpenSSL.version.__version__)
      self.assertTrue(this_version >= supported_version)


global project_root_dir; project_root_dir = None ; # Gotta be a way better than a global...

class Test01Code(unittest.TestCase):
   def setUp(self):
      pass

   def tearDown(self):
      pass

   def test_00banner(self):
      "==> Starting Code Tests"

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
      source_files = ['test/run.py'] # It would be nice to dynamically find all source files instead of hard-code them here...
      for fname in source_files:
         header = open(os.path.join(project_root_dir, fname), 'r').read(100)
         self.assertTrue("# This file is part of Mesh." in header) # We could probably do a more thorough check...

if __name__ == '__main__':
   unittest.main()
