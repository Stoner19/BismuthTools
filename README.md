# BismuthTools

Tools for the Bismuth (a.k.a. Stallion) Cryptocurrency

This repository contains tools I personally use for the Bismuth Cryptocurrency

For license see LICENSE file

The tool is intended for personal use.

See releases for pre-compiled versions

No promises are given that the tools will run on your particular system

Notes:

1. In order to take into account the use of Hyperblocks technology the query components are only designed to use blocks since the latest hyperblock in the ledger.

Requirements

Windows

1. Windows 7 or better
2. Bismuth cryptocurrency installed via the latest installation executable at https://github.com/hclivess/bismuth/releases or run from source
3. Python 2.7 and dependencies as detailed at https://bitcointalk.org/index.php?topic=1525078
4. wxpython for your Python 2.7 installation as found here: https://wxpython.org/download.php

Linux e.g. Ubuntu 16.04 LTS

1. Python 2.7 and dependencies as detailed at https://bitcointalk.org/index.php?topic=1525078
2. wxpython for your Python 2.7 installation as found here: https://wxpython.org/download.php or installed using apt-get
3. The Bismuth cryptocurrency installed from source (some additional python components such as pysocks may be needed depending on your installation)

File placement

The files should be placed in the /bismuth folder on your installation folder. They could possibly be placed elsewhere but I haven't tested this yet. 

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

Future Improvements:

1. Even better menus and menu content
2. Possibly integrate node and miner functions
3. Wallet functions
4. Linux release with executable Done !!
5. Network information
