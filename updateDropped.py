"""
To use this script, you need to pass your Launchpad username (email address)
and password, as well as the full path to the SQLite database you are working
with:

    %s username password /home/manager/Downloads/lucid.db
"""
from zope.testbrowser.browser import Browser
from storm.locals import DateTime, Store, Unicode, create_database


WIKI_PAGE = "https://wiki.ubuntu.com/ReleaseTeam/FeatureStatus/Alpha3Postponed"


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
                "%s%s" % ( WikiWorkItem.split_on, WikiWorkItem.marker)):
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


def login(browser, username, password):
    print "Logging into the wiki..."
    browser.getLink("Log In / Register").click()
    # First stage
    print "Sending credentials to wiki..."
    form = browser.getForm("loginform")
    form.getControl(name="name").value = username
    form.getControl(name="password").value = password
    form.submit()
    # Second stage
    print "Confirming openid..."
    browser.getForm("openid_message").submit()
    # Third stage
    print "Sending launchpad credentials..."
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


def get_status(wiki_data, path):
    print "Getting feature status..."
    blueprints = [x.id for x in wiki_data.get_blueprints()]
    database = create_database("sqlite:%s" % path)
    store = Store(database)
    results = store.find(Blueprint, Blueprint.name.is_in(blueprints))
    if results.count() == 0:
        raise ValueError("No matches found in the database.")
    # XXX We may want to munge status data differently here... 
    return [(x.name, x.implementation) for x in results]


def update_wiki_data(browser, status_data):
    print "Modifiying wiki data with latest status info..."
    import pdb;pdb.set_trace()


def update_page(browser, database):
    browser.getLink("Edit").click()
    form = browser.getForm("editor")
    data = form.getControl(name="savetext").value
    wiki_data = get_wiki_data(data)
    status_data = get_status(wiki_data, database)
    update_wiki_data(browser, status_data)
    form.submit(name="XXX")


def main(username, password, database):
    browser = Browser(WIKI_PAGE)
    login(browser, username, password)
    update_page(browser, database)


if __name__ == "__main__":
    import sys
    try:
        main(*sys.argv[1:])
    except TypeError:
        # Not enough parameters were passed
        print __doc__ % sys.argv[0]
        sys.exit(1)

"""
data = ['kernel-lucid-boot-performance ', 'kernel-lucid-kernel-config-review ', 'kernel-lucid-review-of-ubuntu-delta ', 'dx-lucid-xsplash ', 'mobile-lucid-imx51-debian-cd-to-uboot ', 'mobile-lucid-imx51-debian-cd-to-uboot ', 'mobile-lucid-imx51-debian-cd-to-uboot ', 'mobile-lucid-imx51-debian-cd-to-uboot ', 'mobile-lucid-imx51-debian-cd-to-uboot ', 'foundations-lucid-pre-desktop-lucid-startup-speed ', 'lucid-ubuntu-one-contact-picker ', 'lucid-ubuntu-one-contact-picker ', 'foundations-lucid-pre-desktop-lucid-startup-speed ', 'foundations-lucid-pre-desktop-lucid-startup-speed ', 'dx-lucid-application-indicator ', 'mobile-lucid-arm-lightweightbrowser ', 'dx-lucid-gtk-improvements ', 'dx-lucid-gtk-improvements ', 'dx-lucid-gtk-improvements ', 'dx-lucid-gtk-improvements ', 'dx-lucid-gtk-improvements ', 'desktop-lucid-xorg-triaging-diagnosis ', 'desktop-lucid-xorg-triaging-diagnosis ', 'desktop-lucid-xorg-triaging-diagnosis ', 'desktop-lucid-xorg-triaging-diagnosis ', 'desktop-lucid-startup-speed ', 'desktop-lucid-startup-speed ', 'desktop-lucid-startup-speed ', 'desktop-lucid-startup-speed ', 'desktop-lucid-startup-speed ', 'dx-lucid-application-indicator ', 'dx-lucid-application-indicator ', 'mobile-lucid-arm-per-soc-powermanagement ', 'dx-lucid-me-menu ', 'desktop-lucid-startup-speed ', 'mobile-lucid-arm-lib-tests ', 'mobile-lucid-arm-per-soc-powermanagement ', 'mobile-lucid-arm-device-tree-support ', 'mobile-lucid-arm-device-tree-support ', 'mobile-lucid-arm-device-tree-support ', 'mobile-lucid-arm-device-tree-support ', 'mobile-lucid-arm-device-tree-support ', 'desktop-lucid-xorg-triaging-diagnosis ', 'mobile-lucid-arm-per-soc-powermanagement ', 'server-lucid-uec-testing ', 'server-lucid-daily-vcs ', 'server-lucid-daily-vcs ', 'server-lucid-seeds ', 'mobile-lucid-arm-per-soc-powermanagement ', 'mobile-lucid-arm-lib-tests ', 'mobile-lucid-arm-lib-tests ', 'desktop-lucid-startup-speed ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'desktop-lucid-startup-speed ', 'desktop-lucid-startup-speed ', 'desktop-lucid-xorg-proprietary-drivers ', 'desktop-lucid-xorg-proprietary-drivers ', 'desktop-lucid-xorg-proprietary-drivers ', 'desktop-lucid-xorg-proprietary-drivers ', 'desktop-lucid-xorg-proprietary-drivers ', 'desktop-lucid-xorg-proprietary-drivers ', 'lucid-qa-community-testing-translations ', 'dx-lucid-notifications ', 'dx-lucid-notifications ', 'dx-lucid-notifications ', 'dx-lucid-notifications ', 'dx-lucid-notifications ', 'foundations-lucid-ubiquity-partitioner-optimisation ', 'foundations-lucid-ubiquity-partitioner-optimisation ', 'foundations-lucid-ubiquity-partitioner-optimisation ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-debian-cd-cleanup ', 'mobile-lucid-arm-debian-cd-cleanup ', 'mobile-lucid-arm-debian-cd-cleanup ', 'mobile-lucid-arm-debian-cd-cleanup ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'dx-lucid-notifications ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-rootstock-gui ', 'mobile-lucid-liquid ', 'mobile-lucid-liquid ', 'desktop-lucid-bug-management ', 'dx-lucid-session-menu ', 'foundations-lucid-dynamic-cdrom-handling ', 'desktop-lucid-desktop-cloud ', 'foundations-lucid-software-center-ui-improvements ', 'foundations-lucid-software-center-ui-improvements ', 'foundations-lucid-software-center-ui-improvements ', 'foundations-lucid-software-center-ui-improvements ', 'desktop-lucid-compiz-effects ', 'desktop-lucid-compiz-effects ', 'desktop-lucid-desktop-cloud ', 'server-lucid-xc2 ', 'server-lucid-xc2 ', 'server-lucid-xc2 ', 'server-lucid-xc2 ']
"""
