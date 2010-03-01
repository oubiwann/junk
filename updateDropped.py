"""
To use this script, you need to pass your Launchpad username (email address)
and password, as well as the full path to the SQLite database you are working
with:

    %s username password /home/manager/Downloads/lucid.db
"""
from zope.testbrowser.browser import Browser
from storm.locals import create_database, Unicode, Store


WIKI_PAGE = "https://wiki.ubuntu.com/ReleaseTeam/FeatureStatus/Alpha3Postponed"


class Blueprint(object):
    """
    The data model for the 
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


def get_status(blueprints, path):
    print "Getting feature status..."
    database = create_database("sqlite:%s" % path)
    store = Store(database)
    results = store.find(Blueprint, Blueprint.name.is_in(blueprints))
    if results.count() == 0:
        raise ValueError("No matches found in the database.")
    # XXX We may want to munge status data differently here... 
    return [(x.name, x.implementation) for x in results]


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


def get_blueprint_names(form_data):
    print "Extracting blueprint names from wiki page..."
    lines = form_data.split("\r\n")
    split_on = "||"
    marker = "UbuntuSpec:"
    data = [unicode(x.split(split_on)[1].lstrip(marker).strip()) for x in lines
            if x.startswith("%s%s" % (split_on, marker))]
    if len(data) == 0:
        raise ValueError("No blueprints found.")
    return data


def update_wiki_data(browser, status_data):
    print "Modifiying wiki data with latest status info..."
    import pdb;pdb.set_trace()


def update_page(browser, database):
    browser.getLink("Edit").click()
    form = browser.getForm("editor")
    data = form.getControl(name="savetext").value
    blueprint_names = get_blueprint_names(data)
    status_data = get_status(blueprint_names, database)
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
