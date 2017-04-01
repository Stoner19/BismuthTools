cd "C:\Program Files (x86)\Bismuth" 

rem - edit the above line to the path of your files

pyinstaller.exe --uac-admin --onefile --noconsole --log-level=INFO --version-file=version.txt bismuthtools.py --icon=db.ico --hidden-import=ticons

pause
