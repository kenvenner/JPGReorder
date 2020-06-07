'''
@author:   Ken Venner
@contact:  ken@venerllc.com
@version:  1.02

Tool used to scan the pictures directories and find folders with pictures not 
in the YYYY-MM-DD filename format and report on them

And then build output that can be used to run tools to update these folders
The output is to STDOUT, but could be piped into a BAT file and used to then 
process the files

'''

import kvutil
import kvjpg
import os
import re

# logging - 
import sys
import kvlogger
config=kvlogger.get_config(kvutil.filename_create(__file__, filename_ext='log', path_blank=True))
kvlogger.dictConfig(config)
logger=kvlogger.getLogger(__name__)

# added logging feature to capture and log unhandled exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception




# application variables
optiondictconfig = {
    'AppVersion' : {
        'value' : '1.02',
        'description' : 'defines the version number for the app',
    },
    'test' : {
        'value' : False,
        'type'  : 'bool',
        'description' : 'defines if we are running in test mode',
    },
    'debug' : {
        'value' : False,
        'type'  : 'bool',
        'description' : 'defines if we are running in debug mode',
    },
    'verbose' : {
        'value' : 1,
        'type'  : 'int',
        'description' : 'defines the display level for print messages',
    },
    'jpgrootdir' : {
        'value' : r'D:\JPG-Pictures\General Pictures',
        'description' : 'defines the root directory where folders of JPG files exist',
    },
    'jpgcmdline' : {
        'value' : r'python C:\Users\ken\Dropbox\LinuxShare\JPGReorder\jpgreorder.py adddate=True',
        'description' : 'defines the command line used to convert a folder of JPG',
    },
    'jpgcmdlinedate' : {
        'value' : r'super_config=sub',
        'description' : 'defines the command line used to convert a folder of JPG',
    },
    'chkdaterange' : {
        'value' : True,
        'type'  : 'bool',
        'description' : 'defines if we validating dates in filenames are within range of the subdir',
    },
    'maxdaysdiff' : {
        'value' : 14,
        'type'  : 'int',
        'description' : 'defines the max number of days difference before we are out of range',
    },
}

re_date=re.compile(r'^\d\d\d\d-\d\d-\d\d')


# ---------------------------------------------------------------------------
if __name__ == '__main__':

    # capture the command line
    optiondict = kvutil.kv_parse_command_line( optiondictconfig, raise_error=True, debug=False )

    debug = optiondict['debug']
    
    # convert options into variables
    rootdir = optiondict['jpgrootdir']
    
    # get the directories with the path included
    dirlist = kvutil.filename_list( None, None, fileglob=rootdir+'\*' )

    # check that we found any files or report we did not
    if not dirlist:
        print('No files found:%s', rootdir)
        sys.exit()
        
    # directories to fix
    dir2fix={}
    dircntgood={}
    dircntbad={}
    dircntdate={}
    
    # step through these entries
    for subdir in dirlist:
        # only processing directories not files
        if not os.path.isdir(subdir):
            continue

        # if we are checking date range - grab the subdir date
        if optiondict['chkdaterange']:
            subdirdate = kvjpg.parse_date_from_filename( subdir, defaultdate=None )
            
        # set up good/bad count
        if subdir not in dircntbad:
            dircntbad[subdir] = 0
            dircntgood[subdir] = 0
            dircntdate[subdir] = 0
        

            # get the list of files in this directory no path
            subdirlist = kvutil.filename_list( None, None, subdir+'\*.JPG', strippath=True )

            # step through the files from this directory
            for file in subdirlist:
                if not re_date.search(file):
                    dir2fix[subdir] = file
                    dircntbad[subdir] += 1
                else:
                    dircntgood[subdir] += 1
                    if optiondict['chkdaterange']:
                        filedate = kvjpg.parse_date_from_filename( file, defaultdate=None )
                        if subdirdate and filedate:
                            if abs( (subdirdate-filedate).days ) > optiondict['maxdaysdiff']:
                                dir2fix[subdir] = file
                                dircntdate[subdir] += 1


    # step through folders that need to fixed
    for subdir, file in dir2fix.items():
        print('REM defaultdatefrom=subdir datefrom=jpgdefault OR  datefrom=cleanup defaultdatefrom=subdir addcnt=False')
        print('REM {} - BadCnt: {} - GoodCnt: {} - DateRangeCnt: {}'.format(file, dircntbad[subdir], dircntgood[subdir], dircntdate[subdir]))
        if optiondict['chkdaterange'] and dircntdate[subdir]:
            print('{} workingdir="{}" {}'.format(optiondict['jpgcmdline'], subdir, optiondict['jpgcmdlinedate']))
        else:
            print('{} workingdir="{}"'.format(optiondict['jpgcmdline'], subdir))
        print('call file')
    
