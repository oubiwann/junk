"""
To use this script, you need to pass your Launchpad username (email address)
and password, as well as the full path to the SQLite database you are working
with:

    %s username password /home/manager/Downloads/lucid.db
"""
from zope.testbrowser.browser import Browser
from storm.locals import DateTime, Store, Unicode, create_database

DONE = "done"
INPROGRESS = "inprogress"
TODO = "todo"
POSTPONED = "postponed"

WIKI_PAGE = "https://wiki.ubuntu.com/Oubiwann/TestPage"
#WIKI_PAGE = "https://wiki.ubuntu.com/ReleaseTeam/FeatureStatus/Alpha3Postponed"


class WorkItem(object):
    """
    The data model for the work items in the SQLite database.
    """
    __storm_table__ = "work_items"
    description = Unicode()
    spec = Unicode()
    status = Unicode()
    assignee = Unicode()
    milestone = Unicode()
    date = DateTime()

    def is_dropped(self):
        if self.status == POSTPONED and self.milestone.strip():
            return False
        return True


class Blueprint(object):
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


Blueprint.work_items = ReferenceSet(Blueprint.name, WorkItem.spec)


class WikiWorkItem(object):
    """
    A convenience object for storing and accessing work item data from the wiki
    page.
    """
    split_on = "||"
    marker = "UbuntuSpec:"

    def __init__(self, header_line, data_line):
        self.header_line = header_line
        self.line = data_line
        self.headers = None

    def parse(self, header_line, data_line):
        self.headers = self.extract_headers(self.header_line)
        self.set_attributes(data_line)
        

    @staticmethod
    def split_fields(line):
        # Skip first and last element, since those are non-entires, artifacts
        # of the split.
        return [x.strip() 
                for x in header_line.split(WikiWorkItem.split_on)[1:-1]

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


class WikiRawLine(object):
    """
    An object that simply holds a raw wiki line for later use.
    """
    def __init__(self, line):
        self.line = line


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

    def __init__(self, form_data):
        self.raw_data = form_data
        self.lines = form_data.split(self.split_on)
        self.header_line = self.lines[0]
        self.line_objects = []
        self.blueprints = {}
        self.has_blueprints = False
        for line in lines:
            if line.startswith(
                "%s%s" % (WikiWorkItem.split_on, WikiWorkItem.marker)):
                line_object = WikiWorkItem(header_line, line)
                blueprint = self.get_blueprint(line_object.spec)
                blueprint.add_work_item(line_object)
                self.has_blueprints = True
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

    @staticmethod
    def join(list_of_items):
        return "%s%s%s" % (
            WikiData.split_on,
            WikiData.split_on.join(list_of_items), 
            WikiData.split_on)


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


def get_status(wiki_data, path):
    print "Getting work items status..."
    database = create_database("sqlite:%s" % path)
    store = Store(database)
    results = store.find(WorkItem, WorkItem.status==POSTPONED)
    if results.count() == 0:
        raise ValueError("No matches found in the database.")
    # Order them by priority, blueprint name, and then description.
    results.order_by(
        WorkItem.blueprint.priority, WorkItem.spec, WorkItem.description)
    return results


def update_wiki_data(browser, status_data):
    print "Modifiying wiki data with latest status info..."


def get_new_wiki_data(browser, status_data, prepend="", postpend=""):
    print "Updating the wiki page with the latest data..."
    wiki_data = WikiData()
    separator = WikiWorkItem.join(["<#999999>"]*4)
    # Get all postponed work items.
    last_priority = None
    for result in status_data:
        if result.is_dropped()
            # color last cell orange, make contents "dropped"
            status = None
        else:
            # color last cell yellow, make contents milestone
            status = None
        work_item = WikiWorkItem(
            result.spec, result.blueprint.priority, result.description, status)
        # Check to see if the priority is the same; if so, just add the work
        # item; if it has changed, insert a separator and then add the work
        # item.
    return wiki_data


def update_page_data(browser, database):
    browser.getLink("Edit").click()
    form = browser.getForm("editor")
    data = form.getControl(name="savetext").value
    wiki_data = get_wiki_data(data)
    status_data = get_correlated_status(wiki_data, database)
    update_wiki_data(browser, status_data)
    form.submit(name="XXX")


def replace_page_data(browser, database, trivial=False):
    browser.getLink("Edit").click()
    form = browser.getForm("editor")
    if trivial:
        # XXX - update the checkbox with trival = True
        pass
    data = form.getControl(name="savetext").value
    wiki_data = get_wiki_data(data)
    status_data = get_status(wiki_data, database)
    data = get_new_wiki_data(
        browser, status_data, prepend=wiki_data.header_line)
    form.getControl(name="savetext").value = data
    form.submit(name="XXX")


def main(username, password, database):
    browser = Browser(WIKI_PAGE)
    login(browser, username, password)
    replace_page_data(browser, database)


if __name__ == "__main__":
    import sys
    try:
        # XXX add support for:
        # - passing a date
        # - passing a wiki page
        # - last milestone
        # - next milestone
        main(*sys.argv[1:])
    except TypeError:
        # Not enough parameters were passed
        print __doc__ % sys.argv[0]
        sys.exit(1)
