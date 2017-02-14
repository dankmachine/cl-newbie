#!/usr/bin/env python3
import sys, os, re, os.path
import urllib.request, urllib.error, urllib.parse
import pickle
import webbrowser

def checkURL(url):
    try:
        urllib.request.urlopen(url)
        return True
    except urllib.error.URLError:
        return False

def compare_time(listinfo1, listinfo2):
    """
    Take in two ordered lists of:
    listing url, year, month, day, hour, minute, second

    and return True if the first listing was posted after the second

    If the times are equal, return True if the urls are different
    """
    for time_str1, time_str2 in zip(listinfo1[1:], listinfo2[1:]):
        time_int1, time_int2 = int(time_str1), int(time_str2) 
        if time_int1 < time_int2:
            return False
        if time_int1 > time_int2:
            return True
    return time_str1[0] != time_str2[0]

def newer_listings(listinfo, lastseen):
    """
    Return a list of all listings from listinfo
    that are still newer than lastseen where listinfo
    is sorted from newest to oldest
    """
    index = 0
    for listing in listinfo:
        if compare_time(listing, lastseen):
            index += 1
        else:
            return listinfo[:index]
    return listinfo[:index] # in case all the current listings are wiped out lol

# set url cause we only want this to do one thing
# make sure to use a 'sort by newest' query
# url = 'https://AREA.craigslist.com/search/QUERY'

# Open url on middle click
if os.environ.get('BLOCK_BUTTON') == '2':
    webbrowser.open(url)

# Then scrape and store the listing urls
# index order: listing url, year, month, day, hour, minute, second
page_text = str(urllib.request.urlopen(url).read())
url_ymdhms_pattern = re.compile(r'result\-row.+?\s*\<a\shref\=\"(\S+)\"[\S\s]*?datetime\=\"(\w+)\-(\w+)-(\w+)\s(\w+)\:(\w+)"[\S\s]*?\:\w\w\:(\w\w)')
all_listinfo = re.findall(url_ymdhms_pattern, page_text)

block_instance = os.path.expanduser(os.environ.get('BLOCK_INSTANCE'))
fileprefix = block_instance + '/' if block_instance else ''

# Compare fetched info with previous info to filter for new listings
if os.path.isfile(fileprefix + 'lastseen.p'):
    with open(fileprefix + 'lastseen.p', 'rb') as lastseen_pickle:
        lastseen = pickle.load(lastseen_pickle)
    new_listinfo = newer_listings(all_listinfo, lastseen) 
else:
    new_listinfo = all_listinfo

# Store the new lastseen
if new_listinfo:
    with open(fileprefix + 'lastseen.p', 'wb') as lastseen_pickle:
        pickle.dump(new_listinfo[0], lastseen_pickle)

# Remove numlistings.p on right click
if os.environ.get('BLOCK_BUTTON') == '3':
    os.remove(fileprefix + 'numlistings.p')

# Store the new number of new listings
if os.path.isfile(fileprefix + 'numlistings.p'):
    with open(fileprefix + 'numlistings.p', 'rb') as numlistings_pickle:
        numlistings = pickle.load(numlistings_pickle) + len(new_listinfo)
else:
    numlistings = len(new_listinfo)

with open(fileprefix + 'numlistings.p', 'wb') as numlistings_pickle:
    pickle.dump(numlistings, numlistings_pickle)

# print the bar info:
#   full text
#   short text
#   color
print(numlistings)
print(numlistings)
if numlistings:
    print('#00FF00')
else:
    print('#FFFFFF')
