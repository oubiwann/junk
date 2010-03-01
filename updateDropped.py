"""
To use this script, you need to pass your Launchpad username and password, as
well as the full path to the SQLite database you are working with.
"""
from zope.testbrowser.browser import Browser
from storm.locals import create_database, Unicode, Store


WIKI_PAGE = "https://wiki.ubuntu.com/ReleaseTeam/FeatureStatus/Alpha3Postponed"


class Blueprint(object):
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


def get_dropped_features(blueprints):
    database = create_database("sqlite:%s" % path)
    store = Store(database)
    results = store.find(Blueprint, Blueprint.name.is_in(blueprints))
    import pdb;pdb.set_trace()


def get_blueprint_names(form_data):
    lines = form_data.split("\r\n")
    split_on = "||"
    marker = "UbuntuSpec:"
    return [unicode(x.split(split_on)[1].lstrip(marker)) for x in lines 
            if x.startswith("%s%s" % (split_on, marker)]


def login(browser, username, password):
    browser.getLink("Log In / Register").click()
    # First stage
    form = browser.getForm("loginform")
    form.getControl(name="name").value = username
    form.getControl(name="password").value = password
    form.submit()
    # Second stage
    browser.getForm("openid_message").submit()
    # Third stage
    form = browser.getForm()
    form.getControl(name="field.email").value = username
    form.getControl(name="field.password").value = password
    form.submit(name="field.actions.continue")


def update_page(browser):
    browser.getLink("Edit").click()
    form = browser.getForm("editor")
    data = form.getControl(name="savetext").value
    blueprint_names = get_blueprint_names(data)
    dropped_features = get_dropped_features(blueprint_names)


def main(username, password, database):
    browser = Browser(WIKI_PAGE)
    login(browser, username, password)
    update_page(browser)

if __name__ == "__main__":
    import sys
    try:
        main(*sys.argv[1:])
    except TypeError:
        # Not enough parameters were passed
        print __doc__
        sys.exit(1)

"""
data = ['kernel-lucid-boot-performance ', 'kernel-lucid-kernel-config-review ', 'kernel-lucid-review-of-ubuntu-delta ', 'dx-lucid-xsplash ', 'mobile-lucid-imx51-debian-cd-to-uboot ', 'mobile-lucid-imx51-debian-cd-to-uboot ', 'mobile-lucid-imx51-debian-cd-to-uboot ', 'mobile-lucid-imx51-debian-cd-to-uboot ', 'mobile-lucid-imx51-debian-cd-to-uboot ', 'foundations-lucid-pre-desktop-lucid-startup-speed ', 'lucid-ubuntu-one-contact-picker ', 'lucid-ubuntu-one-contact-picker ', 'foundations-lucid-pre-desktop-lucid-startup-speed ', 'foundations-lucid-pre-desktop-lucid-startup-speed ', 'dx-lucid-application-indicator ', 'mobile-lucid-arm-lightweightbrowser ', 'dx-lucid-gtk-improvements ', 'dx-lucid-gtk-improvements ', 'dx-lucid-gtk-improvements ', 'dx-lucid-gtk-improvements ', 'dx-lucid-gtk-improvements ', 'desktop-lucid-xorg-triaging-diagnosis ', 'desktop-lucid-xorg-triaging-diagnosis ', 'desktop-lucid-xorg-triaging-diagnosis ', 'desktop-lucid-xorg-triaging-diagnosis ', 'desktop-lucid-startup-speed ', 'desktop-lucid-startup-speed ', 'desktop-lucid-startup-speed ', 'desktop-lucid-startup-speed ', 'desktop-lucid-startup-speed ', 'dx-lucid-application-indicator ', 'dx-lucid-application-indicator ', 'mobile-lucid-arm-per-soc-powermanagement ', 'dx-lucid-me-menu ', 'desktop-lucid-startup-speed ', 'mobile-lucid-arm-lib-tests ', 'mobile-lucid-arm-per-soc-powermanagement ', 'mobile-lucid-arm-device-tree-support ', 'mobile-lucid-arm-device-tree-support ', 'mobile-lucid-arm-device-tree-support ', 'mobile-lucid-arm-device-tree-support ', 'mobile-lucid-arm-device-tree-support ', 'desktop-lucid-xorg-triaging-diagnosis ', 'mobile-lucid-arm-per-soc-powermanagement ', 'server-lucid-uec-testing ', 'server-lucid-daily-vcs ', 'server-lucid-daily-vcs ', 'server-lucid-seeds ', 'mobile-lucid-arm-per-soc-powermanagement ', 'mobile-lucid-arm-lib-tests ', 'mobile-lucid-arm-lib-tests ', 'desktop-lucid-startup-speed ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'mobile-lucid-arm-suspend-resume-testplan ', 'desktop-lucid-startup-speed ', 'desktop-lucid-startup-speed ', 'desktop-lucid-xorg-proprietary-drivers ', 'desktop-lucid-xorg-proprietary-drivers ', 'desktop-lucid-xorg-proprietary-drivers ', 'desktop-lucid-xorg-proprietary-drivers ', 'desktop-lucid-xorg-proprietary-drivers ', 'desktop-lucid-xorg-proprietary-drivers ', 'lucid-qa-community-testing-translations ', 'dx-lucid-notifications ', 'dx-lucid-notifications ', 'dx-lucid-notifications ', 'dx-lucid-notifications ', 'dx-lucid-notifications ', 'foundations-lucid-ubiquity-partitioner-optimisation ', 'foundations-lucid-ubiquity-partitioner-optimisation ', 'foundations-lucid-ubiquity-partitioner-optimisation ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-debian-cd-cleanup ', 'mobile-lucid-arm-debian-cd-cleanup ', 'mobile-lucid-arm-debian-cd-cleanup ', 'mobile-lucid-arm-debian-cd-cleanup ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'mobile-lucid-arm-softboot-loader ', 'dx-lucid-notifications ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-alternate-media-client ', 'mobile-lucid-arm-rootstock-gui ', 'mobile-lucid-liquid ', 'mobile-lucid-liquid ', 'desktop-lucid-bug-management ', 'dx-lucid-session-menu ', 'foundations-lucid-dynamic-cdrom-handling ', 'desktop-lucid-desktop-cloud ', 'foundations-lucid-software-center-ui-improvements ', 'foundations-lucid-software-center-ui-improvements ', 'foundations-lucid-software-center-ui-improvements ', 'foundations-lucid-software-center-ui-improvements ', 'desktop-lucid-compiz-effects ', 'desktop-lucid-compiz-effects ', 'desktop-lucid-desktop-cloud ', 'server-lucid-xc2 ', 'server-lucid-xc2 ', 'server-lucid-xc2 ', 'server-lucid-xc2 ']
"""
