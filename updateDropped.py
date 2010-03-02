"""
To use this script, you need to pass your Launchpad username (email address)
and password, as well as the full path to the SQLite database you are working
with:

    %s username password /home/manager/Downloads/lucid.db
"""
from zope.testbrowser.browser import Browser
from storm.locals import (
    DateTime, Reference, ReferenceSet, Store, Storm, Unicode, create_database)


DONE = u"done"
INPROGRESS = u"inprogress"
TODO = u"todo"
POSTPONED = u"postponed"
DROPPED = u"dropped"

WIKI_PAGE = "https://wiki.ubuntu.com/Oubiwann/TestPage"
#WIKI_PAGE = "https://wiki.ubuntu.com/ReleaseTeam/FeatureStatus/Alpha3Postponed"


class OptionsError(Exception):
    pass


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

    def is_dropped(self):
        if self.milestone:
            milestone = True
            if not self.milestone.strip():
                milestone = False
        milestone = False
        if self.status == POSTPONED and milestone:
            return False
        return True


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

    def add_separator(self, color="#999999"):
        separator = WikiWorkItem.join(["<#999999>"]*4)
        self.line_objects.append(separator)

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


def get_status(path, date):
    print "Getting work items status..."
    database = create_database("sqlite:%s" % path)
    store = Store(database)
    results = store.find(
        WorkItem,
        WorkItem.date == date,
        WorkItem.status == POSTPONED,
        WorkItem.spec == Blueprint.name)
    if results.count() == 0:
        raise ValueError("No matches found in the database.")
    # Order them by priority, blueprint name, and then description. We're not
    # using Storm/SQL ordering here, because the values for priority don't sort
    # well.
    results = sorted([(x.blueprint.numeric_priority, x.spec, x.description, x)
                     for x in results])
    return [z for w, x, y, z in results]


def update_wiki_data(browser, status_data):
    print "Modifiying wiki data with latest status info..."
    raise NotImplementedError


def get_new_wiki_data(browser, status_data, prepend="", postpend=""):
    print "Updating the wiki page with the latest data..."
    header = WikiWorkItem.join(
        ["Spec", "Priority", "Work Item Description", "Status"])
    separator = WikiWorkItem.join(["<#999999>"] * 4)
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
            wiki_data.add_line(separator)
        # Check to see if the work item was dropped or just postponed.
        if result.is_dropped():
            # Change the cell color to yellow if it was dropped.
            status = "<#ffff00> %s" % DROPPED
        else:
            status = result.milestone
        work_item = WikiWorkItem(
            # XXX sanitize or convert html a-href's
            result.spec, priority, result.description, status)
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


def replace_page_data(browser, database, trivial=False):
    browser.getLink("Edit").click()
    form = browser.getForm("editor")
    if trivial:
        form.getControl(name="trivial").value = [True]
    # XXX use a passed parameter for date
    status_data = get_status(database, u"2010-03-01")
    data = get_new_wiki_data(browser, status_data)
    form.getControl(name="savetext").value = data
    form.submit(name="button_save")


def main(username, password, database):
    browser = Browser(WIKI_PAGE)
    login(browser, username, password)
    # XXX forcing trivial for testing... need to change it back when done
    replace_page_data(browser, database, trivial=True)


if __name__ == "__main__":
    import sys
    try:
        # XXX add support for:
        # - passing a date
        # - passing a wiki page
        # - last milestone
        # - next milestone
        # - add support for trivial
        main(*sys.argv[1:])
    except OptionsError:
        # Not enough parameters were passed
        print __doc__ % sys.argv[0]
        sys.exit(1)
