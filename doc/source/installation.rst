Installation
============

This installation guide will explain on how to install currentscape.


Installing currentscape
-----------------------

To install currentscape, you probably want to use a python 
`virtual environment <https://bbpteam.epfl.ch/project/spaces/display/BBPWFA/virtualenv>`_.

Currentscape can be pip installed with all its dependencies with the following line:

    pip install -i https://bbpteam.epfl.ch/repository/devpi/simple/ currentscape[example]

This install the currentscape module and its dependencies, as well as the dependencies needed for the example reproducing the currentscape plot from the original paper.

Do not put any brackets if you just want to plot currentscapes, and are not interested in the original example.


Installing from source 
----------------------

If you want to make changes to currentscape, you might want to install it using the 
source repository. The same remarks of the section above apply, 
the only difference is that you clone the git repo::

   git clone ssh://bbpcode.epfl.ch/cells/currentscape.git

and run pip from inside the newly created currentscape subdirectory 
(don't forget the dot at the end of the command)::

    pip install -i https://bbpteam.epfl.ch/repository/devpi/bbprelman/dev/+simple --upgrade .[example]

Supported systems
-----------------

The code of currentscape can be installed on any POSIX system that supports 
pip-installable python code.
