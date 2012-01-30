#!/usr/bin/python
# Copyright (c) 2009 Denis Bilenko. See gevent LICENSE for details.
# Copyright (c) 2012 New Dream Network (DreamHost)
# Downloaded from:
#   https://bitbucket.org/denis/gevent/src/tip/examples/concurrent_download.py
"""
Spawn multiple "jobs" and wait for them to complete.
"""
import gevent
from gevent import monkey

monkey.patch_all()

import urllib2


urls = [
    "http://www.google.com",
    "http://www.yahoo.com",
    "http://www.python.org",
    "http://www.dreamhost.com",
    "http://www.github.com",
    "http://www.openstack.com",
    "http://www.badhost.comm",
    "http://www.ubuntu.com",
    "http://www.launchpad.com",
    "http://www.bitbucket.com",
    "http://www.twisted.com",
    "http://127.0.0.1",
    ]


def get_page(url, offset=50):
    data = urllib2.urlopen(url).read()
    bytes = len(data)
    content = data[:offset]
    print ("%s\n\tbytes: %s\n\tcontent: %r" % (url, bytes, content))


def greenlet_runner(url):
    try:
        print ("\tGreenlet getting page (%s)" % (url,))
        get_page(url)
    except Exception, err:
        print ("%s\n\tCouldn't get page!\n\t%s: %s" % (
            url, err.__class__.__name__, err.args[0]))


def create_greenlets():
    jobs = []
    for url in urls:
        print ("\tScheduling greenlet for %s" % (url,))
        jobs.append(gevent.spawn(greenlet_runner, url))
    return jobs


print ("Creating greenlets ...")
jobs = create_greenlets()
print ("Greenlets created.")
print ("Running greenlets ...")
gevent.joinall(jobs)
print ("\nGreenlets completed.")
