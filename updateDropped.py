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

import mechanize

from zope.testbrowser.browser import Browser

from storm.locals import (
    DateTime, Reference, ReferenceSet, Store, Storm, Unicode, create_database)


DONE = u"done"
INPROGRESS = u"inprogress"
TODO = u"todo"
POSTPONED = u"postponed"
DROPPED = u"dropped"

COLOR_ESSENTIAL = "#FF6666"
COLOR_HIGH = "#FF9966"
COLOR_MEDIUM = "#FFFF66"
COLOR_LOW = "#66FFFF"
COLOR_UNDEFINED = "#CCCCCC"
COLOR_WHITE = "#FFFFFF"

AGENT_STRING = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.3) Gecko/20100404 Ubuntu/10.04 (lucid) Firefox/3.6.3"


class Milestone(object):
    """
    A convenience object that encapsulates milestone comparison logic.
    """
    # IMPORTANT!!! This needs to be maintained with every new milestone that
    # makes it into the SQLite database. Until those values are put into a
    # lookup table with a human-defined, explicit ordering, this has to be done
    # manually.
    legal_values = [
        u"jaunty-updates",
        u"lucid-alpha-1",
        u"lucid-alpha-2",
        u"lucid-alpha-3",
        u"ubuntu-10.04-beta-1",
        u"ubuntu-10.04-beta-2",
        u"ubuntu-10.04",
        u"later",
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

    @staticmethod
    def get_future_milestones(name):
        past_milestone = Milestone(name)
        return Milestone.legal_values[(past_milestone.value + 1):]


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
    is_dropped = False


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
        elif self.priority in ["None", "Not", None, "Undefined"]:
            return 5


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


class WikiRow(WikiRawLine):
    """
    A convenience object for creating general moin moin table rows.
    """
    def __init__(self, *cells):
        self.cells = [unicode(x) for x in cells]

    @staticmethod
    def join(list_of_items):
        return "%s%s%s" % (
            WikiWorkItem.split_on,
            WikiWorkItem.split_on.join(list_of_items),
            WikiWorkItem.split_on)

    def render(self):
        return self.join(self.cells)


class WikiWorkItem(WikiRow):
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
        self.header_line = header_line
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

    def add_separator(self, color="#999999"):
        separator = WikiWorkItem.join(["<%s>" % color] * 4)
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
    form.getControl(name="email").value = username
    form.getControl(name="password").value = password
    form.submit(name="continue")
    # Fourth state (confirm SSO)
    browser.getForm().getControl(name="yes").click()


def get_wiki_data(form_data):
    print "Extracting blueprints and work items from wiki page..."
    wiki_data = WikiData(form_data)
    if not wiki_data.has_blueprints:
        raise ValueError("No blueprints found.")
    return wiki_data


def get_postponed_work_items(database_path, date, for_milestone):
    print "\tGetting dropped work items for milestone %s..." % for_milestone
    database = create_database("sqlite:%s" % database_path)
    store = Store(database)
    results = store.find(
        WorkItem,
        WorkItem.date == date,
        WorkItem.milestone == for_milestone,
        WorkItem.status == POSTPONED,
        WorkItem.spec == Blueprint.name)
    if results.count() == 0:
        raise ValueError("No matches found in the database.")
    return results


def get_future_work_items_lookup(
    database_path, date, for_milestone, descriptions):
    print "\tGetting lookup for future work items..."
    future_milestones = Milestone.get_future_milestones(for_milestone)
    database = create_database("sqlite:%s" % database_path)
    store = Store(database)
    future_work_items = store.find(
        WorkItem,
        WorkItem.date == date,
        WorkItem.description.is_in(descriptions),
        WorkItem.milestone.is_in(future_milestones),
        WorkItem.spec == Blueprint.name)
    return dict([(x.description, x) for x in future_work_items])


def remove_old_milestones(work_items, for_milestone):
    print "\tRemoving old milestones from the result set..."
    if not for_milestone:
        return work_items
    filtered = []
    for_milestone = Milestone(for_milestone)
    for work_item in work_items:
        # If there's no milestone defined or if the milestone associated with
        # the work item is greater than or equal to the one that we've asked
        # about, we want to keep the work item for futher comparisons.
        # Otherwise, we're not interested.
        if (not work_item.milestone or 
            Milestone(work_item.milestone) >= for_milestone):
            filtered.append(work_item)
    return filtered


def sort_work_items(work_items):
    """
    Order the work items by priority, blueprint name, and then description.
    We're not using Storm/SQL ordering here, because the values for priority
    don't sort well.
    """
    print "\tSorting results..."
    results = sorted([(x.blueprint.numeric_priority, x.spec, x.description, x)
                     for x in work_items])
    return [work_item for x, y, z, work_item in results]


def get_dropped_and_postponed(database_path, date=None, for_milestone=None):
    """
    To get the status of the work items, several things need to happend:
        1) get a list of work items that are defined for the given milestone
           and which have status set to "postponed";
        2) get a list of work items for all future milestones, regardless of
           status;
        3) set the status to dropped if a work item has no identical item
           (description) in a future milestone;
        4) otherwise, set the status to postponed using the future-most
           milestone as the status.
    """
    print "Getting postponed and dropped work items..."
    current_work_items = get_postponed_work_items(
        database_path, date, for_milestone)
    descriptions = [x.description for x in current_work_items]
    future_lookup = get_future_work_items_lookup(
        database_path, date, for_milestone, descriptions)
    postponed = []
    dropped = []
    for work_item in current_work_items:
        if work_item.description in future_lookup.keys():
            future_work_item = future_lookup.get(work_item.description)
            postponed.append(future_work_item)
        else:
            work_item.is_dropped = True
            dropped.append(work_item)
    return (dropped, postponed)


def get_new_wiki_data(browser, status_data, prepend="", postpend=""):
    print "Updating the wiki page with the latest data..."

    def strip_html(html):
        return re.sub(r'<[^>]*?>', '', html)

    def color_priority(text):
        if text == "Essential":
            color = COLOR_ESSENTIAL
        elif text == "High":
            color = COLOR_HIGH
        elif text == "Medium":
            color = COLOR_MEDIUM
        elif text == "Low":
            color = COLOR_LOW
        elif text in ["None", "Not", None, "Undefined"]:
            color = COLOR_UNDEFINED
        else:
            print "\tHrm, found unknown priority: %s" % text
            return text
        return "<%s> %s" % (color, text)

    header = WikiWorkItem.join([
        "'''Spec'''", "'''Priority'''", "'''Work Item Description'''",
        "'''Status'''"])
    wiki_data = WikiData()
    wiki_data.add_line(header)
    # Get all postponed work items.
    last_priority = None
    for work_item in status_data:
        # Check to see if the priority is the same; if so, just add the work
        # item; if it has changed, insert a separator and then add the work
        # item.
        priority = work_item.blueprint.priority
        if last_priority != None and priority != last_priority:
            wiki_data.add_separator()
        # Check to see if the work item was dropped or just postponed.
        if work_item.is_dropped:
            status = "<#ffff00> %s" % DROPPED
        else:
            status = work_item.milestone
        work_item_object = WikiWorkItem(
            "UbuntuSpec:%s" % work_item.spec, color_priority(priority),
            strip_html(work_item.description), status)
        wiki_data.add_line(work_item_object)
        last_priority = priority
    return wiki_data.render()


def get_stats(data):
    essential, high, medium, low = (0, 0, 0, 0)
    total = len(data)
    for datum in data:
        priority = datum.blueprint.priority
        if priority == "Essential":
            essential += 1
        elif priority == "High":
            high += 1
        elif priority == "Medium":
            medium += 1
        elif priority == "Low":
            low += 1
    return (essential, high, medium, low, total)


def make_summary(dropped, postponed):
    print "\tGenerating summary..."
    colors = (COLOR_ESSENTIAL, COLOR_HIGH, COLOR_MEDIUM, COLOR_LOW, COLOR_WHITE)
    postponed_stats = get_stats(postponed)
    dropped_stats = get_stats(dropped)
    summed_stats = map(sum, zip(postponed_stats, dropped_stats))
    postponed_colors = map(
        lambda x:"<%s>%s" % (x[1], x[0]), zip(postponed_stats, colors))
    dropped_colors = map(
        lambda x:"<%s>%s" % (x[1], x[0]), zip(dropped_stats, colors))
    summed_colors = map(
        lambda x:"<%s>%s" % (x[1], x[0]), zip(summed_stats, colors))
    summary_data = WikiData()
    summary_data.add_line(WikiRow(
        " ", "'''Essential Priority'''", "'''High Priority'''",
        "'''Medium Priority'''", "'''Low Priority'''", "'''Total Items'''"))
    summary_data.add_line(WikiRow(
        "Postponed Tasks", *postponed_colors))
    summary_data.add_line(WikiRow(
        "Dropped Tasks", *dropped_colors))
    summary_data.add_line(WikiRow(
        "'''Total Tasks'''", *summed_colors))
    data = "== Stats Summary ==%s" % WikiData.split_on
    data += summary_data.render()
    data += "%s== Postponed and Dropped Work Items  ==%s" % (
        WikiData.split_on, WikiData.split_on)
    return data


def replace_page_data(browser, options):
    browser.getLink("Edit").click()
    form = browser.getForm("editor")
    if options.trivial:
        form.getControl(name="trivial").value = [True]
    dropped, postponed = get_dropped_and_postponed(
        options.database, date=options.date, for_milestone=options.milestone)
    status_data = sort_work_items(postponed + dropped)
    data = make_summary(dropped, postponed)
    data += get_new_wiki_data(browser, status_data).encode("utf-8")
    form.getControl(name="savetext").value = data
    form.submit(name="button_save")


def main(options):
    mech_browser = mechanize.Browser()
    mech_browser.addheaders = [("User-agent", AGENT_STRING)]
    mech_browser.set_handle_robots(None)
    browser = Browser(options.url, mech_browser=mech_browser)
    login(browser, options.username, options.password)
    replace_page_data(browser, options)
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
