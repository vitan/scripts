# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

#!/usr/bin/env python
# Written by Weitao Zhou <zhouwtlord@gmail.com>

import hashlib
import urllib2
import optparse
import os
import Queue
import re
import socket
import sys
import threading
import time

__version__ = '0.1'

USAGE = "%prog [options] <urls_input_file> <target_dir> <thread_num> <thread_delay> <timeout>"
ARGS_MIN_LENGTH = 5
VERSION = "%prog v" + __version__

#RE_PATTERN = r'[\w]{1,}'
RE_PATTERN = r'[a-zA-Z0-9]{1,}'

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}


class CrawlCount(threading.Thread):
    
    def __init__(self, queue, target, delay):
        threading.Thread.__init__(self)
        self.queue = queue
        self.target = target
        self.delay = delay
    
    def run(self):
        queue_non_empty = True
        while queue_non_empty:
            try:
                url = self.queue.get(False)
                fetcher = Fetcher(url)
                if fetcher.fetch() == False:
                    # Fetch Failed
                    continue
                content = fetcher.content 
                
                wordcount = WordCount(content, RE_PATTERN)
                wordcount.count()   
                
                compose = ['%s=%s' % item for item in wordcount.word_count.items()]
                
                # TODO
                # 1. how to avoid duplicated filename caused by duplicated url
                # 2. Since linux can't accept '/' as filename, hash the url to solve it
                filename = hashlib.sha256(url).hexdigest()
                with open(os.path.join(self.target, filename), 'w') as outf:
                    outf.write('\n'.join(compose))
                
                time.sleep(self.delay)
            except Queue.Empty:
                queue_non_empty = False


class Fetcher(object):

    def __init__(self, url):
        self.url = url
        self.content = None

    def _addHeaders(self, request):
        for key, value in HEADERS.items():
            request.add_header(key, value)

    def open(self):
        url = self.url
        try:
            print 'Fetching url %s' % url
            request = urllib2.Request(url)
            handle = urllib2.build_opener()
        except IOError:
            return None
        return (request, handle)

    def fetch(self):
        request, handle = self.open()
        self._addHeaders(request)
        if handle:
            try:
                self.content = unicode(handle.open(request).read(), "utf-8", errors="replace")
                return True
            except urllib2.HTTPError, error:
                if error.code == 404:
                    print >> sys.stderr, "ERROR: %s -> %s" % (error, error.url)
                else:
                    print >> sys.stderr, "ERROR: %s" % error
                return False
            except urllib2.URLError, error:
                print >> sys.stderr, "ERROR: %s" % error
                return False
            except socket.timeout, error:
                print >> sys.stderr, "ERROR: %s" % error
                return False
        return False


class WordCount(object):
    
    def __init__(self, text, re_pattern):
        self.re_pattern = re_pattern
        self.text = text
        self.word_count = dict()
        
    def pre_process(self):
        # Pre process the inputted Text:
        # 1. remove punctuation; 2. lower case;
        # Note: Given interview deadline, here I didn't involve tokenize, stemming, stopwords and other NLP pre-process methods
        word_list = self._remove_punctuation()
        return self._lower_case(word_list)
    
    def _remove_punctuation(self):
        print 'Removing punctuation'
        word_list = re.findall(self.re_pattern, self.text)
        return word_list
    
    def _lower_case(self, word_list):
        print 'Lowering case'
        return [word.lower() for word in word_list]
    
    def count(self):
        print 'Word Counting'
        word_list = self.pre_process()
        for word in word_list:
            self.word_count[word] = self.word_count.get(word, 0) + 1

def parse_options(args_min_length):
    """parse_options() -> opts, args

    Parse any command-line options given returning both
    the parsed options and arguments.
    """

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)


    opts, args = parser.parse_args()

    if len(args) < args_min_length:
        parser.print_help()
        raise SystemExit, 1

    return opts, args

def main():
    opts, args = parse_options(ARGS_MIN_LENGTH)
    
    urls_inf = args[0]
    target_dir = args[1]
    thread_num = int(args[2])
    thread_delay = int(args[3])
    socket_timeout = int(args[4])
    
    #set global timeout of socket
    socket.setdefaulttimeout(socket_timeout)
    
    splite = ['=']*20
    splite[10] = 'START'
    start_time = time.time()
    print ''.join(splite)

    q = Queue.Queue()
    with open(urls_inf, 'r') as urls:
        for url in urls:
            q.put(url)

            
    threads = []
    # multiple thread
    for i in range(thread_num):
        t = CrawlCount(q, target_dir, thread_delay)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    end_time = time.time()
    due = end_time-start_time
    print 'Used time: %s' % due
    splite[10] = 'END'
    print ''.join(splite)


if __name__ == "__main__":
    main()

