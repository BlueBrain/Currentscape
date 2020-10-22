Installation
============

This installation guide will explain on how to install currentscape.

Installing currentscape as a BBP module
---------------------------------------

If you are on gpfs, getting currentscape should be as easy as::

    module load unstable
    module load currentscape


Installing currentscape
-----------------------

You can also install currentscape using pip.

In that case, you probably want to use a python 
`virtual environment <https://bbpteam.epfl.ch/project/spaces/display/BBPWFA/virtualenv>`_.

Pip install currentscape from the BBP Devpi server::

    pip install -i 'https://bbpteam.epfl.ch/repository/devpi/bbprelman/dev/+simple/' currentscape[bbp]

Hopefully this installation went smoothly. If it didn't, please create a Jira 
ticket, assign it to Aurelien Jaquier, and explain as detailed as possible the problems you encountered.


Installing from source 
----------------------

If you want to make changes to currentscape, you might want to install it using the 
source repository. The same remarks of the section above apply, 
the only difference is that you clone the git repo::

   git clone ssh://bbpcode.epfl.ch/cells/currentscape.git

and run pip from inside the newly created currentscape subdirectory 
(don't forget the dot at the end of the command)::

    pip install -i https://bbpteam.epfl.ch/repository/devpi/bbprelman/dev/+simple --upgrade .[bbp]

Supported systems
-----------------

The code of BGLibPy can be installed on any POSIX system that supports 
pip-installable python code.
