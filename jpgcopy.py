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
}


# module variables
re_date=re.compile(r'^\d\d\d\d-\d\d-\d\d')
createdoutdir = []

# in 2020 we are +1, and in 2021 we are -1
moveyear=1


# ---------------------------------------------------------------------------
if __name__ == '__main__':

    # capture the command line
    optiondict = kvutil.kv_parse_command_line( optiondictconfig, raise_error=True, debug=False )

    # test that dirname is set
    if not optiondict['dirname']:
        print('dirname must be set - valid values:', ','.join(list(collections.keys())))
        sys.exit()

    # assure folder on inputs
    for fld in ['jpgrootdir','outrootdir','usbrootdir']:
        if optiondict[fld] and optiondict[fld][:-1] != '\\':
            optiondict[fld] += '\\'

    # convert options into variables
    rootdir = optiondict['jpgrootdir']
    dirname = optiondict['dirname']
    matchlist = collections[optiondict['dirname']]
    outrootdir = optiondict['outrootdir']
    usbdrive = optiondict['usbrootdir']
    usbcopy = optiondict['usbcopy']
    
    # get the directories with the path included
    dirlist = kvutil.filename_list( None, None, fileglob=rootdir+'*' )

    # step through these entries
    for subdir in dirlist:
        # working directories not files
        if not os.path.isdir(subdir):
            continue

        # extract the year out of the subdir
        year = os.path.basename(subdir)[:4]

        # and if this is not a year we start with skip this directory
        if not year.isdigit():
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

        # check to see if this subdirectory matchines the dirname we are looking to process
        for re in matchlist:
            if re.search(subdir):
                # matches - create commands to copy over the files
                # create the directory if we have not seen it yet
                if not outdir in createdoutdir:
                    print('mkdir "{}"'.format(outdir))
                    createdoutdir.append(outdir)
                # finally copy out the files
                print('copy "{}\*.*" "{}"'.format(subdir, outdir))
                # we are done looking for a match
                break

        
#eof
