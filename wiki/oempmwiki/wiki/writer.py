import sys

import mechanize

from oempmwiki import const
from oempmwiki.clients import browser


class WikiWriter(object):
    """
    A class that provides a means of writing wiki data to a wiki page.
    """
    def __init__(self, wiki_url, username, password):
        self.wiki_url = wiki_url
        self.username = username
        self.password = password
        mech_browser = mechanize.Browser()
        mech_browser.addheaders = [("User-agent", const.AGENT_STRING)]
        mech_browser.set_handle_robots(False)
        self.browser = browser.Browser(wiki_url, mech_browser=mech_browser)
        self.login()

    def login(self):
        print "Logging into the wiki..."
        self.browser.getLink("Login").click()
        print "\tConfirming openid..."
        self.browser.getForm("openid_message").submit()
        print "\tSending launchpad credentials..."
        form = self.browser.getForm()
        form.getControl(name="email").value = self.username
        form.getControl(name="password").value = self.password
        form.submit(name="continue")
        print "Logged into wiki."

    def checksum(self, data):
        # XXX check to see if we need to write!
        # XXX hrm... but since we need to go through the trouble of logging in
        # first, just to see if anything's changed, it might make more sense to
        # track the data obtained from the source... see if it has changed
        # since the last "get"...
        pass

    def write(self, data):
        self.browser.open(self.wiki_url)
        if not data:
            print "Nothing to write; skipping."
            sys.exit(0)
        is_trivial = True
        try:
            self.browser.getLink("Edit").click()
            print "Editing wiki page..."
        except mechanize.HTTPError:
            self.browser.getLink("Create new empty page").click()
            is_trivial = False
            print "Creating new wiki page..."
        form = self.browser.getForm("editor")
        form.getControl(name="trivial").value = [is_trivial]
        form.getControl(name="savetext").value = data.encode("utf-8")
        form.submit(name="button_save")
        print "Page changes saved."
