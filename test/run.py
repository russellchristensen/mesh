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

import unittest, sys
from distutils import version

class TestPrerequisites(unittest.TestCase):
   def setUp(self):
      pass

   def test_00os(self):
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

   def tearDown(self):
      pass

if __name__ == '__main__':
   unittest.main()
