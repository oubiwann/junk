
#!/usr/bin/python
# Copyright (c) 2012 New Dream Network, LLC (DreamHost)
"""
Use the Greenlet class to run multiple "jobs" and wait for them to complete.
"""
import gevent
from gevent import monkey

monkey.patch_all()

import timeit
import urllib2




def get_page(url, content_offset=100):
    try:
        data = urllib2.urlopen(url).read()
    except Exception, err:
        data = err
    return data


def check_content(greenlet_exit):
    data = greenlet_exit.value
    bytes = 0
    if isinstance(data, basestring):
        bytes = len(data)

def create_greenlets(urls):
    jobs = []
    for url in urls:
        g = gevent.Greenlet(get_page, url, content_offset=20)
        g.link_value(check_content)
        g.start()
        jobs.append(g)
    return jobs


def complex(url_count=1):
    urls = ["http://127.0.0.1"] * url_count
    jobs = create_greenlets(urls)
    gevent.joinall(jobs)


def simple(url_count=1):
    urls = ["http://127.0.0.1"] * url_count
    jobs = [gevent.spawn(get_page, url) for url in urls]
    gevent.joinall(jobs)


def run_it(runs, requests):
    for command in ['complex', 'simple']:
        import_string = 'from __main__ import %s' % command
        command_string = '%s(url_count=%s)' % (command, requests)
        for run in runs:
            time = timeit.timeit(command_string, import_string, number=run)
            print "%s, %s, %s, %s" % (command, run, requests, time)

def run_it_2(runs, requests):
    for command in ['complex', 'simple']:
        import_string = 'from __main__ import %s' % command
        for run, request_count in zip(runs, requests):
            command_string = '%s(url_count=%s)' % (command, request_count)
            time = timeit.timeit(command_string, import_string, number=run)
            print "%s, %s, %s, %s" % (command, run, request_count, time)


# progression 1
runs = [1,2,3,4,5,6,7,8,9,10,20,30,40,50,100,200,500,1000,5000,10000]
requests = 1
#run_it(runs, requests)
# progression 2
runs = [1,2,3,4,5,6,7,8,9,10,20,30,40,50,100,200,500,1000]
requests = 10
#run_it(runs, requests)
# progression 3
runs = [1,2,3,4,5,6,7,8,9,10,20,30,40,50,100]
requests = 100
#run_it(runs, requests)
# progression 4
runs = [1,2,3,4,5,6,7,8,9,10]
requests = 1000
#run_it(runs, requests)
# progression 5
runs = [1,2,3]
requests = 10000
#run_it(runs, requests)
# progression 6
runs = [1,2,3]
requests = 100000
#run_it(runs, requests)
# progression 7
runs = [100000,75000,50000,25000,10000,7500,5000,2500,1000,750,500,250,100,75,
        50,25,10,8,5,3,1]
requests = [1,3,5,8,10,25,50,75,100,250,500,750,1000,2500,5000,7500,10000,
            25000,50000,75000,100000]
run_it_2(runs, requests)
