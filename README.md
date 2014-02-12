mkvswitch
=========
Script for mass-switching default tracks in MKV containers.

##### Requirements
* Python 2.7+
* enzyme (`pip install enzyme`)
* mkvtoolnix (`http://www.bunkus.org/videotools/mkvtoolnix/downloads.html`)


##### Setup
* Add path to mkvpropedit executable from mkvtoolnix package to settings.py


##### Use
`python mkvswitch.py [-r(ecursive)] path [path ...]` where path is either a directory or a MKV file. When prompted input number pairs for tracks to be set as default.


##### Known issues
* Files with tracks which names contain characters that can't be represented at current console encoding will be skipped with an error.
* This would be so much better with a GUI.
