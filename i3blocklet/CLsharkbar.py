#!/usr/bin/env python3
import sys, os, re, os.path
import urllib.request, socket
import pickle
import webbrowser
import time

class InvalidURLException(Exception):
    pass

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

def main(argv):
    """
    Takes in a craigslist url and outputs the listings to a file

    Raises:
        InvalidURLException -- if the passed-in url isn't a validly formatted craisglist url
        urllib.request.URLError -- if we can't get the webpage data after retrying 
        urllib.request.HTTPError -- if there's some unforseen problem (lol) with the request
        socket.timeout -- if we time out before retrieving the request
    """

    # First check that the url is valid
    # make sure to use a 'sort by newest' query
    # url = 'https://AREA.craigslist.com/search/...sort=date...'
    url = argv[1]
    cl_url_template = re.compile(r'https\:\/\/\w*\.craigslist\.org\/search\/.*sort=date.*')

    if not (cl_url_template.fullmatch(url)):
        raise InvalidURLException('craigslist url is invalid')

    # Open url on middle click
    if os.environ.get('BLOCK_BUTTON') == '2':
        webbrowser.open(url)

    # Then scrape and store the listing urls
    # index order: listing url, year, month, day, hour, minute, second
    retries = 3 # retry at most 3 times
    for _ in range(retries):
        try:
            url_response = urllib.request.urlopen(url, timeout=15)
            break
        except (socket.timeout, urllib.request.URLError, urllib.request.HTTPError):
            time.sleep(3)
    else:
        raise

    page_text = str(url_response.read())
    url_ymdhms_pattern = re.compile(r'result\-row.+?\s*\<a\shref\=\"(\S+)\"[\S\s]*?datetime\=\"(\w+)\-(\w+)-(\w+)\s(\w+)\:(\w+)"[\S\s]*?\:\w\w\:(\w\w)')
    all_listinfo = re.findall(url_ymdhms_pattern, page_text)

    fileprefix = ''
    block_instance = os.environ.get('BLOCK_INSTANCE')
    if block_instance:
        bi_path = os.path.expanduser(block_instance)
        fileprefix = bi_path + '/'

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

if __name__ == "__main__":
    main(sys.argv)
