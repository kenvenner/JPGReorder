@echo off
if NOT "%computername%" == "DT-WIN10" (
   echo Running on a machine we have not seen yet: %computername%
   exit /b 1
)
rem starting date - last time we extracted files - update after each run
python jpgreorder.py workingdir="C:\Users\ken\Pictures\iCloud Photos\Downloads" copytodir="D:\JPG-Pictures\General Pictures\new" adddate=1 addcnt=0 onlygtdate=06/01/2020

rem date range
rem python jpgreorder.py workingdir="C:\Users\ken\Pictures\iCloud Photos\Downloads" copytodir="D:\JPG-Pictures\General Pictures\new" adddate=1 addcnt=0 onlygtdate=02/02/2019 onlyltdate=02/04/2019
