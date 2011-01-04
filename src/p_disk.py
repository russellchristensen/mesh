#! /usr/bin/env python

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
import subprocess
import time
import re

while True:
   proc = subprocess.Popen(['df'], stdout=subprocess.PIPE)
   # Get df output
   df_out = proc.stdout.read()
   parse = re.compile(r'^(.+)[\n\r]? +(\d+) +(\d+) +(\d+) +(\d+)% +([a-zA-Z/_\-\.\d]+)', re.MULTILINE)
   # Iterate through the parsed output of df
   for fs, blocks, used, available, percent, mounted in re.findall(parse, df_out):
      # Convert the parsed data for ease of use later
      fs, blocks, used, available, percent, mounted =  fs.strip(), int(blocks.strip()), int(used.strip()), int(available.strip()), int(percent.strip()), mounted.strip()
      print fs, blocks, used, available, percent, mounted
   print
   time.sleep(1)
