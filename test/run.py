#!/usr/bin/env python

import unittest, sys
from distutils import version

class TestPrerequisites(unittest.TestCase):
   def setUp(self):
      pass

   def test_00(self):
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
