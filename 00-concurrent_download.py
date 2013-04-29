#!/usr/bin/python
# Copyright (c) 2009 Denis Bilenko. See LICENSE for details.
# Downloaded from:
#   https://bitbucket.org/denis/gevent/src/tip/examples/concurrent_download.py
"""
Spawn multiple workers and wait for them to complete.
"""
import gevent
from gevent import monkey

monkey.patch_all()

import urllib2


urls = [
    'http://www.google.com',
    'http://www.yandex.ru',
    'http://www.python.org',
    ]


def print_head(url):
    print ('Starting %s' % url)
    data = urllib2.urlopen(url).read()
    print ('%s: %s bytes: %r' % (url, len(data), data[:50]))


jobs = [gevent.spawn(print_head, url) for url in urls]
gevent.joinall(jobs)
