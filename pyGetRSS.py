#!/usr/bin/python

import feedparser
import sys
import getopt
import os
from urllib2 import urlopen, URLError, HTTPError
import shlex
import subprocess
import datetime

def header():
    print ""
    print "==========================================================================="
    print "= Python script to download RSS podcast feeds                             ="
    print "==========================================================================="
    print ""

def debug():
    print "Number of arguments: ", len(sys.argv), 'arguments.'
    print "Argument List:", str(sys.argv)

def logW(dest,target_file):
    now = datetime.datetime.now()
    logdatetime = str(now.strftime("%Y-%m-%d"))
    logfile = "%spodlog.txt" % dest 
    log = open(logfile, 'a')
    nabbed = logdatetime + " -- Downloaded: " + target_file
    log.write(nabbed)
    log.write("\n")
    log.close



def parse(rss_url):
    print "Parsing %s \n" % rss_url
    feed = feedparser.parse(rss_url)
    return feed

def find_mp3(feed,debug_code):
    url_list = []
    for index,item in enumerate(feed.entries):
        
        if debug_code == True:
            print index 
            print item
            print item.links
            print "Podcast Title: %s " % item.title
            print "Podcast Description:\n" + item.description

        # New method -- works much better
        for lines in item.links:
            if lines['type'] == u'audio/mpeg' or lines['type'] == u'audio/x-mpeg':
                url = str(lines['href'].split('?')[0])
                url_list.append([url])

        """ # old method -- broke with some/most RSS feeds
        for key, val in item.links[1].iteritems():
            if key == "href":
                a = str(val.split('?')[0])#.encode("utf-8")
                url_list.append([a])
        """

    return url_list

def dl_file(url,dest):
    print "\nUsing dl_file()"
    try:
        f = urlopen(url)
        print "Filename on disk will be --> " + os.path.basename(url)
        print "Downloading Podcast via url: " + url
        directory = dest
        target_file = directory + os.path.basename(url)
        if os.path.isfile(target_file):
            print "File %s already exists; not downloading" % target_file
        else:
            logW(dest,target_file)
            print "Writing to: %s" % target_file
            with open(target_file, "wb") as local_file:
                local_file.write(f.read())

    except HTTPError, e:
        print "HTTP Error: ", e.code, url
    except URLError, e:
        print "URL Error: ", e.reason, url

def dl_fileWget(url,dest):
    print "Using dlfileWget()"
    directory = dest
    target_file = directory + os.path.basename(url)
    if os.path.isfile(target_file):
        print "File %s already exists; not downloading" % target_file
    else:
        logW(dest,target_file)
        print "Downloading file via wget subprocess..."
        command = "wget " + url + " -q --progress=bar --no-clobber -O " + target_file
        print command
        args = shlex.split(command)
        subprocess.Popen(args)

def dl_dummy(url,dest,debug_code):
    print "Pretending to download ==> %s" % url
    print "  to location ==> %s" % dest

def split_and_dl(url_list,dest,limit,download_method,debug_code):
    downloader = download_method
    url_list = url_list[0:limit]
    for urls in url_list:
        if downloader == 'debug' or debug_code == True:
            dl_dummy(urls[0],dest,debug_code)        
        elif downloader == 'wget':
            dl_fileWget(urls[0],dest)
        else: 
            dl_file(urls[0],dest)        
       

def main(argv):
    
    dest = ''
    rss_url = ''
    limit = 5
    download_method = ''
    debug_code = False

    try:
        opts, args = getopt.getopt(argv,"hu:d:l:m:",["rssfeed=","destination=","limit=","method=","debug"])
    except getopt.GetoptError:
        print str(sys.argv)
        print "%s -u <rss_feed_url> -d <destination_directory> -l <5> -m <download_method> [default=py,py,wget,debug]" % sys.argv[0]
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print "%s -u <rss_feed_url> -d <destination_directory> -l <5> -m <download_method> [default=py,py,wget,debug]" % sys.argv[0]
            sys.exit()
        elif opt in ("-u", "--rssfeed"):
            rss_url = arg
        elif opt in ("-d", "--destination"):
            dest = arg
        elif opt in ("-l", "--limit"):
            limit = int(arg)
        elif opt in ("-m", "--method"):
            download_method = arg
        elif opt in ("--debug"):
            print "Debugging is ON"
            debug()
            debug_code = True

    if debug_code == True:
        print dest, rss_url, limit, download_method, debug_code
    
    #rss_url = "http://cupodcast.podbean.com/feed"
    #rss_url = "http://theadamcarollashow.libsyn.com/rss"
    #rss_url = "https://feeds.feedburner.com/TheAdamAndDrewShow?format=xml"
    
    header()
    feed = parse(rss_url)
    url_list = find_mp3(feed,debug_code)
    split_and_dl(url_list,dest,limit,download_method,debug_code)
    print "Complete."

if __name__ == '__main__':
    main(sys.argv[1:])

