Changelog
=========

Version 0.0.11
--------------

Changes
~~~~~~~
- Improved memory use by deleting large variables when they are not of use anymore.
- Improved memory use by using np.int8 in create_black_line function.
- Made sure that every data in Datasets are numpy arrays.


Version 0.0.10
--------------

Changes
~~~~~~~
- Forced fixed timesteps in extract_currs, since currentscape expects data with fixed timesteps.

Version 0.0.9
-------------

Added
~~~~~
- New SAHP stimulus for current extraction.



Version 0.0.8
-------------

Fixed
~~~~~
- Test data in test_currentscape_functions.


Version 0.0.7
-------------

Fixed
~~~~~
- Unit conversion when turning current density into currents in extract_currs.

Added
~~~~~
- Added tests for data processing functions.
- Added warning when there is not enough colors in colormap.

Changes
~~~~~~~
- Refactored currentscape into smaller, more meaningful modules.
- Changed default left-side adjusting, 
    so that the labels and ticks do not overlap.
- Changed dict key for blackline thickness and x-chunksize in config
    since they should not belong exclusively to currentscape anymore.
- Changed 'labels' and 'ticklabels' to 'ylabels' and 'yticklabels' in config["show"]
    to distinguish them from 'xlabels' and 'xticklabels'.

New Features
~~~~~~~~~~~~
- Reorder the currents in each subplot, 
    so that the currents with the largest contribution lay at the top.
    The legend is reordered accordingly.
- Added an autoscaling for y limits and ticks for current (and ions) subplots.
- Added a new subplot to currentscape: absolute currents.
- Absolute currents can be displayed as lines or as a stackplot.
- Allowed extract_currs to extract ionic concentration.
- Added a new subplot to currentscape: ionic concentration.
- Added a new subplot: pie charts showing the overall contribution of currents.
- Label and ticklabel of the x axis can now be displayed on the bottom plot.
- Gridlines corresponding to the x ticks can be displayed on all the plots.
- x ticks can be custom or generated automatically.
- Currentscape plotting can be disabled in the config.


Version 0.0.6
-------------

Fixes
~~~~~
- Currentscape used to fill empty data (e.g. no inward/outward current at all)
    with the first color in data. Now it fills it with white.
- Fixed config example in README and doc.
- Removed top and bottom frame of currentscape which was hiding part of the data.
- Fixed central black line separating currentscape plots that weas hiding part of the data.

New Features
~~~~~~~~~~~~
- Added new colormap choices.
- Added possibility of putting patterns (hatches) on top of color palette.
- When using patterns, matplotlib uses bar plots, which takes some time to compute,
    so reducing x-resolution was enabled.
- Chunksize (when reducing x-resolution) is corrected when not a divisor of data size.
- Patterns color, design and 'density' can be customised.
- The legend y position can be customised.
- Added a 'mixer' that prevent two successive currents to have the same color or pattern.
- Added library to easily extract currents from any location (soma or other).
- Now uses neuron in extract_currs lib to get the segment area and use it to turn
    current densities into currents.
- Can use default protocols from singlecell-optimization, or custom protocols.
- Added tests for extract currents.


Version 0.0.4
-------------

- Added docs to tox envlist.


Version 0.0.3
-------------

Fixes
~~~~~
- Fixed non pylint-conform style.


Version 0.0.2
-------------

New Features
~~~~~~~~~~~~
- Added documentation.


Version 0.0.1
-------------

New Features
~~~~~~~~~~~~
- Currentscapes can be plotted using code from Alonso and Marder (2019).
- Labels, ticks and legend are automatically added to the figure.
- Most of the style is hard-coded, to stay close to the original paper,
    but the figure display can still be adapted to most data, using a configuration file.
- Added example from original paper.
- Added example in README.md with link to homemade data.