#!/usr/bin/env python

import os
import sys

from glob import glob
from optparse import OptionParser


class Event(object):

    def __init__(self, path):
        self.path = path

    @property
    def capabilities(self):
        path = os.path.join(self.path, "device", "capabilities", "abs")
        line = read_line(path)
        return int(line, 16)

    @property
    def device(self):
        base = os.path.basename(self.path)
        return os.path.join("/dev", "input", base)

    @property
    def name(self):
        path = os.path.join(self.path, "device", "name")
        return read_line(path)


def get_events(input):
    event_glob = os.path.join(input, "event*")
    for event_path in glob(event_glob):
        yield Event(event_path)

def read_line(path):
    f = open(path)
    try:
        return f.readline().strip()
    finally:
        f.close()

def main(args):
    usage = "Usage: %prog [OPTIONS]"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--input",
        metavar="FILE",
        default="/sys/class/input",
        help="Input sysfs directory")
    (options, args) = parser.parse_args(args)

    detected = False
    for event in get_events(options.input):
        if event.capabilities & 0x35:
            if not detected:
                detected = True
                print "Found device(s):"
            print "%s: %s" % (event.name, event.device)

    if not detected:
        print "No MT-capable device found..."
        return 1

    else:
        return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

