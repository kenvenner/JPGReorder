2020-06-06 - new tools

New Tools created

jpgchk4date.py - check the directories and files to find directories needing attention
jpgcopy.py - find and copy out (consolidated directory or to USB) files by collection
jpgreorder.py - rename files based on criteria passed into the program



2020-06-06 - processing new files

1) Copy files to 1 or 2 locations:
   a)  dropbox\PhotosToProcess\new OR
   b)  on dt-win10 machine: D:\JPG-Pictures\General Pictures\new
2) Go to the processing directory for the tools:  dropbox\Linuxshare\JPGReorder
3) Based on where you put the files run the following command:
   a)  runnew_box.bat, then run file.bat
   b)  runnew_d.bat, then run file.bat
4) To capture pictures from debbies icloud account/phone (on the dt-win10 machine)
   a)  icloud.bat, then run file.bat
   b)  EDIT icloud.bat changing the date on onlygtdate to yesterday's date
5) Create folders to store the data on dt-win10



2020-06-06 - jpgreorder.py

- required fields -
workingdir - the source directory where the JPGs to be processed are stored
fileglob - default:  *.jpg - defines the string we use to find files
outfile - default:  file.bat - defines the name of the file created that holds the copy/rename commands

adddate - default:  true - build new filenames with date in the filename name based on datefrom
addcnt - default:  true - build new filenames with counters on them



- optional fields - 
copytodir - when set - defines the directory we are copying files into
timedelta - when set - adjust the timestamp on a defined set of files by the number of seconds specified
onlygtdate - when set - limits processing to only files with an image date greater than the specified date
onlyltdate - when set - limits processing to only files with an image date less than the specified date
onlynondate - when set - limits processing to only files with no date in their filename

- data controls -
datefrom - default: jpg - defines where to get the date from when assigning dates to files
    jpg - from the meta data in the file - if no date set - set to none
    jpgdefault - from the meta data in the file - if not date set - set to the calculated 'defaultdate'
    filename - extract the date from the date in the filename
    filecreate - extract the date from the create date of the file
    forced - set date to the defaultdate passed in for all files with seconds increment in order of sorted files
    cleanup - set the date to the defaultdate passed in for all files,
              but cleanup the filename list, sort again, and seconds set based on this new sorted order
nonjpgdatefrom - default:  filecreate - specifies where we get the date from non JPG files when datefrom=jpg, or reset to match datefrom value
    filename - extract the date from the date in the filename
    filecreate - extract the date from the create date of the file
    forced - set date to the defaultdate passed in for all files with seconds increment in order of sorted files
    cleanup - set the date to the defaultdate passed in for all files,
              but cleanup the filename list, sort again, and seconds set based on this new sorted order
defaultdatefrom - default: default - defines where the default date comes from when we need to assign default date
    subdir - date from the folder name these files are in
    now - take current time stamp
    default - take epoch 1901-01-01
    cmdline - use the date specified via the command line
defaultdate - when set - is the default date used - must be set when defaultdatefrom is set to 'cmdline'

- overall control -
super_config - when set - defines high level set of settings
    sub - reset all filenames to use the date from the subdirectory, have no counter, and be ordered in original filename order
    subdir - same effect as 'sub'





2019-07 New Instructions

1) Put files in the "d:\JPG-Pictures\General Pictures\New" directory
2) Go to:  cd \users\ken\dropbox\linuxshare\jpgreorder
3) run "icloud.bat" - this will prep to move debbies cloud pictures over
4) run "file.bat" - this will copy and rename files
5) edit "icloud.bat" - change the greater than date to yesterdays date
6) rune "runnewc.bat" - this will prep changing filename
7) run "file.bat"
8) Opne explorer twice and move files to new folder that should be moved
9) remove all files that no longer are needed from new directory

======================================

2019 New Python version of this tool:

Go to directory where tool in installed
desktop:
cd \users\ken\dropbox\linuxshare\jpgreorder

SHORTCUT:  just run "runnew.bat" if the files are in "new" directory

Copy down the direcotry you want to process JPG/PNG files from
something like:  \users\ken\Dropbox\PhotosToProcess\new

run the following command

python jpgreorder.py workingdir="\users\ken\Dropbox\PhotosToProcess\new" adddate=True

it will generate a file:

file.bat

look at this file and then run it.

==============================


To use - do the following

Open command window
cd \users\ken\dropbox\linuxshare\jpgreorder
d:
cd "\JPG-Pictures\General Pictures"

go into the directory you want to work with
run the following command:

c:jpgreorder conf=c:dtwin10.conf

then run:

file

and you are done

or if working from dropbox folder

cd \users\ken\dropbox\PhotosToProcess\<directory>
c:\users\ken\dropbox\linuxshare\jpgreorder\jpgreorder conf=c:\users\ken\dropbox\linuxshare\jpgreorder\dtwin10.conf

or if you want dates on the files type the following command
c:\users\ken\dropbox\linuxshare\jpgreorder\jpgreorder conf=c:\users\ken\dropbox\linuxshare\jpgreorder\dtwin10.conf adddate=1

Options:

    # Flags that control behaviors
    alldir => 0,    # if set to 1 - we will find all subdirs under basedir and process them
    changeall => 0, # if set to 1 - we will generate BAT files even when there was no order change in directory
    adddate => 0,   # if set to 1 - we will add the YYYY-MM-DD- to the filename created base on date taken
    rmvdate => 0,   # if set to 1 - we will remove from the originaly file the YYYY-MM-DD- if it exists
    rmvcnt  => 0    # if set to 1 - we will not add back in the count value and change the filename


simplified into a bat file that does it all

renum 

