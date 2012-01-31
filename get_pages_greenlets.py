#!/usr/bin/python
# Copyright (c) 2012 New Dream Network (DreamHost)
"""
Use the Greenlet class to run multiple "jobs" and wait for them to complete.
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


def get_page(url, content_offset=100):
    try:
        return (url, urllib2.urlopen(url).read(), content_offset)
    except Exception, err:
        return (url, err, None)


def print_success(data, offset):
    print("    bytes: %s" % len(data))
    print("    content: %s" % data[:offset].replace("\n", "").strip())


def print_error(err):
    print("    Error!")
    print("    %s: %s!" % (err.__class__.__name__, err.args[0]))


def check_content(greenlet_exit):
    url, result, offset = greenlet_exit.value
    print("  Checking results for %s ..." % url)
    if isinstance(result, Exception):
        print_error(result)
    else:
        print_success(result, offset)


def create_greenlets():
    jobs = []
    for url in urls:
        print("  Creating and scheduling greenlet for %s ..." % url)
        g = gevent.Greenlet(get_page, url, content_offset=20)
        g.link_value(check_content)
        # now schedule it to run
        g.start()
        print("  Done.")
        jobs.append(g)
    return jobs


print("Creating greenlets ...")
jobs = create_greenlets()
print("Greenlets created.")
print("Getting results ...")
gevent.joinall(jobs)
print("\nGreenlets completed.")
