@echo off
if [%1] == [] (
   echo Must pass in the working directory as the first parameter
   exit /b 1
)
if NOT EXIST %1 (
   echo Must pass in a valid working directory as the first parameter
   exit /b 1
)
if "%computername%" == "DT-WIN10" (
   goto known_machine
)
if "%computername%" == "KVENNER-X1" (
   goto known_machine
)
if "%computername%" == "KVENNER-LENOVO1" (
   call kv-activate
   goto known_machine
)
if "%computername%" == "DT-WIN11" (
   call kv-activate
   goto known_machine
)
echo Running on a machine we have not seen yet: %computername%
exit /b 1
:known_machine
rem run from machine with dropbox installed
python jpgreorder.py adddate=True workingdir=%1
rem show what was created
type file.bat
@echo off
rem
echo .
echo run the file:  file.bat
rem eof
