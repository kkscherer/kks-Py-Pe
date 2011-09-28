import os
from os.path import join, getsize
import re
print "start"
for root, dirs, files in os.walk('C:\Users\scherer\Desktop\Karl'):
    print sum(getsize(join(root, name)) for name in files),
    print "bytes in\t", len(files), " files \t",
    print root
    for name in files:
        if re.search('\.jpg$', name, re.I) == None:
            print name
    if 'By Date' in dirs:
        dirs.remove('By Date')  # don't visit CVS directories
    if 'Non JPG' in dirs:
        dirs.remove('Non JPG')  # don't visit CVS directories
    if 'By Type' in dirs:
        dirs.remove('By Type')  # don't visit CVS directories
