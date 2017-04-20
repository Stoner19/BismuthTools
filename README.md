# BismuthTools

Tools for the Bismuth Cryptocurrency

This repository contains tools I personally use for the Bismuth Cryptocurrency

For license see LICENSE file

The tool is intended for personal use.

There is a web version based on webpy in the WebEdition folder

See releases for pre-compiled versions

No promises are given that the tools will run on your particular system

Notes:

1. In order to take into account the use of Hyperblocks technology the query components are only designed to use blocks since the latest hyperblock in your ledger.

Requirements

Windows

1. Windows 7 or better
2. Bismuth cryptocurrency installed via the latest installation executable at https://github.com/hclivess/bismuth/releases or run from source
3. The latest executable from releases https://github.com/maccaspacca/BismuthTools/releases use "bismuthtools.exe" for desktop or "bismuthtoolsweb.exe" if you want to access from a browser (localhost:8080)

4. Run from source
 a. Python 2.7 and dependencies as detailed at https://bitcointalk.org/index.php?topic=1525078
 
 b. wxpython for your Python 2.7 installation as found here: https://wxpython.org/download.php
 
 c. If you have sponsors enabled then you will need BS4 (pip install bs4)
 
 d. If you wish you can compile your own executables using pyinstaller and the .cmd files provided

Linux e.g. Ubuntu 16.04 LTS

1. Python 2.7 and dependencies as detailed at https://bitcointalk.org/index.php?topic=1525078
2. wxpython for your Python 2.7 installation as found here: https://wxpython.org/download.php or installed using apt-get
3. The Bismuth cryptocurrency installed from source (some additional python components such as pysocks may be needed depending on your installation)
4. If you have sponsors enabled then you will need BS4 (pip install bs4)
5. You can also compile your own executables using pyinstaller and the .cmd file provided or use the ones provided in releases

File placement

The files should be placed into a folder called "tools" under the /bismuth folder on your main Bismuth installation folder.

If a folder doesn't already exist called "tools" you will need to create one.

miners.db

On first run, if there is no miners.db then a new one will be created.
Once the update process is complete then click 'Refresh List' to display the new or latest list of miners.

Version 0.2 Improvements 21/03/2017

1. Better help menus
2. Wallet info auto refresh every 5 mins
3. Miner query auto list refresh
4. Ledger query, latest block auto refresh every 5 mins
5. Basic logging to 'tools.log'

Version 0.21 Changes 24/03/2017

1. Incorporate Hclivess pull request
2. Code changes and bug fixes
3. New feature: Miner name registration - see your name instead of address in Miner Query - more information in Name.md

Note: Make sure you delete your existing miner.db file before you run this update of the tool (or overwrite it with the one provided)

Version 0.3 Changes 27/03/2017

1. Code adjustments to provide Linux support
2. Use of threadsafe code to pass data to the statusbar
3. Minor look and feel changes

Note: Make sure you delete your existing miner.db file before you run this update of the tool (or overwrite it with the one provided)

Version 0.31 Changes 29/03/2017

1. Bug fix in miners.db rebuild
2. Windows executable file information via version.txt

Note: Make sure you delete your existing miner.db file before you run this update of the tool (or overwrite it with the one provided)

Version 0.40 Changes 02/04/2017

1. Change of install location to a sub folder of the Bismuth main folder. It is recommended you call this folder "tools" 
2. Bug fix in miners.db rebuild
3. Bug fix in miner naming process due to removal of base64encode in Bismuth code.

Note: Make sure you delete your existing miner.db file before you run this update of the tool

Version 0.41 Changes 07/04/2017
 
1. Bug fix in miners.db rebuild

Note: Make sure you delete your existing miner.db file before you run this update of the tool

Version 0.42 Changes 17/04/2017
 
1. Bug fix in miners.db rebuild
2. Pythonic improvements (ongoing)
3. Initial test code for sponsors / advertisers in web tools - more information provided later (for the moment this is switched off)

Note: Make sure you delete your existing miner.db file before you run this update of the tool

Future Improvements:

1. Deliver future executable releases using an installer program (version 0.5)
2. Even better menus and menu content
3. Network information
4. Opt-in advertising function - get paid in Bismuth after testing phase
