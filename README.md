FRAMERATE WATCHER
=================

![alt tag](https://raw.github.com/stenyak/framerateWatcher/master/screenshot.jpg)

DESCRIPTION
-----------
App for the racing simulator Assetto Corsa www.assettocorsa.net

Analyzes and plots various framerate statistics.

Implements a spike detector which is less sensitive than the default.

Registers the timestamps of those major spikes, in order to help compare them with other system statistics (gathered through third party programs, such as ProcessExplorer or PerfMon).


INSTALL
-------

 1. Open your AC/apps/plugins directory.
 2. Create a directory named framerateWatcher.
 3. Copy the framerateWatcher.py file inside.

TODO
----

 * Log most cpu/gpu/io consuming process whenever a spike is detected.
 * Allow user to customize the FramerateWatcher constants via UI controls.


LICENSING
---------

Copyright 2013 Bruno Gonzalez Campo <stenyak@stenyak.com>

Distributed under the GNU GPL v3. For full terms see the LICENSE.txt file.
