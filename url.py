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
	ssym = raw_input('Stock:')
else:
        ssym = sys.argv[1]
ssym =  str.upper(ssym)
# see if we should be verbose
if len(sys.argv) > 2 and sys.argv[2] == '-v':
	q = False
else:
	q = True
#
# need to adjust dates here (params a b c and d e f)
# 
days = 130 
bday = days*168/96 # course business day calculation
import datetime
t1 = datetime.date.today()
td = datetime.timedelta(days=bday)
t2 = t1 - td

# set up CGI string
data = urllib.urlencode(mkdict(s=ssym,
                               a=t2.month,
                               b=t2.day,
                               c=t2.year,
                               d=t1.month,
                               e=t1.day,
                               f=t1.year,
                               g='d', ignore='.csv'))
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
	    row[-1] = row[-1] + " " +ssym
    if not q :
            print "\t".join(row)
    spamWriter.writerow(row)
if not q :
    print spamReader.line_num
f.close()
# we're done
