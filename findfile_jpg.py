from win32com.client import Dispatch
import os
from os.path import join, getsize
import re
import pyexiv2

shell = Dispatch('WScript.Shell')

# exif stuff goes here

date_dir = 'C:\Users\scherer\Desktop\Karl\pydate'
dirs_to_search = 'C:\Users\scherer\Desktop\Karl\Taipaw'

for root, dirs, files in os.walk(dirs_to_search):
#    print sum(getsize(join(root, name)) for name in files),
#    print "bytes in\t", len(files), " files \t",
#    print root
    if 'By Date' in dirs:
        dirs.remove('By Date')  # don't visit By Date directories
    if 'Non JPG' in dirs:
        dirs.remove('Non JPG')  # don't visit Non JPG directories
    if 'By Type' in dirs:
        dirs.remove('By Type')  # don't visit By Type directories
    jpg = 0
    non_jpg = 0
    for name in files:
        if re.search('\.jpg', name, re.I) == None:
            print "NOT JPG\t", name
            non_jpg = non_jpg + 1                   
        else:
            jpg = jpg + 1
            #print name, 
            metadata = pyexiv2.ImageMetadata(join(root, name))
            metadata.read()
            if 'Exif.Image.DateTime' in metadata.exif_keys:
                tag = metadata['Exif.Image.DateTime']
                date_taken = '2012_12_12'
            else:
                print "NO EXIF\t", name
                tag = ''
                continue
            if os.path.exists(join(date_dir, date_taken)):
                pass
            else:
                os.mkdir(join(date_dir, date_taken))
            shortcut = shell.CreateShortCut(join(date_dir, date_taken, name + ".lnk"))
            if shortcut.Targetpath == join(root, name):
                print "EXIST\t", shortcut.Targetpath, 
            else:
                print "NEW\t", shortcut, 
                shortcut.Targetpath = join(root, name)
                shortcut.WorkingDirectory = root
                shortcut.save()
            print "\t", tag.value
#            createShortcut(join(path, name + ".lnk"), target=join(root, name), wDir=root)

    print "number of jpg files = ", jpg, " others = ", non_jpg


