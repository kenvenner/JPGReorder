'''
@author:   Ken Venner
@contact:  ken@venerllc.com
@version:  1.03

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
        'value' : '1.03',
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
    'outfile' : {
        'value' : 'file.bat',
        'description' : 'output filename that holds commands generated',
    },
}

re_date=re.compile(r'^\d\d\d\d-\d\d-\d\d')


# ---------------------------------------------------------------------------
if __name__ == '__main__':

    # capture the command line
    optiondict = kvutil.kv_parse_command_line( optiondictconfig, raise_error=True, debug=False )

    # convert options into variables
    debug = optiondict['debug']
    rootdir = optiondict['jpgrootdir']

    # local variable
    actionlist = []
    
    # get the directories with the path included
    dirlist = kvutil.filename_list( None, None, fileglob=rootdir+'\*' )

    # check that we found any files or report we did not
    if not dirlist:
        logger.warning('No files found:%s', rootdir)
        print('No files found:', rootdir)
        sys.exit()

    # debugging
    logger.debug('number of directories to check:%d', len(dirlist))
    
    # directories to fix
    dir2fix={}
    dircntgood={}
    dircntbad={}
    dircntdate={}
    
    # step through these entries
    for subdir in dirlist:
        # debugging
        logger.debug('subdir:%s', subdir)
        
        # only processing directories not files
        if not os.path.isdir(subdir):
            logger.debug('file not directory - get next entry')
            continue

        # if we are checking date range - grab the subdir date
        if optiondict['chkdaterange']:
            subdirdate = kvjpg.parse_date_from_filename( subdir, defaultdate=None )
            logger.debug('subdirdate:%s', subdirdate)

            
        # set up good/bad count
        if subdir not in dircntbad:
            dircntbad[subdir] = 0
            dircntgood[subdir] = 0
            dircntdate[subdir] = 0
        

            # get the list of files in this directory no path
            subdirlist = kvutil.filename_list( None, None, subdir+'\*.JPG', strippath=True )

            # debugging
            logger.debug('number of files to inspect:%d', len(subdirlist))
            
            # step through the files from this directory
            for file in subdirlist:
                if not re_date.search(file):
                    dir2fix[subdir] = file
                    dircntbad[subdir] += 1
                    logger.debug('no date in filename:%s', file)
                else:
                    dircntgood[subdir] += 1
                    if optiondict['chkdaterange']:
                        filedate = kvjpg.parse_date_from_filename( file, defaultdate=None )
                        if subdirdate and filedate:
                            if abs( (subdirdate-filedate).days ) > optiondict['maxdaysdiff']:
                                dir2fix[subdir] = file
                                dircntdate[subdir] += 1
                                logger.debug('exceeded date diff:%s:fdate:%s:subdate:%s:diff:%d', file,filedate,subdirdate,abs( (subdirdate-filedate).days ))
                        else:
                            logger.debug('one or more dates not set:%s:fdate:%s:subdate:%s',file,filedate,subdirdate)


    # step through folders that need to fixed
    for subdir, file in dir2fix.items():
        actionlist.append('REM defaultdatefrom=subdir datefrom=jpgdefault OR  datefrom=cleanup defaultdatefrom=subdir addcnt=False')
        actionlist.append('REM {} - BadCnt: {} - GoodCnt: {} - DateRangeCnt: {}'.format(file, dircntbad[subdir], dircntgood[subdir], dircntdate[subdir]))
        if optiondict['chkdaterange'] and dircntdate[subdir]:
            actionlist.append('{} workingdir="{}" {}'.format(optiondict['jpgcmdline'], subdir, optiondict['jpgcmdlinedate']))
        else:
            actionlist.append('{} workingdir="{}"'.format(optiondict['jpgcmdline'], subdir))
        actionlist.append('call file')

    # we have data - write to file
    if actionlist:
        # save action list to a file - start of the file is the working directory
        kvjpg.write_action_list_to_file( optiondict['outfile'], actionlist )
        
        # communicate you saved the file
        print('Please review:  ', optiondict['outfile'])
        print('Datesort same:  ', sameorder)
    else:
        print('No records found on this run - nothing to take action on')
        
    
#eof
