import sys


def check():
    msg = ""
    failed = False
    try:
        from zope.testbrowser.browser import Browser
    except ImportError:
        msg += "\tzope.testbrowser\n"
        failed = True
    if failed:
        print "You appear to be missing dependencies. You need to install the"
        print "following libraries:"
        print msg
        sys.exit(1)
