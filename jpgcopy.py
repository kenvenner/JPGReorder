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
import shutil

# logging - 
import sys
import kvlogger
config=kvlogger.get_config(kvutil.filename_create(__file__, filename_ext='log', path_blank=True), loggerlevel='DEBUG')
kvlogger.dictConfig(config)
logger=kvlogger.getLogger(__name__)

# added logging feature to capture and log unhandled exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception



# defineded list of collections we can create
collections = {
    'Houghton' : [
        re.compile(r'Houghton', re.IGNORECASE),
        re.compile(r'Zack', re.IGNORECASE),
        re.compile(r'Karli', re.IGNORECASE),
    ],
    'Colella' : [
        re.compile(r'Colella', re.IGNORECASE),
        re.compile(r'Jordan', re.IGNORECASE),
        re.compile(r'Whit', re.IGNORECASE),
    ],
    'Superbowl' : [
        re.compile(r'Superbowl', re.IGNORECASE),
    ],
}



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
    'outrootdir' : {
        'value' : r'D:\JPG-Pictures',
        'description' : 'defines the root directory where folders of JPG files exist',
    },
    'usbrootdir' : {
        'value' : 'I:\\',
        'description' : 'defines the root directory where folders of JPG files exist',
    },
    'usbcopy' : {
        'value' : False,
        'type'  : 'bool',
        'description' : 'flag controls how this run works - True - copy folders to USB - False - consolidated copy locally',
    },
    'dirname' : {
        'value' : None,
        'type'  : 'inlist',
        'valid' : list(collections.keys()),
        'description' : 'defines the collection we are processing for from a predefined list',
    },
    'makecmd' : {
        'value' : True,
        'type'  : 'bool',
        'description' : 'flag, when true - generates commands to copy, when false executes the file copies'
    },
    'outfile' : {
        'value' : 'file.bat',
        'description' : 'output filename that holds commands generated',
    },
        
}


# module variables
re_date=re.compile(r'^\d\d\d\d-\d\d-\d\d')

# global variables
createdoutdir = []
actionlist = []

# in 2020 we are +1, and in 2021 we are -1
moveyear=1

# create the commands that will create directories and copy files
def add_directory_actions( subdir, outdir, actionlist, createdoutdir ):
    # create commands to copy over the files
    # create the directory if we have not seen it yet
    if not outdir in createdoutdir:
        actionlist.append('mkdir "{}"'.format(outdir))
        createdoutdir.append(outdir)
    # finally copy out the files
    actionlist.append('copy "{}\*.*" "{}"'.format(subdir, outdir))

# check files in both locations and copy if required
def copy_files_if_newer( subdir, outdir, optiondict ):
    copyfilecnt = 0
    
    # check to see output directory exists - if not - create
    if not os.path.isdir(outdir):
        logger.debug('create outdir:%s', outdir)
        # create the output directory - it does not exist
        try:
            os.makedirs( outdir )
        except Exception as e:
            logger.error('makedirs:%s' % e)
            raise e
    # get the list of files in the input folder
    dirlist = kvutil.filename_list( None, None, fileglob=os.path.join(subdir,'*') )

    # step through files and determine if we need to copy
    for file in dirlist:
        # create a filename in the output directory
        outfile = kvutil.filename_create( file, filename_path=outdir )
        # see if file is in the output directory already and its mtime >= the original file
        if os.path.exists(outfile) and os.path.getmtime(outfile) >= os.path.getmtime(file):
            # logger.debug('file exists no need to copy:%s', file)
            continue

        # need to copy over this file to the output directory
        if optiondict['test']:
            logger.info('copy %s to %s', file,outfile)
        else:
            shutil.copy(file, outfile)
            logger.debug('copy %s to %s', file,outfile)
        copyfilecnt += 1

    # return the count of files copied for this directory
    return copyfilecnt


# ---------------------------------------------------------------------------
if __name__ == '__main__':

    # capture the command line
    optiondict = kvutil.kv_parse_command_line( optiondictconfig, raise_error=True, debug=False )

    # test that dirname is set
    if not optiondict['dirname']:
        logger.warning('dirname must be set - valid values:%s', list(collections.keys()))
        print('dirname must be set - valid values:', ','.join(list(collections.keys())))
        sys.exit()

    # assure folder on inputs
    for fld in ['jpgrootdir','outrootdir','usbrootdir']:
        if optiondict[fld] and optiondict[fld][:-1] != '\\':
            logger.debug('add ending path symbol to variable:%s', fld)
            optiondict[fld] += '\\'

    # convert options into variables
    rootdir = optiondict['jpgrootdir']
    dirname = optiondict['dirname']
    matchlist = collections[optiondict['dirname']]
    outrootdir = optiondict['outrootdir']
    usbdrive = optiondict['usbrootdir']
    usbcopy = optiondict['usbcopy']

    # local variables
    copiedfilecnt = 0
    
    # debbuging
    logger.debug('rootdir:%s', optiondict['jpgrootdir'])
    logger.debug('dirname:%s', optiondict['dirname'])
    logger.debug('matchlist:%s', collections[optiondict['dirname']])
    logger.debug('outrootdir:%s', optiondict['outrootdir'])
    logger.debug('usbdrive:%s', optiondict['usbrootdir'])
    logger.debug('usbcopy:%s', optiondict['usbcopy'])
    
    # get the directories with the path included
    dirlist = kvutil.filename_list( None, None, fileglob=rootdir+'*' )

    # debugging
    logger.debug('number of directories:%d', len(dirlist))
    
    # step through these entries
    for subdir in dirlist:
        # working directories not files
        if not os.path.isdir(subdir):
            logger.debug('skipped - not a directory:%s', subdir)
            continue

        # extract the year out of the subdir
        year = os.path.basename(subdir)[:4]

        # and if this is not a year we start with skip this directory
        if not year.isdigit():
            logger.debug('skipped - does not start with year:%s', subdir)
            continue


        # make the year groups for local consolidation copies
        # we are doing two years per folder
        if int(year)%2:
            outyear = str(int(year)+moveyear)
            outfolder='{}-{}-{}'.format(dirname,outyear,year)
        else:
            outyear = str(int(year)-moveyear)
            outfolder='{}-{}-{}'.format(dirname,year,outyear)

        # build the output directory full path
        if usbcopy:
            outdir=os.path.join(usbdrive,os.path.basename(subdir))
        else:
            outdir=os.path.join(outrootdir,outfolder)

        # debugging
        logger.debug('outfolder:%s', outfolder)
        logger.debug('outdir:%s', outdir)
        logger.debug('subdir:%s', subdir)

        # check to see if this subdirectory matches the dirname we are looking to process
        for re in matchlist:
            if re.search(subdir):
                logger.debug('match:%s', re)
                # we are done looking for a match
                if optiondict['makecmd']:
                    # capture data to create the batch file
                    add_directory_actions( subdir, outdir, actionlist, createdoutdir )
                else:
                    # make the moves directly
                    subdircopiedfilecnt = copy_files_if_newer( subdir, outdir, optiondict )                    
                    if subdircopiedfilecnt:
                        logger.info('files copied:%s:%d', subdir, subdircopiedfilecnt)
                        copiedfilecnt += subdircopiedfilecnt
                             
                # we found the match we are done with this subdir
                break

    # when done - generate the file if we created one
    if optiondict['makecmd']:
        kvjpg.write_action_list_to_file( optiondict['outfile'], actionlist )
        logger.info('Please review and execute:%s', optiondict['outfile'])
    else:
        logger.info('Files copied:%d', copiedfilecnt)

#eof
