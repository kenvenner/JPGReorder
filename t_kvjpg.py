import kvjpg
import unittest
import datetime
import os
import re

__version__ = '1.05'

datestr = '2018-10-18'
dateval = datetime.datetime.strptime(datestr, '%Y-%m-%d')
dirstr  = os.path.normpath('c:/test/test1')
cntstr  = 'CNT00010'

# required files to make this test work:
# 2019-11-02-CNT00340-DSC02121.JPG
# 2019-11-02-CNT00540-IMG_5260.JPG
# IMG_2666.JPG

class TestKVJpg(unittest.TestCase):

    def test_parse_optiondict_timedelta_p01_simple(self):
        self.assertEqual( kvjpg.parse_optiondict_timedelta( 'IMG_(\d+).JPG:-1800:3450:3470' ), (re.compile('IMG_(\d+).JPG'),-1800,range(3450,3470)))
    def test_parse_optiondict_timedelta_p02_single_value(self):
        self.assertEqual( kvjpg.parse_optiondict_timedelta( 'IMG_(\d+).JPG:-1800:3450' ), (re.compile('IMG_(\d+).JPG'),-1800,3450))
        
    def test_parse_date_from_filename_p01_simple_with_date(self):
        self.assertEqual( kvjpg.parse_date_from_filename( datestr + '-Ken.jpg'), dateval)
    def test_parse_date_from_filename_p02_simple_with_no_date(self):
        self.assertEqual( kvjpg.parse_date_from_filename( 'Ken.jpg'), kvjpg.defaultdatetime)
    def test_parse_date_from_filename_p03_simple_with_no_date_pass_datetime(self):
        passdatetime=datetime.datetime.now()
        self.assertEqual( kvjpg.parse_date_from_filename( 'Ken.jpg', defaultdate=passdatetime), passdatetime)
    def test_parse_date_from_filename_p04_simple_with_date_and_cnt(self):
        self.assertEqual( kvjpg.parse_date_from_filename( datestr + '-CNT00010-Ken.jpg'), dateval + datetime.timedelta(seconds=10))

    def test_parse_cleanup_filename_p01_simple(self):
        self.assertEqual( kvjpg.parse_cleanup_filename( datestr + '-CNT00040-Ken.jpg'), ('.', 'Ken.jpg') )
        self.assertEqual( kvjpg.parse_cleanup_filename( '-CNT00040-Ken.jpg'), ('.', '-Ken.jpg') )
        self.assertEqual( kvjpg.parse_cleanup_filename( 'CNT00040-Ken.jpg'), ('.', 'Ken.jpg') )
        self.assertEqual( kvjpg.parse_cleanup_filename( 'CNT0004-Ken.jpg'), ('.', 'Ken.jpg') )
        self.assertEqual( kvjpg.parse_cleanup_filename( 'CNT4-Ken.jpg'), ('.', 'Ken.jpg') )
        self.assertEqual( kvjpg.parse_cleanup_filename( 'CNT-Ken.jpg'), ('.', 'CNT-Ken.jpg') )
        self.assertEqual( kvjpg.parse_cleanup_filename( 'Ken.jpg'), ('.', 'Ken.jpg') )

    def test_parse_cleanup_filename_p01_with_dir(self):
        self.assertEqual( kvjpg.parse_cleanup_filename( os.path.join(dirstr, datestr + '-CNT00040-Ken.jpg')), (dirstr, 'Ken.jpg') )
        self.assertEqual( kvjpg.parse_cleanup_filename( os.path.join(dirstr, '-CNT00040-Ken.jpg')), (dirstr, '-Ken.jpg') )
        self.assertEqual( kvjpg.parse_cleanup_filename( os.path.join(dirstr, 'CNT00040-Ken.jpg')), (dirstr, 'Ken.jpg') )
        self.assertEqual( kvjpg.parse_cleanup_filename( os.path.join(dirstr, 'CNT0004-Ken.jpg')), (dirstr, 'Ken.jpg') )
        self.assertEqual( kvjpg.parse_cleanup_filename( os.path.join(dirstr, 'CNT4-Ken.jpg')), (dirstr, 'Ken.jpg') )
        self.assertEqual( kvjpg.parse_cleanup_filename( os.path.join(dirstr, 'CNT-Ken.jpg')), (dirstr, 'CNT-Ken.jpg') )
        self.assertEqual( kvjpg.parse_cleanup_filename( os.path.join(dirstr, 'Ken.jpg')), (dirstr, 'Ken.jpg') )        

    def test_datetime_offset_for_matching_filename_p01_match_exact(self):
        filerow = [datetime.datetime(2018, 10, 15, 11, 29, 51, 560672),'IMG_3466.JPG']
        kvjpg.datetime_offset_for_matching_filename( filerow, re.compile('IMG_(\d+).JPG'), datetime.timedelta(seconds=-30*60), 3466)
        self.assertEqual( filerow[0], datetime.datetime(2018, 10, 15, 10, 59, 51, 560672) )
    def test_datetime_offset_for_matching_filename_p02_match_range(self):
        filerow = [datetime.datetime(2018, 10, 15, 11, 29, 51, 560672),'IMG_3466.JPG']
        kvjpg.datetime_offset_for_matching_filename( filerow, re.compile('IMG_(\d+).JPG'), datetime.timedelta(seconds=-30*60), range(3450,3470))
        self.assertEqual( filerow[0], datetime.datetime(2018, 10, 15, 10, 59, 51, 560672) )
    def test_datetime_offset_for_matching_filename_p03_nomatch(self):
        filerow = [datetime.datetime(2018, 10, 15, 11, 29, 51, 560672),'IMG_3466.JPG']
        kvjpg.datetime_offset_for_matching_filename( filerow, re.compile('IMG_4\d\d\d.JPG'), datetime.timedelta(seconds=-30*60), 4000)
        self.assertEqual( filerow[0], datetime.datetime(2018, 10, 15, 11, 29, 51, 560672) )
    def test_datetime_offset_for_matching_filename_f01_match_exact_no_group(self):
        with self.assertRaises(Exception) as context:
            filerow = [datetime.datetime(2018, 10, 15, 11, 29, 51, 560672),'IMG_3466.JPG']
            kvjpg.datetime_offset_for_matching_filename( filerow, re.compile('IMG_\d+.JPG'), datetime.timedelta(seconds=-30*60), 3466)

    #def test_display_exif_attributes_p01_simple(self):
        #self.assertIsNone( kvjpg.display_exif_attributes("IMG_2666.JPG") )

    def test_get_exif_datetime_attribute_from_jpg_p01_simple(self):
        self.assertEqual(kvjpg.get_exif_datetime_attribute_from_jpg('2019-11-02-CNT00340-DSC02121.JPG', debug=True), datetime.datetime(2019, 11, 2, 4, 32, 15))


    def test_get_date_sorted_filelists_p01_simple(self):
        (filelist, datefilelistsorted, sameorder) = kvjpg.get_date_sorted_filelists( '*.jpg' )
        # based on files in C:\Users\ken\Dropbox\LinuxShare\JPGReorder
        self.assertEqual(filelist[-1], 'IMG_2666.JPG')  
        self.assertEqual(datefilelistsorted[0][1], 'IMG_2666.JPG')
    def test_get_date_sorted_filelists_p02_cleanup(self):
        (filelist, datefilelistsorted, sameorder) = kvjpg.get_date_sorted_filelists( '*.jpg', datefrom='cleanup' )
        # based on files in C:\Users\ken\Dropbox\LinuxShare\JPGReorder
        self.assertEqual(filelist[-1], '2019-11-02-CNT00540-IMG_5260.JPG')  
        self.assertEqual(datefilelistsorted[1][1], 'IMG_2666.JPG')
        

    def test_create_file_action_list_p01_ren_simple(self):
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join(dirstr,'IMG_2666.JPG')]], )[0],
                          'ren "c:\\test\\test1\\IMG_2666.JPG" "CNT00010-IMG_2666.JPG"')
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join('','IMG_2666.JPG')]], )[0],
                          'ren "IMG_2666.JPG" "CNT00010-IMG_2666.JPG"')
    def test_create_file_action_list_p02_ren_adddate_fullpath(self):
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join(dirstr,'IMG_2666.JPG')]], adddate=True)[0],
                          'ren "c:\\test\\test1\\IMG_2666.JPG" "2018-10-18-CNT00010-IMG_2666.JPG"')
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join('','IMG_2666.JPG')]], adddate=True)[0],
                          'ren "IMG_2666.JPG" "2018-10-18-CNT00010-IMG_2666.JPG"')
    def test_create_file_action_list_p03_ren_simple_infile_cnt(self):
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join(dirstr,cntstr+'-IMG_2666.JPG')]], )[0],
                          'ren "c:\\test\\test1\\'+cntstr+'-IMG_2666.JPG" "CNT00010-IMG_2666.JPG"')
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join('',cntstr+'-IMG_2666.JPG')]], )[0],
                          'ren "'+cntstr+'-IMG_2666.JPG" "CNT00010-IMG_2666.JPG"')
    def test_create_file_action_list_p04_ren_simple_infile_date(self):
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join(dirstr,datestr+'-IMG_2666.JPG')]], )[0],
                          'ren "c:\\test\\test1\\'+datestr+'-IMG_2666.JPG" "CNT00010-IMG_2666.JPG"')
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join('',datestr+'-IMG_2666.JPG')]], )[0],
                          'ren "'+datestr+'-IMG_2666.JPG" "CNT00010-IMG_2666.JPG"')
    def test_create_file_action_list_p05_ren_simple_infile_date_cnt(self):
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join(dirstr,datestr+'-'+cntstr+'-IMG_2666.JPG')]], )[0],
                          'ren "c:\\test\\test1\\'+datestr+'-'+cntstr+'-IMG_2666.JPG" "CNT00010-IMG_2666.JPG"')
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join('',datestr+'-'+cntstr+'-IMG_2666.JPG')]], )[0],
                          'ren "'+datestr+'-'+cntstr+'-IMG_2666.JPG" "CNT00010-IMG_2666.JPG"')

    def test_create_file_action_list_p01_copy_simple(self):
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join(dirstr,'IMG_2666.JPG')]], copytodir='c:/temp')[0],
                          'copy "c:\\test\\test1\\IMG_2666.JPG" "c:\\temp\\CNT00010-IMG_2666.JPG"')
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join('','IMG_2666.JPG')]], copytodir='c:/temp')[0],
                          'copy "IMG_2666.JPG" "c:\\temp\\CNT00010-IMG_2666.JPG"')
    def test_create_file_action_list_p02_copy_adddate_fullpath(self):
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join(dirstr,'IMG_2666.JPG')]], copytodir='c:/temp', adddate=True)[0],
                          'copy "c:\\test\\test1\\IMG_2666.JPG" "c:\\temp\\2018-10-18-CNT00010-IMG_2666.JPG"')
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join('','IMG_2666.JPG')]], copytodir='c:/temp', adddate=True)[0],
                          'copy "IMG_2666.JPG" "c:\\temp\\2018-10-18-CNT00010-IMG_2666.JPG"')
    def test_create_file_action_list_p03_copy_simple_infile_cnt(self):
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join(dirstr,cntstr+'-IMG_2666.JPG')]], copytodir='c:/temp')[0],
                          'copy "c:\\test\\test1\\'+cntstr+'-IMG_2666.JPG" "c:\\temp\\CNT00010-IMG_2666.JPG"')
        self.assertEqual( kvjpg.create_file_action_list( [[dateval,os.path.join('',cntstr+'-IMG_2666.JPG')]], copytodir='c:/temp')[0],
                          'copy "'+cntstr+'-IMG_2666.JPG" "c:\\temp\\CNT00010-IMG_2666.JPG"')


if __name__ == '__main__':
    unittest.main()
