import csv, urllib2


data_host = "spreadsheets1.google.com"
data_path = "/a/canonical.com/spreadsheet/pub"
data_key = "0ArIWq6t1tnKldGtGRkxGRzVuczBJcW83b3VlRlYyUGc"
data_query = "hl=en_US&hl=en_US&key=%s&single=true&gid=0&output=csv" % data_key
data_url = "https://%s%s?%s" % (data_host, data_path, data_query)


data = urllib2.urlopen(data_url).read()
print data


class WikiRawLine(object):
    """ 
    An object that simply holds a raw wiki line for later use.
    """
    split_on = "||"

    def __init__(self, line):
        self.line = line

    def __repr__(self):
        self.render()

    def render(self):
        return self.line


class WikiRow(WikiRawLine):
    """ 
    A convenience object for creating general moin moin table rows.
    """
    def __init__(self, *cells):
        self.cells = [unicode(x) for x in cells]

    @staticmethod
    def join(list_of_items):
        return "%s%s%s" % ( 
            self.split_on,
            self.split_on.join(list_of_items),
            self.split_on)

    def render(self):
        return self.join(self.cells)


class ProjectStatusRow(WikiRow):
    """
    A Row subclass that has project-specific customizations.
    """
    # XXX add rules for checking/normalizing content
    # XXX add rules for coloring cells based on content


class WikiTable(object):
    """
    A convenience object for creating general moin moin tables.
    """
    def __init__(self, dictionary, headers=None, subheaders=None, 
                 row_class=None, writer=None):
        self.row_data = dictionary
        self.headers = headers
        self.subheaders = subheaders
        self.compiled_data = None
        self.rows = []
        self.writer = writer
        if not row_class:
            row_class = ProjectStatusRow
        self.row_class = row_class

    def __repr__(self):
        return "\n".join([repr(x) for x in self.rows])

    def build_table(self):
        if self.headers:
            self.rows.append(self.row_class(self.headers))
        if self.subheaders:
            self.rows.append(self.row_class(self.subheaders))
        for row_data in self.row_data:
            data = [x for x in row_data.values()]
            self.rows.append(self.row_class(data))

    def write(self, writer=None):
        if writer:
            self.writer = writer
        self.writer.write(str(self))

                
class WikiWriter(object):
    """
    A class that provides a means of writing wiki data to a wiki page.
    """

def login(browser, username, password):
    print "Logging into the wiki..."
    browser.getLink("Log In / Register").click()
    # First stage
    print "\tSending credentials to wiki..."
    form = browser.getForm("loginform")
    form.getControl(name="name").value = username
    form.getControl(name="password").value = password
    form.submit()
    # Second stage
    print "\tConfirming openid..."
    browser.getForm("openid_message").submit()
    # Third stage
    print "\tSending launchpad credentials..."
    form = browser.getForm()
    form.getControl(name="email").value = username
    form.getControl(name="password").value = password
    form.submit(name="continue")
    # Fourth state (confirm SSO)
    browser.getForm().getControl(name="yes").click()


def replace_page_data(browser, options, dropped, postponed, status_data):
    browser.getLink("Edit").click()
    form = browser.getForm("editor")
    if options.trivial:
        form.getControl(name="trivial").value = [True]
    data = make_summary(dropped, postponed)
    data += get_new_wiki_data(browser, status_data).encode("utf-8")
    form.getControl(name="savetext").value = data
    form.submit(name="button_save")


def main(options):
    # get the data first, that's the quickest op
    dropped, postponed, status_data = get_page_data(options)
    # then mess with openid and the wiki
    mech_browser = mechanize.Browser()
    mech_browser.addheaders = [("User-agent", AGENT_STRING)]
    mech_browser.set_handle_robots(None)
    browser = Browser(options.url, mech_browser=mech_browser)
    login(browser, options.username, options.password)
    replace_page_data(browser, options, dropped, postponed, status_data)
    print "Operation complete."


if __name__ == "__main__":
    from copy import copy
    from datetime import datetime
    from optparse import Option, OptionParser, OptionValueError

    def check_unicode(option, opt, value):
        try:
            return unicode(value)
        except ValueError, error:
            raise OptionValueError(error)

    class CustomOption(Option):
        TYPES = Option.TYPES + ("unicode",)
        TYPE_CHECKER = copy(Option.TYPE_CHECKER)
        TYPE_CHECKER["unicode"] = check_unicode

    # XXX Make the defualt date, e.g., "SELECT MAX(date) FROM work_items"
    date = datetime.now().strftime("%Y-%m-%d")
    parser = OptionParser(usage=__doc__, option_class=CustomOption)
    parser.add_option(
        "-u", "--user", dest="username",
        help="Launchpad username (email address)")
    parser.add_option(
        "-p", "--password", dest="password",
        help="password for Launchpad account")
    parser.add_option(
        "-d", "--database", dest="database",
        help="full path to the SQLite database")
    parser.add_option(
        "--url", dest="url", help="wiki page to update")
    parser.add_option(
        "-m", "--milestone", dest="milestone", type="unicode",
        help="limit the reults to the given milestone")
    parser.add_option(
        "--date", dest="date", default=date, type="unicode",
        help="query historical data for the given date")
    parser.add_option(
        "-t", "--trivial", dest="trivial", default=False, action="store_true",
        help="save the wiki page as a trivial change")
    (options, args) = parser.parse_args()
    if not options.username:
        parser.error("username is required")
    if not options.password:
        parser.error("password is required")
    if not options.database:
        parser.error("the path to the database is required")
    if not options.url:
        parser.error("a wiki URL is required")
    main(options)   
