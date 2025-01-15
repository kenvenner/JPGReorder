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

rem starting date - last time we extracted files - update after each run
rem python jpgreorder.py workingdir="D:\JPG-Pictures\iCloud Photos\Downloads" copytodir="D:\JPG-Pictures\General Pictures\new" adddate=1 addcnt=0 onlygtdate=08/17/2024

python jpgreorder.py workingdir="C:\Users\ken\iCloudPhotos\Photos" copytodir="D:\JPG-Pictures\General Pictures\new" adddate=1 addcnt=0 fileglob_glob="*.heic" onlygtdate=01/14/2025
echo Run file.bat, then heic_new.bat


rem date range
rem python jpgreorder.py workingdir="C:\Users\ken\Pictures\iCloud Photos\Downloads" copytodir="D:\JPG-Pictures\General Pictures\new" adddate=1 addcnt=0 onlygtdate=11/12/2022 debug=True

rem date range
rem python jpgreorder.py workingdir="C:\Users\ken\Pictures\iCloud Photos\Downloads" copytodir="D:\JPG-Pictures\General Pictures\new" adddate=1 addcnt=0 onlygtdate=02/02/2019 onlyltdate=02/04/2019
