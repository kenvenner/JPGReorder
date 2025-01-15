'''
@author:   Ken Venner
@contact:  ken@venerllc.com
@version:  1.02

Convert HEIC files to JPG files in the current directory
with command line option to delete original HEIC file


Taken from:  https://gist.github.com/urigoren/b8dc1c944d313444a4ba1efc953db003
             https://stackoverflow.com/questions/65045644/heic-to-jpeg-conversion-with-metadata


'''
import kvutil
import os
from glob import glob

from PIL import Image
from pathlib import Path
from pillow_heif import register_heif_opener, read_heif
from tqdm import tqdm ## progress bar
# from argparse import ArgumentParser ## replace with kvutil command line parser

optiondictconfig = {
    'AppVersion' : {
        'value': '1.01',
        'description' : 'defines the version number for the app',
    },
    'workingdir' : {
        'description' : 'directory we will be processing files from (default: current directory)',
        'type' : 'dir',
    },
    'delete' : {
        'description' : 'flag, if true, remove the HEIC file after conversion',
        'type' : 'bool',
        'value': True,
    },
}

# open the tooling
register_heif_opener()

def convert_heic_to_jpg(optiondict):
    print("Converting HEIC files to JPG")
    files = list(Path(optiondict['workingdir']).glob("*.heic")) + list(Path(optiondict['workingdir']).glob("*.HEIC"))

    if len(files) == 0:
        print("No HEIC files found")
        return

    skipped_files = []
    for f in tqdm(files):
        # check to see the file exits - if not skip
        if not os.path.exists(f):
            continue
        
        # open the image file
        heif_file = read_heif(f)
   
        #create the new image
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )
        
        # create the meta data to add
        # print(heif_file.info.keys())
        dictionary=heif_file.info
        exif_dict=dictionary['exif']
        # debug 
        # print(exif_dict)
    
        # save out the JPG with meta data
        if exif_dict:
            image.save(str(f.with_suffix('.jpg')), "JPEG",  exif=exif_dict)
        else:
            skipped_files.append(f)

        # remove file if requested
        if optiondict['delete']:
            f.unlink()

        # return the skipped files
        return skipped_files
    
def convert_heic_to_jpg_no_exif_data(optiondict):
    print("Converting HEIC files to JPG")
    files = list(Path(optiondict['workingdir']).glob("*.heic")) + list(Path(optiondict['workingdir']).glob("*.HEIC"))

    if len(files) == 0:
        print("No HEIC files found")
        return

    for f in tqdm(files):
        image = Image.open(str(f))
        image.convert('RGB').save(str(f.with_suffix('.jpg')))
        if optiondict['delete']:
            f.unlink()


if __name__ == "__main__":
    # capture the command line
    optiondict = kvutil.kv_parse_command_line( optiondictconfig, raise_error=True, debug=False )

    # set a default value in not specified
    if not optiondict['workingdir']:
        optiondict['workingdir'] = os.path.normpath('.')
     
    skipped_files = convert_heic_to_jpg(optiondict)

    # show waht we skipped
    if skipped_files:
        print('Following files could not be converted')
        for x in skipped_files:
            print(x)
            
