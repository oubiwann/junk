import mechanize

from zope.testbrowser.browser import Browser

from oempmwiki import const


class WikiWriter(object):
    """
    A class that provides a means of writing wiki data to a wiki page.
    """
    def __init__(self, wiki_url, username, password):
        # then mess with openid and the wiki
        self.username = username
        self.password = password
        mech_browser = mechanize.Browser()
        mech_browser.addheaders = [("User-agent", const.AGENT_STRING)]
        mech_browser.set_handle_robots(None)
        self.browser = Browser(wiki_url, mech_browser=mech_browser)
        self.login()

    def login(self):
        print "Logging into the wiki..."
        self.browser.getLink("Login").click()
        # First stage
        print "\tSending credentials to wiki..."
        form = self.browser.getForm("loginform")
        form.getControl(name="name").value = self.username
        form.getControl(name="password").value = self.password
        form.submit()
        # Second stage
        print "\tConfirming openid..."
        self.browser.getForm("openid_message").submit()
        # Third stage
        print "\tSending launchpad credentials..."
        form = self.browser.getForm()
        form.getControl(name="email").value = self.username
        form.getControl(name="password").value = self.password
        form.submit(name="continue")
        print "Logged into wiki."

    def write(self, data):
        print "Editing wiki page..."
        self.browser.getLink("Edit").click()
        form = self.browser.getForm("editor")
        form.getControl(name="trivial").value = [True]
        form.getControl(name="savetext").value = data.encode("utf-8")
        form.submit(name="button_save")
        print "Page changes saved."
