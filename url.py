import urllib
import urllib2
import sys

def mkdict(**kwargs): # makes generation of data dict easier
  return kwargs  

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' # mask Python agent
headers = { 'User-Agent' : user_agent }		  
url = 'http://ichart.finance.yahoo.com/table.csv' # Yahoo Finance Hist Stock data url

# get Stock symbol from cmd line or interactive input
if len(sys.argv) < 2:
	s = raw_input('Stock:')
else:
        s = sys.argv[1]
s =  str.upper(s)
# see if we should be verbose
if len(sys.argv) > 2 and sys.argv[2] == '-v':
	q = False
else:
	q = True
#
# TODO
# need to adjust dates here (params a b c and d e f)
#

# set up CGI string
data = urllib.urlencode(mkdict(s=s, a=8, b=17, c=2011, d=9, e=10, f=2011, g='d', ignore='.csv'))
if not q :
	print data
# ask Yahoo for data
try:
	req = urllib2.Request(url+"?"+data)  # requires GET request
	#req = urllib2.Request(url, data, headers) # this would be PUT
	response = urllib2.urlopen(req)
	html = response.read()
except :
	print "Couldn't get data for " + s
	sys.exit(2)

# debug only
# print urllib2.Request.get_full_url(req)
# print html
# print response.info()

# parse Yahoo data and write to file
import csv

f=open('C:\Users\scherer\Desktop\imagetools\stocks.csv', 'wb')
spamWriter = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
spamReader = csv.reader(str.splitlines(html), delimiter=',')

for row in spamReader:
    if row[-1] == 'Adj Close' :   # add stock symbol to first line, nice touch
	    row[-1] = row[-1] + " " +s
    if not q :
            print "\t".join(row)
    spamWriter.writerow(row)

f.close()
# we're done
