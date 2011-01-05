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
parser.add_option('-a', '--test-all',     help='Test everything.',               action='store_true', dest='test_all', default=False)
parser.add_option('-c', '--test-core',    help='(DEFAULT) Test mesh core only.', action='store_true', dest='test_core', default=False)
parser.add_option('-p', '--test-plugins', help='Test all plugins.',              action='store_true', dest='test_plugins', default=False)
parser.add_option('-t', '--test-plugin',  help='Test a specific plugin only.',   action='store', dest='test_plugin', default=False)
parser.add_option('-v', '--verbose',      help='Verbose output',                 action='store_true', dest='verbose', default=False)
(options, args) = parser.parse_args()

# Default to running core unit tests
if not (options.test_all + options.test_core + options.test_plugins) and not options.test_plugin:
   options.test_core = True

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
if options.test_all or options.test_plugins:
   for full_path in glob.glob(os.path.join(core_tests.project_root_dir, 'src', 'p_*')):
      module_name = os.path.split(full_path)[1][:-3]
      print "Importing '%s' ... " % module_name,
      module_to_test = __import__(module_name)
      print "done."
      suite_list.append(unittest.TestLoader().loadTestsFromModule(module_to_test))
# Run a specific plugin's unit tests?
elif options.test_plugin:
   module_to_test = __import__(options.test_plugin)
   suite_list.append(unittest.TestLoader().loadTestsFromModule(module_to_test))

uber_suite = unittest.TestSuite(suite_list)
unittest.TextTestRunner(verbosity=verbosity).run(uber_suite)
   
