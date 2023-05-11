Changelog
=========

Version 0.1.1
-------------

Changes
~~~~~~~
- examples is not be treated as a module anymore (as it should). To use the examples, one should go to the example folder to run the scripts.
- Added line creation in get_colors_and hatches_lists, renamed it get_colors_hatches_lines_lists and used it in more places.

Added
~~~~~
- Example with a cell, script to record currents/ionic concentrations from it, and script to plot its currentscape.
- Test to run the new example, running the cell and plotting its currentscape.

Fixed
~~~~~
- Fixed legend for currentscape with no hatches
- Removed minor yticks. They were popping out when not using autoscale for ylim and ticks with log scale
- Dotted horizontal lines at tick level. They were not the right length when data with adaptable timesteps were given

Removed
~~~~~~~
- extract_currs module
- unused .gitreview file
- __init__.py file in examples. examples folder should not be treated as a module.


Version 0.1.0
-------------

Changes
~~~~~~~
- use fill_between instead of imshow or barplot (more precise, less pixelised and consumes less memory)
- default extension for figure saving in config is now pdf (in order to not loose details)

Added
~~~~~
- new 'legacy_method' entry in config for currents and currentscape to access legacy imshow and barplots


Version 0.0.12
--------------

Changes
~~~~~~~
- Turned some print statements into logging statements
- Refactored Main Protocol's run function in extract_currs
- Refactored output writing into a write_output function in extract_currs
- Turned os.path statements into pathlib.Path statements
- Refactored extract_currs/features/define_efeatures
- Turned string formatting into f-strings
- Refactored the loading of release_params into a function
- Moved bluepyopt, neuron and scipy dependencies as extras in setup.py
- Refactored currents.reorder_currents_and_names for better quality code
- Used np.asarray instead of np.array when  possible
- Refactored color and pattern mapping into functions
- Renamed col_idxs into curr_idxs in several function arguments

Added
~~~~~
- Unit tests for all currentscape functions that do not use matplotlib
- Linting checks to the extract_currs module
- Test for the new write_output function
- Installation instructions in the README

Removed
~~~~~~~
- Unused logging.basicConfig
- Print statements
- extract_currs/YeoJohnson.py
- extract_currs/features/eFELFeatureExtra
- extract_currs/features/SingletonWeightObjective
- Non-necessary stuff from extract_currs/features/define_efeatures
- Score calculations during Main Protocol
- Non-necessary variables form extract_currs' create_protocols
- __init__ function in SweepProtocolCustom that was the same as the parent class

Fixed
~~~~~
- Tox
- Barplot shrinking when chunk size has to be resized


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