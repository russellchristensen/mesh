# What is mesh?

**mesh** is a decentralized, secure, powerful, fast monitoring system.

# What's the status of development?

_Design/Alpha Development!_

We're very actively designing, prototyping, and changing things all the time.  Developers welcome!

# Getting Started

#### You must have...
* OS X, Linux or similar OS.  Windows only if you want to help get it working.
* [git](http://git-scm.com/)
* [Python 2.5+](http://python.org)

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

> src/mesh.py
# Resources
* [Mesh Messaging Design Overview (.pdf)](https://github.com/meshers/mesh/blob/master/docs/messaging-design-overview.pdf)
* [Plugin Ideas (.txt)](https://github.com/meshers/mesh/blob/master/docs/plugin_ideas.txt)
