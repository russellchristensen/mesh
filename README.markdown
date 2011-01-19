# What is mesh?

**mesh** is a decentralized, secure, powerful, fast monitoring system.

# What's the status of development?

_Design/Pre-beta Development!_

We're very actively designing, prototyping, and changing things all the time.  Developers welcome!

# Getting Started

#### You must have...
* OS X, Linux or similar OS.  Windows only if you want to help get it working.
* [git](http://git-scm.com/)  - (And on OS X I highly recommend [gitx](http://gitx.frim.nl/) as well)
* [Python 2.6+](http://python.org)

####Clone the mesh repository onto your machine:

> git clone git://github.com/meshers/mesh.git

#### Run the tests and see what you are missing:

> cd mesh
> tests/run.py -v

#### Most likely, you'll need to install some or all of these packages:

* [M2Crypto](http://chandlerproject.org/bin/view/Projects/MeTooCrypto)
* [ZeroMQ](http://www.zeromq.org/)
* [PyZMQ](http://www.zeromq.org/bindings:python)
* [psutil](http://code.google.com/p/psutil/)

#### Once the tests pass, you're ready!

> ./mesh

# Resources
* [Mesh Messaging Design Overview (.pdf)](https://github.com/meshers/mesh/blob/master/docs/messaging-design-overview.pdf)
* [Plugin Ideas (.txt)](https://github.com/meshers/mesh/blob/master/docs/plugin_ideas.txt)

# Roadmap

The roadmap is subject to (lots of) change without notice!

#### Version 0.1 (Released Jan 18 2011 - https://github.com/meshers/mesh/downloads/mesh-0.1.tar.bz2)
* Target audience: Developers only
* Nodes can communicate (NOTE: COMMUNICATIONS ARE COMPLETELY UNSECURED!!)
* Node connections are initiated manually
* Some basic plugins work
* Event model undetermined
* All configuration done manually in the config file
* Brain-dead email-relay listener implemented

#### Version 0.2 (Release ETA: before Feb 2011)
* Target audience: Developers only
* Nodes have brain-dead routing, but it makes it to the destination...eventually.
* Nodes can communicate securely
* Completely manual certificate / CA management
* Plugin interface refinements
* Plugin unit-testing requirements formalized
* More plugins
* Node re-connection support
* Event model formalized
* Start creating configuration program

#### Version 0.3 (Release ETA: Feb 2011)
* Target audience: Very advanced users
* More plugins
* Improvements to listener
* Nodes have better routing
* Simplify certificate management, first steps toward certificate automation

#### Version 0.5 (Release ETA: Mar 2011)
* Target audience: Very Advanced users
* Node auto-connection support for same-LAN
* More plugins
* Configuration program 100% usable
* More listener types

#### Version 0.6 (Release ETA: 2Q 2011)
* Target audience: Advanced users
* Node auto-connection support for different-LAN
* Nodes have really good routing
* More plugins
* Configuration program knows which plugins will work on the current system/setup.

#### Version 0.7 (Release ETA: 3Q 2011)
* Target audience: Competent sys admins
* Auto-configuration
* Automatic CA / certificate management

#### Version 1.0 (Release ETA: 3Q/4Q 2011)
* Target audience: All sys admins
