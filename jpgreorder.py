'''
@author:   Ken Venner
@contact:  ken@venerllc.com
@version:  1.09

Search a user defined directory for a set of files
read the meta data of the files and create a script
used to copy/rename these files.

'''
import kvutil
import kvjpg
import os
import datetime

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


# ability to fast track set a configuration
super_config = {
    ### SUB #####
    # we are using the date from the subdirectory to put dates on records
    # we are leaving the records in the filename order
    # we are NOT looking up the datetime on the JPG files
    'sub' : {
        'datefrom' : 'cleanup',
        'defaultdatefrom' : 'subdir',
        'addcnt' : False,
        'adddate' : True,
    },
}
super_config['subdir'] = super_config['sub']


# program option configuration
optiondictconfig = {
    'AppVersion' : {
        'value': '1.09',
        'description' : 'defines the version number for the app',
    },
    'copytodir' : {
        'description' : 'directory we will copy files into with new filename',
        'type' : 'dir',
    },
    'workingdir' : {
        'description' : 'directory we will be processing files from (default: current directory)',
        'type' : 'dir',
    },
    'fileglob' : {
        'description' : 'file search string (globing)',
    },
    'outfile' : {
        'value' : 'file.bat',
        'description' : 'output filename that holds commands generated',
    },
    'addcnt' : {
        'value' : True,
        'description' : 'flag, if true, output filename includes a count "CNT####-"',
        'type' : 'bool',
    },
    'adddate' :  {
        'value' : False,
        'description' : 'flag, if true, output filename includes a date "YYYY-MM-DD-"',
        'type' : 'bool',
    },
    'timedelta' : {
        'description' : 're.compile_string:offset_seconds_int:range1_int:range2_int_optional',
        # compile string should fully match the filename and have a grouping clause to extract the picture number (e.g. ".*DSC(\d+).*"
        # range1 used if only matching 1 picture, range2 used if you are matching a range of pictures (e.g. :1:10000 is a range)
        # example:  timedelta=".*DSC(\d+).*:3480:3000:4000
        #    - files with DSC in them in the number range from 3000-4000 will have 3480 seconds added to their picture time (58 minutes)
    },
    'onlygtdate' : {
        'description' : 'only process files with an image date greater than this date',
        'type' : 'date',
    },
    'onlyltdate' : {
        'description' : 'only process files with an image date less than this date',
        'type' : 'date',
    },
    'onlynondate' : {
        'description' : 'flag, if true, update only files that do not have dates already',
        'type' : 'bool',
    },
    'datefrom'    : {
        'value'   : 'jpg',
        'description' : 'defines what method used to assign dates to files',
        'type'    : 'inlist',
        'valid'   : ['jpg','jpgdefault','filename','filecreate','forced','cleanup'],
                     # look at kvjpg.py for the explanation on each of these settings
                     # def get_date_sorted_filelists()
    },
    'nonjpgdatefrom'    : {
        'value'   : 'filecreate',
        'description' : 'defines what method used to assign dates to non-JPG files when datefrom is jpg',
        'type'    : 'inlist',
        'valid'   : ['filename','filecreate','forced','cleanup'],
    },
    'defaultdate' : {
        'description' : 'default date to assign to photos when a default is needed',
        'type' : 'date',
    },
    'defaultdatefrom' : {
        'value'   : 'default',
        'description' : 'defines where we get the defaultdate from',
        'type'    : 'inlist',
        'valid'   : ['subdir','now','default','cmdline'],
                     # subdir - take the date from the directory name housing the files
                     # now - take current date/time
                     # default - use epoch (1901-01-01 00:00:01)
                     # cmdline - take the value from defaultdate on the command line
    },
    'debug' : {
        'description' : 'flag, if true, display debugging information',
        'type' : 'bool',
    },
    'super_config' : {
        'description' : 'defines a preconfigured configuration - overrides settings',
        'type'  : 'inlist',
        'valid' : list(super_config.keys()),
    },


    # legacy options - NOT USED
    'alldir' : {
        'description' : 'NOT USED - would be flag to specify to walk file system',
        'type' : 'bool',
    },
    'adate' : {
        'value' : None,
        'description' : 'NOT USED - would be used to capture different meta dates',
        'type' : 'bool',
    },
        
    'allfiles' : {
        'value' : None,
        'description' : 'NOT USED',
        'type' : 'bool',
    },
    'recount' :  {
        'value' : None,
        'description' : 'NOT USED',
        'olddescription' : 'flag, if true, file date taken from filename, if false, date takeing from file meta data',
        'type' : 'bool',
    },

}

# the remapping of command line options to their proper value
keymapdict = {
    'superconfig' : 'super_config',
}



# function to set the default date based on how the user defined it should be set
def calc_default_date( optiondict ):
    logger.debug('defaultdatefrom:%s', optiondict['defaultdatefrom'])
    if optiondict['defaultdatefrom']=='cmdline':
        if not optiondict['defaultdate']:
            logger.error('defaultdatefrom set to cmdline but no defaultdate passed in')
            raise Exception('defaultdatefrom set to cmdline but no defaultdate passed in')
        return optiondict['defaultdate']
    elif optiondict['defaultdatefrom']=='default':
        return kvjpg.defaultdatetime
    elif optiondict['defaultdatefrom']=='now':
        return datetime.datetime.now()
    else:
        # we are pulling the date from the subdirectory we are processing
        if optiondict['workingdir'] != '.':
            wparts = kvutil.filename_splitall( optiondict['workingdir'] )
        else:
            wparts = kvutil.filename_splitall( os.path.abspath('.') )

        # having the parts - we want to extract the date from the last element
        defaultdate = kvjpg.parse_date_from_filename( wparts[-1], None )

        # check to see we got a date back and return it
        if defaultdate:
            return defaultdate

        # if no date returned raise an exception
        logger.error('Date not extracted from folder:%s', wparts[-1])
        raise Exception('Date not extracted from folder:%s', wparts[-1])


# ---------------------------------------------------------------------------
if __name__ == '__main__':

    # capture the command line
    optiondict = kvutil.kv_parse_command_line( optiondictconfig, raise_error=True, keymapdict=keymapdict, debug=False )

    # create a local variable
    debug = optiondict['debug']

    # mark the log for the run
    logger.info('STARTUP(v%s)%s', optiondictconfig['AppVersion']['value'], '-'*40)

    # debugging
    if debug: print('debug-optiondict:', optiondict)

    # filter out legacy values
    for legacyoption in ('alldir','adate','allfiles','recount'):
        if legacyoption in optiondict and optiondict[legacyoption]:
            logger.error('invalid legacy option set:%s', legacyoption)
            raise Exception('invalid legacy option set:%s', legacyoption)
    
    
    # set a default value in not specified
    if not optiondict['workingdir']:
        optiondict['workingdir'] = os.path.normpath('.')
    if not optiondict['fileglob']:
        optiondict['fileglob'] = os.path.join(optiondict['workingdir'], '*.jpg')

    # process superconfigurations if set
    if optiondict['super_config']:
        for key,val in super_config[optiondict['super_config']].items():
            logger.debug('change optiondict key:%s:value:%s', key,val)
            optiondict[key] = val

    # set the default date based on the type of default date
    optiondict['defaultdate'] = calc_default_date(optiondict)
    
    # special processing on options - convert early to fail before processing
    if optiondict['timedelta']:
        if "," in optiondict['timedelta']:
            redelta = optiondict['timedelta'].split(",")
        else:
            redelta = [optiondict['timedelta']]

        time_shifts = list()
        for f_delta in redelta:
            (re_filename, timedelta, pic_range) = kvjpg.parse_optiondict_timedelta( f_delta )
            time_shifts.append((re_filename, timedelta, pic_range))

    # get files as defined by the user
    (filelist, datefilelistsorted, sameorder) = kvjpg.get_date_sorted_filelists( optiondict['fileglob'], datefrom=optiondict['datefrom'], nonjpgdatefrom=optiondict['nonjpgdatefrom'], defaultdate=optiondict['defaultdate'])

    if debug:
        print('optiondict-timedelta: ', optiondict['timedelta'])
        print('timedelta: ', timedelta)
        print('time_shifts:', time_shifts)

    # change the offset on files if enabled
    if optiondict['timedelta']:
        for (re_filename, timedelta, pic_range) in time_shifts:
            for filename_row in datefilelistsorted:
                kvjpg.datetime_offset_for_matching_filename( filename_row, re_filename, datetime.timedelta(seconds=timedelta), pic_range, debug=debug )
            # with offsets changed - sort again
            datefilelistsorted = sorted(datefilelistsorted)

    # filter the list if we were provided a date to filter on
    if optiondict['onlygtdate'] or optiondict['onlyltdate']:
        # set up the max ranges for compare
        gtdate = datetime.datetime(2001,1,1)
        ltdate = datetime.datetime.now()
        
        # adjust these dates if user specified a date
        if optiondict['onlygtdate']:
            gtdate = optiondict['onlygtdate']
        if optiondict['onlyltdate']:
            ltdate = optiondict['onlyltdate']
        
        # now filter the list
        filteredfilelist=[]
        for filename_row in datefilelistsorted:
            if filename_row[0] > gtdate and filename_row[0] < ltdate:
                filteredfilelist.append(filename_row)
        # overwrite the array with the newly created array
        datefilelistsorted = filteredfilelist

    # filter the list to files that don't have dates on them
    if optiondict['onlynondate']:
        datafilelistsorted = [rec for rec in datefileliststored if not kvjpg.parse_date_from_filename( rec[1], defaultdate=None )]

    
    # convert into a list of actions
    actionlist = kvjpg.create_file_action_list( datefilelistsorted,
                                                copytodir=optiondict['copytodir'],
                                                adddate=optiondict['adddate'],
                                                addcnt=optiondict['addcnt'],
                                                debug=debug )
    
    # debugging
    if debug:
        print('filelist------------------------------\n',filelist)
        print('datefilelistsorted--------------------\n',datefilelistsorted)
        print('actionlist----------------------------\n',actionlist)
    
    if actionlist:
        # save action list to a file - start of the file is the working directory
        kvjpg.write_action_list_to_file( optiondict['outfile'], actionlist )
        
        # communicate you saved the file
        print('Please review:  ', optiondict['outfile'])
        print('Datesort same:  ', sameorder)
    else:
        print('No records found on this run - nothing to take action on')
        
#eof
