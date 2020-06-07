'''
@author:   Ken Venner
@contact:  ken@venerllc.com
@version:  1.02

Take the copy/rename file created by jpgreorder.py
And convert it to create a new file to revert the changes 
made and return filenames to their original settings

'''
import kvutil
import os
import re

# this program is used to reverse the work done by executing
# jpgreorder.py - getting out file.bat - running this file
# this utility reads in the file.bat file
# and creates a new undofile.bat file that returns
# the changed filenames back to the original order.
#
# to run:  python undofile.py

# program option configuration
optiondictconfig = {
    'AppVersion' : {
        'value' : '1.02',
        'description' : 'defines the version number for the app',
    },
    'infile' : {
        'value' : 'file.bat',
        'description' : 'input filename that holds commands that were generated',
    },
    'outfile' : {
        'value' : 'fileundo.bat',
        'description' : 'output filename that holds translated commands generated',
    },
    'debug' : {
        'description' : 'flag, if true, display debugging information',
        'type' : 'bool',
    },
}

######################## FUNCTIONS ###################################

# Regex not working - getting weird results - just find the four places there are " marks
def new_cmdline_via_find( line, debug=False ):
    # setup array to capture the 4 locatnois we find the " character
    # first element in this array is -1 so on the first loop we start at position zero.
    # the real values come out in index values 1:5
    quoteloc=[]
    quoteloc.append(-1)
    if debug: print('quoteloc:',quoteloc)
    for idx in range(1,5):
        # debugging
        if debug: print('idx:', idx, 'idx-1:', idx-1, 'quote[idx-1]:', quoteloc[idx-1])
        # find the next " character
        quoteloc.append(line.find('"', quoteloc[idx-1]+1))
        # check that we found it and error out if we did not
        if quoteloc[-1] == -1:
            print('Did not find " on interation [%] for string:' % (idx, line))
            raise

    # parse up the found information
    origfilenamefull = line[quoteloc[1]+1:quoteloc[2]]
    newfilename = line[quoteloc[3]+1:quoteloc[4]]
    if debug: print('orig:', origfilenamefull, '\nnew:', newfilename)
    (origpath, origfilename, origext) = kvutil.filename_split( origfilenamefull )
    if debug: print('path:', origpath, '\nfilename:', origfilename)
    returnfilenamefull = os.path.join( origpath, newfilename )
    if debug: print('return:', returnfilenamefull)
    newcmd = 'ren "%s" "%s"' % (returnfilenamefull, origfilename)
    if debug: print( newcmd )

    return newcmd

# find via regex - NOT WORKING ON 2019-01-10;kv
def new_cmdline_via_regex( line, debug=False):
    # create the regex that will pull apart the command line
    reFile = re.compile('ren\s+"([^"]*)"\s+"([^"]*)"')

    # use the regex to find the two filenames
    m = re.File( line )
    # if we did not find the two file names we have a problem
    if not m:
        print('Could not regex line:', line)
        raise
    
    # found the filenames - parse them out
    origfilenamefull = m.group(1)
    newfilename = m.group(2)
    if debug: print('orig:', origfilenamefull, '\nnew:', newfilename)
    (origpath, origfilename) = kvutil.filename_split( origfilenamefull )
    if debug: print('path:', origpath, '\nfilename:', origfilename)
    returnfilenamefull = os.path.join( origpath, newfilename )
    if debug: print('return:', returnfilenamefull)
    newcmd = 'ren "%s" "%s"' % (returnfilenamefull, origfilename)
    if debug: print( newcmd )

    return newcmd


######################## MAIN ###################################

# call the command line parser
optiondict = kvutil.kv_parse_command_line( optiondictconfig, debug=False)

# create a local variable
debug = optiondict['debug']

# debugging
if debug:
    cmdfile = kvutil.slurp( optiondict['infile'] )
    print('cmdfile\n', cmdfile)

# read in the file
cmdlines = kvutil.read_list_from_file_lines( optiondict['infile'] )

# debugging
if debug:
    print('----------------')
    print(cmdlines)
    print('----------------')

# create the output file and write out the results
with open( optiondict['outfile'], 'w' ) as t:
    # for each line, convert to a new command line and save to file
    for line in cmdlines:
        t.write( new_cmdline_via_find( line ) + '\n' )


# message to user
print('New batch file created:', optiondict['outfile'])

# eof


    
    
    
