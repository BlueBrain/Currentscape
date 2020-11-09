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

    module load archive/2020-10
    module load python


Matplotlib
~~~~~~~~~~

Matplotlib is automatically installed with the pip installation,
but is not automatically installed with the currentscape module yet, so in that case, 
you should install it yourself in your virtual environment ::

    pip install matplotlib

Numpy
~~~~~

Numpy is automatically installed with the pip installation,
but is not automatically installed with the currentscape module yet, so in that case, 
you should load it yourself ::

    module load archive/2020-10
    module load py-numpy
