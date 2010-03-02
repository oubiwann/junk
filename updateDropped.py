#!/usr/bin/env python
"""

To use this script, you need to pass your Launchpad username (email address)
and password, as well as the full path to the SQLite database you are working
with and the URL for the wiki page you wish to update:

    %prog [options]

An example usage:

    %prog -u you@canonical.com -p secret \\
        -d /home/you/Downloads/lucid.db \\
        --url https://wiki.ubuntu.com/YourTestPage \\
        --trivial --date 2010-03-01 --milestone lucid-alpha-3

Note that this script requires both storm and zope.testbrowser to be installed.
"""
import re

from zope.testbrowser.browser import Browser
from storm.locals import (
    DateTime, Reference, ReferenceSet, Store, Storm, Unicode, create_database)


DONE = u"done"
INPROGRESS = u"inprogress"
TODO = u"todo"
POSTPONED = u"postponed"
DROPPED = u"dropped"


class Milestone(object):
    """
    A convenience object that encapsulates milestone comparison logic.
    """
    # IMPORTANT!!! This needs to be maintained with every new milestone that
    # makes it into the SQLite database!
    legal_values = [
        "jaunty-updates",
        "lucid-alpha-1",
        "lucid-alpha-2",
        "lucid-alpha-3",
        "ubuntu-10.04-beta-1",
        "ubuntu-10.04-beta-2",
        "ubuntu-10.04",
        "later",
        ]

    def __init__(self, name):
        self.name = name.lower()
        self.value = self.legal_values.index(self.name)

    def __cmp__(self, other):
        if self.value > other.value:
            return 1
        elif self.value < other.value:
            return -1
        else:
            return 0

    def __sub__(self, other):
        return self.legal_values[abs(self.value - other)]    

    def __add__(self, other):
        return self.legal_values[self.value + other]    


class WorkItem(Storm):
    """
    The data model for the work items in the SQLite database.
    """
    __storm_table__ = "work_items"
    __storm_primary__ = "spec", "description", "milestone", "date"
    description = Unicode()
    spec = Unicode()
    status = Unicode()
    assignee = Unicode()
    milestone = Unicode()
    date = Unicode()
    blueprint = Reference(spec, "Blueprint.name")


class Blueprint(Storm):
    """
    The data model for the specs in the SQLite database.
    """
    __storm_table__ = "specs"
    name = Unicode(primary=True)
    url = Unicode()
    priority = Unicode()
    implementation = Unicode()
    assignee = Unicode()
    team = Unicode()
    status = Unicode()
    milestone = Unicode()
    definition = Unicode()
    drafter = Unicode()
    approver = Unicode()
    details_url = Unicode()

    @property
    def numeric_priority(self):
        if self.priority == "Essential":
            return 1
        elif self.priority == "High":
            return 2
        elif self.priority == "Medium":
            return 3
        elif self.priority == "Low":
            return 4


Blueprint.work_items = ReferenceSet(Blueprint.name, WorkItem.spec)


class WikiRawLine(object):
    """
    An object that simply holds a raw wiki line for later use.
    """
    split_on = "||"

    def __init__(self, line):
        self.line = line

    def render(self):
        return self.line


class WikiWorkItem(WikiRawLine):
    """
    A convenience object for storing and accessing work item data from the wiki
    page.
    """
    marker = "UbuntuSpec:"

    def __init__(self, spec=None, priority=None, description=None, status=None):
        self.spec = spec
        self.priority = priority
        self.description = description
        self.status = status
        self.header_line = None
        self.line = None
        self.headers = None

    def parse(self, header_line, data_line):
        self.headers = self.extract_headers(self.header_line)
        self.set_attributes(data_line)

    @staticmethod
    def split_fields(line):
        # Skip first and last element, since those are non-entires, artifacts
        # of the split.
        return [x.strip()
                for x in header_line.split(WikiWorkItem.split_on)[1:-1]]

    @staticmethod
    def extract_headers(header_line):
        """
        This code is written to be dynamic, but other code will expect the
        headers to be the following:

            'Spec', 'Priority', 'Work Item Description', 'Status'

        If those ever change, other code may need to be updated.
        """
        splits = WikiWorkItem.split_fields(header_line)

        def clean(header_name):
            return header_name.replace("'", "").strip()

        def sanitize(header_name):
            return clean(header_name).lower().replace(" ", "_")

        return [(x, clean(y), sanitize(y)) for x, y in enumerate(splits)]

    def set_attributes(self, data_line):
        if not data_line.startswith("%s%s" % (split_on, marker)):
            raise ValueError("Invalid data line %s was passed." % data_line)
        splits = self.split_fields(data_line)
        for header, data in zip(self.headers, splits):
            index, header_name, attr = header
            setattr(self, attr, unicode(data))

    @staticmethod
    def join(list_of_items):
        return "%s%s%s" % (
            WikiWorkItem.split_on,
            WikiWorkItem.split_on.join(list_of_items),
            WikiWorkItem.split_on)

    def render(self):
        data = [self.spec, self.priority, self.description, self.status]
        return self.join(data)


class WikiBlueprint(object):
    """
    A convenience object for storing and accessing blueprint data from the wiki
    page.
    """
    def __init__(self, id):
        self.id = id
        self.work_items = []

    def add_work_item(self, work_item_wiki_object):
        self.work_items.append(work_item_wiki_object)


class WikiData(object):
    """
    A convenience object for storing and accessing all the wiki form data as
    objects.
    """
    split_on = "\r\n"

    def __init__(self, initial_row=None, form_data=None):
        self.raw_data = None
        self.lines = None
        self.header_line = None
        self.line_objects = []
        self.blueprints = {}
        self.has_blueprints = False
        if initial_row:
            self.add_line(initial_row)
        if form_data:
            self.parse(form_data)

    def parse(self, form_data):
        self.raw_data = form_data
        self.lines = form_data.split(self.split_on)
        self.header_line = self.lines[0]
        for line in lines:
            if line.startswith(
                "%s%s" % (WikiWorkItem.split_on, WikiWorkItem.marker)):
                line_object = WikiWorkItem(header_line, line)
                self.add_work_item(line_object)
            else:
                line_object = WikiRawLine(line)
            self.line_objects.append(line_object)

    def get_blueprint(self, id):
        blueprint = self.blueprints.get(id)
        if not blueprint:
            blueprint = WikiBlueprint(id)
            self.blueprints[id] = blueprint
        return blueprint

    def get_blueprints(self):
        return self.blueprints.values()

    def add_work_item(self, work_item):
        self.line_objects.append(work_item)
        blueprint = self.get_blueprint(work_item.spec)
        blueprint.add_work_item(work_item)
        if not self.has_blueprint:
            self.has_blueprints = True

    def add_separator(self, color="999999"):
        separator = WikiWorkItem.join(["<#%s>" % color] * 4)
        self.add_line(separator)

    def add_line(self, string_or_object):
        if isinstance(string_or_object, basestring):
            line_object = WikiRawLine(string_or_object)
        else:
            line_object = string_or_object
        self.line_objects.append(line_object)

    @staticmethod
    def join(list_of_items):
        return "%s%s%s" % (
            WikiData.split_on,
            WikiData.split_on.join(list_of_items),
            WikiData.split_on)

    def render(self):
        data = [line_object.render() for line_object in self.line_objects]
        return WikiData.join(data).strip()


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
    form.getControl(name="field.email").value = username
    form.getControl(name="field.password").value = password
    form.submit(name="field.actions.continue")


def get_wiki_data(form_data):
    print "Extracting blueprints and work items from wiki page..."
    wiki_data = WikiData(form_data)
    if not wiki_data.has_blueprints:
        raise ValueError("No blueprints found.")
    return wiki_data


def get_correlated_status(wiki_data, path):
    blueprints = [x.id for x in wiki_data.get_blueprints()]
    database = create_database("sqlite:%s" % path)
    store = Store(database)
    results = store.find(Blueprint, Blueprint.name.is_in(blueprints))
    if results.count() == 0:
        raise ValueError("No matches found in the database.")
    # XXX We may want to munge status data differently here...
    return [(x.name, x.implementation) for x in results]


def remove_old_milestones(work_items):
    # XXX implement!
    return work_items


def sort_work_items(work_items):

    # XXX may not need this now...
    def check_milestone(milestone):
        # If no milestone is set in the options, we want to include all
        # milestones; if one is set, we want to limit to the legal values.
        legal_milestone_values = [next_milestone, None, u""]
        if next_milestone == None:
            return True
        elif milestone in legal_milestone_values:
            return True
        return False

    results = sorted([(x.blueprint.numeric_priority, x.spec, x.description, x)
                     for x in results])
                     #for x in results if check_milestone(x.milestone)])
    return [z for w, x, y, z in results]


def get_status(path, date=None, next_milestone=None):
    print "Getting work items status..."

    database = create_database("sqlite:%s" % path)
    store = Store(database)
    results = store.find(
        WorkItem,
        WorkItem.date == date,
        WorkItem.spec == Blueprint.name)
    if results.count() == 0:
        raise ValueError("No matches found in the database.")
    # Order them by priority, blueprint name, and then description. We're not
    # using Storm/SQL ordering here, because the values for priority don't sort
    # well.
    filtered_results = []
    for result in remove_old_milestones(results):
        milestone = Milestone
        filtered_results.append(result)

    return sort_work_items(filtered_results)

def update_wiki_data(browser, status_data):
    print "Modifiying wiki data with latest status info..."
    raise NotImplementedError


def get_new_wiki_data(browser, status_data, prepend="", postpend=""):
    print "Updating the wiki page with the latest data..."

    def strip_html(html):
        return re.sub(r'<[^>]*?>', '', html)

    def color_priority(text):
        if text == "Essential":
            color = "FF6666"
        elif text == "High":
            color = "FF9966"
        elif text == "Medium":
            color = "FFFF66"
        elif text == "Low":
            color = "66FFFF"
        return "<#%s> %s" % (color, text)

    header = WikiWorkItem.join([
        "'''Spec'''", "'''Priority'''", "'''Work Item Description'''",
        "'''Status'''"])
    wiki_data = WikiData()
    wiki_data.add_line(header)
    # Get all postponed work items.
    last_priority = None
    for result in status_data:
        # Check to see if the priority is the same; if so, just add the work
        # item; if it has changed, insert a separator and then add the work
        # item.
        priority = result.blueprint.priority
        if last_priority != None and priority != last_priority:
            wiki_data.add_separator()
        # Check to see if the work item was dropped or just postponed.
        status = result.milestone or "<#ffff00> %s" % DROPPED
        work_item = WikiWorkItem(
            "UbuntuSpec:%s" % result.spec, color_priority(priority),
            strip_html(result.description), status)
        wiki_data.add_line(work_item)
        last_priority = priority
    return wiki_data.render()


def update_page_data(browser, database):
    browser.getLink("Edit").click()
    form = browser.getForm("editor")
    data = form.getControl(name="savetext").value
    wiki_data = get_wiki_data(data)
    status_data = get_correlated_status(wiki_data, database)
    update_wiki_data(browser, status_data)
    form.submit(name="button_save")


def replace_page_data(browser, options):
    browser.getLink("Edit").click()
    form = browser.getForm("editor")
    if options.trivial:
        form.getControl(name="trivial").value = [True]
    status_data = get_status(
        options.database, date=options.date, next_milestone=options.milestone)
    data = get_new_wiki_data(browser, status_data)
    form.getControl(name="savetext").value = data
    form.submit(name="button_save")


def main(options):
    browser = Browser(options.url)
    login(browser, options.username, options.password)
    replace_page_data(browser, options)


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
