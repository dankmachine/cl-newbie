import sys, os, re, os.path
import urllib.request, urllib.error, urllib.parse
import pickle

def checkURL(url):
    try:
        urllib.request.urlopen(url)
        return True
    except urllib.error.URLError:
        return False

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
    return not time_str1[0] == time_str2[0]

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
    """ Takes in a craigslist url and outputs the listings to a file """

    # First check that the url is valid
    url = argv[1]
    cl_url_template = re.compile(r'https\:\/\/\w*\.craigslist\.org\/search\/.*')

    if not (cl_url_template.fullmatch(url) and checkURL(url)):
        raise InvalidURLException('craigslist url is invalid')

    # Then scrape and store the listing urls
    # index order: listing url, year, month, day, hour, minute, second
    page_text = str(urllib.request.urlopen(url).read())
    url_ymdhms_pattern = re.compile(r'result\-row.+?\s*\<a\shref\=\"(\S+)\"[\S\s]*?datetime\=\"(\w+)\-(\w+)-(\w+)\s(\w+)\:(\w+)"[\S\s]*?\:\w\w\:(\w\w)')
    all_listinfo = re.findall(url_ymdhms_pattern, page_text)

    # Compare fetched info with previous info to filter for new listings
    if os.path.isfile('lastseen.p'):
        lastseen = pickle.load(open("lastseen.p", "rb"))
        new_listinfo = newer_listings(all_listinfo, lastseen) 
    else:
        new_listinfo = all_listinfo

    # Store the new lastseen
    if new_listinfo:
        pickle.dump(new_listinfo[0], open("lastseen.p", "wb"))

    # pickle current info and 
    # output new ones to a human-readable file
    newlistings_file = open("newlistings.txt", "w+")
    for newlisting in new_listinfo:
        newlistings_file.write('https://craigslist.org/' + newlisting[0] + '\n')
    newlistings_file.close()

if __name__ == "__main__":
    main(sys.argv)
