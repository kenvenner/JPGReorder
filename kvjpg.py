'''
@author:   Ken Venner
@contact:  ken@venerllc.com
@version:  1.08

Library of tools used to process JPG image files
'''


import piexif
import datetime
import glob
import sys
import os
import re

# logging
import logging
logger = logging.getLogger(__name__)


# global variables
AppVersion = '1.08'

debug = False

cntstrfmt = 'CNT%04d0-'
datestrfmt = '%Y-%m-%d-'

cntstrre = re.compile('CNT(\d+)-')
datestrre = re.compile('(\d\d\d\d-\d\d-\d\d)-')

defaultdatetime = datetime.datetime.strptime('1901:01:01 00:00:01', '%Y:%m:%d %H:%M:%S')

# take the string that was passed in on the command line and make needed variables
#
# timedeltastr format:re.compile_string:offset_seconds_int:range1_int:range2_int_optional
#  re.compile_string - string passed into the re.compile command - used to determine if a filename matches
#                      this should extract the picture number associated with pictures that match
#  offset_seconds_int - int number of seconds to change the time on photos that match
#  range1_int - int starting number of photo file that matches the RE
#  range2_int - int (optional) ending number of phone file that matches the RE
#
def parse_optiondict_timedelta( timedeltastr, debug=False ):
    (compile_str,offset_sec,*range_str) = timedeltastr.split(':')
    re_compile=re.compile(compile_str)
    timedelta=int(offset_sec)
    # debugging
    if debug:
        print('range_str:',range_str)
        print('range_str[0]:', range_str[0])
        print('len:', len(range_str))
    logger.debug('range_str:%s',range_str)
    logger.debug('range_str[0]:%s', range_str[0])
    logger.debug('len:%d', len(range_str))

    # parse up what was passed in
    if len(range_str)==2:
        pic_range=range(int(range_str[0]),int(range_str[1]))
    else:
        pic_range=int(range_str[0])
    return(re_compile,timedelta,pic_range)

# routine to pull the date from the filename rather than from the file
def parse_date_from_filename( filename, defaultdate=defaultdatetime, debug=False ):
    # perform matching on filename
    m = re.search(datestrre, filename)
    s = re.search(cntstrre, filename)
    # debug
    if debug:
        print('filename:',filename)
        print('m',m)
        if m:  print('m.group0:', m.group(0))
        if m:  print('m.group1:', m.group(1))
        print('s',s)
        if s:  print('s.group0:', s.group(0))
        if s:  print('s.group1:', s.group(1))
    logger.debug('filename:%s',filename)
    logger.debug('m:%s',m)
    if m:
        logger.debug('m.group0:%s' ,m.group(0))
        logger.debug('m.group1:%s' ,m.group(1))
    logger.debug('s:%s',s)
    if s:
        logger.debug('s.group0:%s', s.group(0))
        logger.debug('s.group1:%s', s.group(1))

    # check for match on date in filename
    if m:
        # check for match on count in filename
        if s:
            # debugging
            logger.debug('date and count to build the time')
            # we are using filename date and cnt to build the time
            return datetime.datetime.strptime(m.group(1), '%Y-%m-%d') + datetime.timedelta(seconds=int(s.group(1)))
        else:
            # debugging
            logger.debug('date only builds the time')
            # we are using justfilename date to build the time
            return datetime.datetime.strptime(m.group(1), '%Y-%m-%d')
    else:
        # debugging
        logger.debug('default date builds the time')
        # we are using the default date to build the time
        return defaultdate
    
# bust up the filename and strip previously implemented strings in the basename
def parse_cleanup_filename( filename, debug=False ):
    # split the filename up
    (dirname, basename) = os.path.split(filename)
    if debug:
        print('parse_cleanup_filename:dirname:', dirname)
        print('parse_cleanup_filename:basename:', basename)
    logger.debug('dirname:%s', dirname)
    logger.debug('basename:%s', basename)
    # make dirname normal path
    dirname = os.path.normpath(dirname)
    # remove CNT in the basename string if it exists
    basename = re.sub( cntstrre, '', basename )
    if debug:  print('parse_cleanup_filename:basename-post-cnt:', basename)
    logger.debug('basename-post-cnt:%s', basename)
    # remove DATESTR in the basename string if it exists
    basename = re.sub( datestrre, '', basename )
    if debug:  print('parse_cleanup_filename:basename-post-date:', basename)
    logger.debug('basename-post-date:%s', basename)
    # return results
    return ( dirname, basename )

# 
# offset the datetime in filename_row[0] by timedelta_offset if the filename in filename_row[1] re.search matches re_filename
#   filename_row = 2 position list [ datetime, filename_str ]
#   re_filename = re.compile() that extracts out the image number (eg. re.compile('IMG_(\d).JPG', re.IGNORECASE))
#   timedelta_offset = datetime.timedelta object (eg. datetime.timedelta(seconds=-30*60) - 30 minute earlier)
#   filerange = int or range of int that defines the re.compile matching values that we apply offset to (eg. 3466 or range(3455,3470)
#
# this routine can be used when two cameras don't have the same date/time in them.  using this will move the time
# date of one cameras picture to align with the timedate of the other camera
#
def datetime_offset_for_matching_filename( filename_row, re_filename, timedelta_offset, filerange, debug=False ):
    if debug:
        print('datetime_offset_for_matching_filename:filename_row:', filename_row)
        print('datetime_offset_for_matching_filename:re_filename:', re_filename)
        print('datetime_offset_for_matching_filename:timedelta_offset:', timedelta_offset)
        print('datetime_offset_for_matching_filename:filerange:', filerange)
        print('datetime_offset_for_matching_filename:filename_row[1]:', filename_row[1])
    logger.debug('filename_row:%s', filename_row)
    logger.debug('re_filename:%s', re_filename)
    logger.debug('timedelta_offset:%s', timedelta_offset)
    logger.debug('filerange:%s', filerange)
    logger.debug('filename_row[1]:%s', filename_row[1])

    m = re.search( re_filename, filename_row[1] )
    if m:
        picture = int(m.group(1))
        if debug:
            print('datetime_offset_for_matching_filename:filename-match: true')
            print('datetime_offset_for_matching_filename:picture:', picture)
            print('datetime_offset_for_matching_filename:filename_row[0]-before:', filename_row[0])
        logger.debug('filename-match: true')
        logger.debug('picture:%s', picture)
        logger.debug('filename_row[0]-before:%s', filename_row[0])
            
        if picture == filerange or picture in filerange:
            # filename match - change the timedate record by offset
            filename_row[0] += timedelta_offset
            if debug:
                print('datetime_offset_for_matching_filename:filename_row[0]-after:', filename_row[0])
            logger.debug('filename_row[0]-after:%s', filename_row[0])
                
        
# display all exif attributes for the file passed in
def display_exif_attributes( filename, debug=False ):
    exif_dict = piexif.load( filename )
    print('ifds:', exif_dict.keys())
    print('ifd : tag : name : value')
    for ifd in ("0th", "Exif", "GPS", "1st"):
        for tag in exif_dict[ifd]:
            print(ifd, ':', tag, ':', piexif.TAGS[ifd][tag]["name"], ':', exif_dict[ifd][tag])

    
# default:  get the DateTime out of JPG meta data
def get_exif_attribute_from_jpg( fn, ifd='0th', tag=306, debug=False ):
    exif_dict = piexif.load(fn)
    # convert the attributes to a datetime object if its name is datetime
    if 'DateTime' in piexif.TAGS[ifd][tag]["name"]:
        try:
            return datetime.datetime.strptime(exif_dict[ifd][tag].decode("utf-8") , '%Y:%m:%d %H:%M:%S')
        except Exception:
            return datetime.datetime.now()
    # if not converted - return the value
    return exif_dict[ifd][tag]


# get the DateTime out of JPG meta data
def get_exif_datetime_attribute_from_jpg( fn, ifd='0th', tag=306, defaultdate=datetime.datetime.now(), debug=False ):
    exif_dict = piexif.load(fn)
    # convert the attributes to a datetime object if its name is datetime
    if 'DateTime' in piexif.TAGS[ifd][tag]["name"]:
        try:
            return datetime.datetime.strptime(exif_dict[ifd][tag].decode("utf-8"), '%Y:%m:%d %H:%M:%S')
        except Exception:
            logger.debug('failed to convert DateTime - used default')
            return defaultdate
    # if not converted - return the value
    logger.debug('not datetime converted')
    return exif_dict[ifd][tag]

# create a sorted list of filenames based on cleaned up file names
def sorted_filelist_by_cleanedup_filename( filelist ):
    # create a new list that has the dir, clean_filename, orig_filename
    # the '*' infront of the fuction is because we want to expand out the tuple passed back
    newlist = [ [*parse_cleanup_filename(file), file] for file in filelist ]
    # take this list sort it, extract out the orig_filenaem and return that result
    sortedlist = [ filerow[2] for filerow in sorted(newlist) ]
    return sortedlist

# process a list of files
#   datefrom - specifies where we get the date from
#     jpg - read the value from the meta data in the file (use datefrom strategy when the date does not exist in the file)
#     jpgdefault - read the value from the meta data in the file (use defaultdate when meta data does not exist)
#     filename - read the value from the date in the filename itself (use default date if filename does not have date)
#     filecreate - read the file create date date/time and use this to set the fdate
#     forced - set date to the defaultdate passed in for all files with seconds increment in order of sorted files
#     cleanup - set the date to the defaultdate passed in for all files,
#               but cleanup the filename list, sort again, and seconds set based on this new sorted order
#   nonjpgdatefrom - specifies where we get the date from non JPG files when datefrom=jpg, or reset to match datefrom value
#     << same values as datefrom without jpg or jpgdefault as valid values>>
#
def get_date_sorted_filelists( fileglob, datefrom='jpg', nonjpgdatefrom='filecreate', defaultdate=datetime.datetime.now(), debug=False  ):
    # local variable
    datefilelist = []

    # debugging
    logger.debug('defaultdate:%s', defaultdate)

    # set the default date for jpg file lookup
    jpgdefaultdate = None
    if datefrom == 'jpgdefault':   jpgdefaultdate = defaultdate
    logger.debug('jgpdefaultdate:%s', jpgdefaultdate)
    
    # update/change nonjpgdatefrom if datefrom is not jpg
    if not 'jpg' in datefrom:
        nonjpgdatefrom = datefrom
        logger.debug('set nonjpgdatefrom to value from datefrom:%s', datefrom)
        
    # pull the filelist and sort by filename from filesystem
    filelist = sorted(glob.glob( fileglob ))

    # if we running in cleanup mode, then resort the list
    if datefrom=='cleanup':
        filelist = sorted_filelist_by_cleanedup_filename( filelist )
        logger.debug('resort the file list with cleanedup filenames')

    # step through this list of files - and grab a date associated with each file
    filecnt = 0
    for fname in filelist:
        filecnt += 1
        fdate = None
        # JPG processing first
        if fname.lower().endswith('.jpg') and 'jpg' in datefrom:
            # get file date of the picture form meta data
            # and set the default date properl
            fdate = get_exif_datetime_attribute_from_jpg( fname, defaultdate=jpgdefaultdate )

        # if the fdate is set, save it and loop again
        if fdate:
            logger.debug('fdate set by jpg meta data:%s:%s', fname, fdate)
            datefilelist.append([fdate, fname])
            continue

        # if the fdate is not set - lets set the fdate based on the nonjpgdatefrom strategy
        if nonjpgdatefrom == 'filename':
            # the date we use is pulled from the filename
            fdate = parse_date_from_filename( fname, defaultdate )
            # debugging
            logger.debug('fdate set by %s:%s:%s', nonjpgdatefrom, fname, fdate)
        elif nonjpgdatefrom=='filecreate':
            # the date is pulled from the file create date
            # works for windows os - not sure this will work on linux/macos
            # TODO - update this to be platform independent
            fdate = datetime.datetime.fromtimestamp(os.path.getctime( fname ) )
            logger.debug('fdate set by %s:%s:%s', nonjpgdatefrom, fname, fdate)
        elif nonjpgdatefrom in ('forced', 'cleanup'):
            # we are forcing the date to the same date - that which was passed in
            # are adding a second to each entry to give us a sort order that aligns with how this list is storted
            fdate = defaultdate +  datetime.timedelta(seconds=filecnt)
            logger.debug('fdate set by %s:%s:%s', nonjpgdatefrom, fname, fdate)
        else:
            # we have a defaultdate type we don't know - raise exception
            raise Exception('unknown defaultdate:%s',nonjpgdatefrom)

        # add this record to list
        datefilelist.append([fdate, fname])

    # create sorted list
    datefilelistsorted = sorted(datefilelist)

    # determine if they are different orders based on date/time sort and flag if they are
    sameorder=True
    for idx in range(len(datefilelist)):
        if datefilelistsorted[idx][1] != datefilelist[idx][1]:
            logger.debug('%s:%s:%s', idx,datefilelistsorted[idx][1],datefilelist[idx][1])
            sameorder=False
            break
        

    # return the two lists
    return (filelist, datefilelistsorted, sameorder)

    
# create list of actions to be taken
def create_file_action_list( datefilelistsorted, copytodir=None, adddate=False, addcnt=True, debug=False ):
    datestr=''
    cntstr=''
    if copytodir:
        actionstr = 'copy'
        copytodir = os.path.normpath(copytodir)
    else:
        actionstr = 'ren'
    filecnt = 0
    actionline = []
    
    # step through the files
    for (fdate, fname) in datefilelistsorted:
        # increment the file counter
        filecnt += 1

        # calc the date string
        if adddate:
            datestr = datetime.datetime.strftime(fdate, datestrfmt)

        # calc the counter string
        if addcnt:
            cntstr = cntstrfmt % filecnt

        # split up the current fname
        (dirname, basename) = parse_cleanup_filename( fname )

        # put it back togehter
        # fname = os.path.join( dirname, basename )

        # make the input filename normal path structure
        fname = os.path.normpath( fname )

        # create the new basename
        basenamenew = ''.join((datestr,cntstr,basename))

        # create the output filename
        if copytodir:
            fnamenew = os.path.join( copytodir, basenamenew )
        else:
            # learning - you DON'T put the path into the new name when renaming
            #fnamenew = os.path.join( dirname, basenamenew )
            fnamenew = basenamenew
            
        # calculate the file string
        actionline.append('%s "%s" "%s"' % (actionstr, fname, fnamenew))

    # when done return the list
    return actionline

# take action list nad write it out of a file
def write_action_list_to_file( filename, actionlist, workingdir=None, debug=False ):
    with open( filename, 'w' ) as out:
        if workingdir:
            out.write('cd "' + workingdir + '"\n')
        out.write('\n'.join(actionlist))

if __name__ == '__main__':
    #filelist = build_bat_reorder_by_datetaken( '*.*' )
    (filelist,sortedfilelist) = get_date_sorted_filelists( '*.*' )
    print('filelist:', filelist)
    print('sortedfilelist:', sortedfilelist)
    save_file_change( sortedfilelist, 'file.bat', True )
    
    jpgdate = get_exif_attribute_from_jpg( "IMG_2666.JPG" )
    print(type(jpgdate))
    print(jpgdate)
    sys.exit()
    

#eof
