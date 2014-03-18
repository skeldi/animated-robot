#!/usr/bin/env python

import urllib, urllib2
from datetime import datetime
from dateutil.relativedelta import relativedelta
from BeautifulSoup import BeautifulSoup


#useragent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome_Scrape/33.0.1750.154'
accountwww = 'https://account.tfl.gov.uk'
oysterwww = 'https://oyster.tfl.gov.uk'
cardID = ''   # oystercard number
username = '' # oystercard website user name - URLencoded
password = '' # oystercard website password
bodyData = "ReturnUrl=https%3A%2F%2Foyster.tfl.gov.uk%2Foyster%2Fsecurity_check&AppId=8ead5cf4-4624-4389-b90c-b1fd1937bf1f&UserName="+username+"&Password="+password+"&Sign+in=Sign+in"

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
urllib2.install_opener(opener)
# log in
#bodyData = urllib.urlencode({'UserName': username, 'Password': password})
#headers = {'User-Agent': useragent}
request = urllib2.Request(accountwww + '/Oyster/', bodyData) #, headers
response = urllib2.urlopen(request)
welcomepage = BeautifulSoup(response)


JourneyHistoryTag = welcomepage.find(lambda tag: tag.string == 'Journey history')
if JourneyHistoryTag is None:
    # get card form
    cardform = welcomepage.find('form', id='selectCardForm')
    #print cardform['action']
    cardurl = oysterwww + cardform['action']
    q = urllib.urlencode({'cardId': cardID, 'method': 'input'})
    # form (sometimes?) has stupid text input hidden by css
    cardhidden = cardform.find('input', type='hidden')
    if cardhidden:
        q += urllib.urlencode({cardhidden['name']: cardhidden['value']})
    creq = urllib2.Request(cardurl, q) #,headers
    g = urllib2.urlopen(creq)
    cardpage = BeautifulSoup(g)
    #print cardpage
    JourneyHistoryTag = cardpage.find(lambda tag: tag.string == 'Journey history')
    if JourneyHistoryTag is None:
        raise Exception, 'Failed to find journey history'
# now ready to get journey history
todate = datetime.now()
fromdate = todate - relativedelta(weeks=8)
jhdict = {'dateRange': 'custom date range',
        'customDateRangeSel': 'false', 'isJSEnabledForPagenation': 'false',
        'offset': '0', 'rows': '0',
        'csDateTo': todate.strftime("%d/%m/%Y"),
        'csDateFrom': fromdate.strftime("%d/%m/%Y")}
jhurl = oysterwww + JourneyHistoryTag['href']
jhreq = urllib2.Request(jhurl, urllib.urlencode(jhdict))
jhresponse = urllib2.urlopen(jhreq)
#jhpage = jh.read()
#response = urllib2.urlopen(jhreq)
jhpage = BeautifulSoup(jhresponse)
#print jhpage

#Download CSV format
csvform = jhpage.find('form', id='jhDownloadForm')
csvformA = csvform.a['onclick']
#this is the URL we now want to download and save as CSV file
print csvformA.split('"')[1]

# Retrieve the webpage as a string
CSVurl = oysterwww + csvformA.split('"')[1]
CSVreq = urllib2.Request(CSVurl)
CSVresponse = urllib2.urlopen(CSVreq)
#print CSVresponse.read()

# Save the string to a file
csvstr = CSVresponse.read()

lines = csvstr.split("\\n")
file = open("journey.csv", "w")
for line in lines:
   file.write(line + "\n")
file.close()
