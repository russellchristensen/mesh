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

import core_tests, glob, imp, optparse, os, sys, unittest

sys.path.append(os.path.join(core_tests.project_root_dir, 'src'))

# Parse command-line arguments
parser = optparse.OptionParser()
parser.add_option('-a', '--test-all',     help='(DEFAULT) Test everything.',   action='store_true', dest='test_all', default=False)
parser.add_option('-c', '--test-core',    help='Test mesh core.',              action='store_true', dest='test_core', default=False)
parser.add_option('-p', '--test-plugins', help='Test all plugins.',            action='store_true', dest='test_plugins', default=False)
parser.add_option('-t', '--test-plugin',  help='Test a specific plugin only.', action='store', dest='test_plugin', default=False)
parser.add_option('-v', '--verbose',      help='Verbose output',               action='store_true', dest='verbose', default=False)
(options, args) = parser.parse_args()

# Default to running everything
if not (options.test_all + options.test_core + options.test_plugins) and not options.test_plugin:
   options.test_all = True

# Set verbosity
if options.verbose:
   verbosity = 2
else:
   verbosity = 1

suite_list = []
# Run core unit tests?
if options.test_all or options.test_core:
   suite_list.append(unittest.TestLoader().loadTestsFromModule(core_tests))
# Run all plugins' unit tests?
ok           = 0
unconfigured = 0
unsupported  = 0
broken       = 0
if options.test_all or options.test_plugins:
   for full_path in glob.glob(os.path.join(core_tests.project_root_dir, 'src', 'p_*py')):
      module_name = os.path.split(full_path)[1][:-3]
      print "Loading %-25s" % module_name,
      try:
         module_to_test = __import__(module_name)
      except:
         print "[Broken]"
         broken += 1
         continue
      if not sys.platform in module_to_test.supported_os:
         print "[Unsupported]"
         unsupported += 1
         continue
      elif not module_to_test.configured():
         print "[Unconfigured]"
         unconfigured += 1
         continue
      else:
         print "[OK]"
         ok += 1
         suite_list.append(unittest.TestLoader().loadTestsFromModule(module_to_test))
   print "OK: %d, Unconfigured: %d, Unsupported: %d, Broken: %d" % (ok, unconfigured, unsupported, broken)
# Run a specific plugin's unit tests?
elif options.test_plugin:
   module_to_test = __import__(options.test_plugin)
   suite_list.append(unittest.TestLoader().loadTestsFromModule(module_to_test))

uber_suite = unittest.TestSuite(suite_list)
unittest.TextTestRunner(verbosity=verbosity).run(uber_suite)
   
