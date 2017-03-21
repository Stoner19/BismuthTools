# Bismuth Tools | Desktop Edition

This folder contains a desktop version of the Bismuth Tools using Python.
The tool is intended for personal use.

A compiled Windows executable is in releases

No promises are given that the tools will run on your system

Notes:

1. In order to take into account the use of Hyperblocks technology the query components are only designed to use the last 10000 blocks.

A windows executable is provided as part of this release.

Requirements

1. Windows 7 or better
2. Bismuth (a.k.a.) Stallion cryptocurrency installed via the latest installation executable at https://github.com/hclivess/bismuth/releases
3. Python 2.7 and dependencies as detailed at https://bitcointalk.org/index.php?topic=1525078
4. wxpython for your Python 2.7 installation as found here: https://wxpython.org/download.php

File placement

The files should be placed in the /bismuth (formerly /stallion) folder on your Windows installation folder. They could possibly be placed elsewhere but I haven't tested this yet. 

miners.db

On first run, if there is no miners.db then a new one will be created.
Once the update process is complete then click 'Refresh List' to display the new or latest list of miners.

Version 0.2 Improvements 21/03/2017

1. Better help menus
2. Wallet info auto refresh every 5 mins
3. Miner query auto list refresh
4. Ledger query, latest block auto refresh every 5 mins
5. Basic logging to 'tools.log'

Future Improvements:

1. Even better menus and menu content
2. Possibly integrate node and miner functions
3. Wallet functions
3. Linux release with executable
4. Network information
