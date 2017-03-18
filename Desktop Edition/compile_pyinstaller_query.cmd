cd "C:\Program Files (x86)\Bismuth" 

rem - edit the above line to the path of your bismuthtool.py and icons.py files

pyinstaller.exe --uac-admin --onefile --noconsole --log-level=INFO bismuthtool.py --icon=db.ico --hidden-import=icons

pause
