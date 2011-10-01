from win32com.client import Dispatch
import os
from os.path import join, getsize
import re
import shutil

shell = Dispatch('WScript.Shell')

# exif stuff goes here

cwd = os.getcwd()
cwd_files = join(cwd, "files")
print cwd, cwd_files
date_dir = 'C:\Users\scherer\Desktop\Karl\copy'
dirs_to_search = 'C:\Users\scherer\Desktop\Karl\copy'

for root, dirs, files in os.walk(dirs_to_search):

#    print sum(getsize(join(root, name)) for name in files),
#    print "bytes in\t", len(files), " files \t",
#    print root
    lnk = 0
    non_lnk = 0
#    for name in os.listdir(dirs_to_search):
    for name in files:
        if re.search('\.lnk', name, re.I) == None:
            print "NOT LNK\t", name
            non_lnk = non_lnk + 1                   
        else:
            lnk = lnk + 1
            print name," Target: ",
            shortcut = shell.CreateShortCut(join(date_dir, name))
            print "EXIST\t", shortcut.Targetpath,"\n" 
            shutil.copy2(shortcut.Targetpath, date_dir)
            os.remove(join(date_dir, name))
            
    print "number of lnk files = ", lnk, " others = ", non_lnk


