@echo off
if NOT "%computername%" == "DT-WIN10" (
   echo Running on a machine we have not seen yet: %computername%
   exit /b 1
)
rem run from machine with dropbox installed
python jpgreorder.py workingdir="D:\JPG-Pictures\General Pictures\new" adddate=True
rem show what was created
type file.bat
rem
echo "run the file:  file.bat"
rem eof
