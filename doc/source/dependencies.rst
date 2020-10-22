.. _dependencies:

Dependencies
============

The main dependencies of currentscape are::

    Python 3.6+ 
    Matplotlib
    Numpy

Ideally, follow the installation instructions of these tools, or use 
pre-installed versions.

Python
------

Modern Linux systems will have Python 2.7 or 3 installed.

Make sure you're using a recent version of pip. It's best to run ::

    pip install pip --upgrade

before installing anything else using pip.

Possibly ways to acquire Python on BB5 are:

Pre-installed modules
~~~~~~~~~~~~~~~~~~~~~

First, you need to load an archive of your choice containing Python. Then you can load Python ::

    module load archive/2020-02
    module load python


Matplotlib
~~~~~~~~~~

You won't have to manually install Matplotlib, it is automatically installed by
the pip-install of currentscape.

Numpy
~~~~~

You won't have to manually install Numpy, it is automatically installed by
the pip-install of currentscape.
