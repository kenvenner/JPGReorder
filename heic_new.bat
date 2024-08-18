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

rem tell it where to convert
python heic2jpg.py delete=1 workingdir="D:\JPG-Pictures\General Pictures\new"
