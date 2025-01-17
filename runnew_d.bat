@echo off
if "%computername%" == "DT-WIN11" (
   goto known_machine
)
if "%computername%" == "KVENNER-X1" (
   goto known_machine
)

echo Running on a machine we have not seen yet: %computername%
echo Run this on any of the following machines:  DT-WIN11, KVENNER-X1
exit /b 1

:known_machine
call kv-activate

rem run from machine with dropbox installed
python jpgreorder.py workingdir="D:\JPG-Pictures\General Pictures\new" adddate=True
rem show what was created
type file.bat
rem
echo "run the file:  file.bat"
rem eof
