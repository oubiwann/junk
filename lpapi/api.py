#!/usr/bin/env python
from datetime import datetime
import os.path

from launchpadlib.launchpad import Launchpad


def no_credentials():
    print "Can't proceed without Launchpad credential."
    import sys
    sys.exit()


class API(object):
    """
    This is a tiny convenience wrapper for the Launchpad Python library.
    
    Best resources for more information about launchpadlib:
        * https://launchpad.net/+apidoc/devel.html
        * https://help.launchpad.net/API/Examples
        * http://code.mumak.net/2010/03/get-started-with-launchpadlib.html
        * http://code.mumak.net/2010/03/launchpadlib-powerup.html
        * http://code.mumak.net/2010/03/launchpadlib-gotchas.html
    """
    def __init__(self, project_name, cachedir="", debug=False):
        if not cachedir:
            cachedir = os.path.expanduser("~/.launchpadlib/cache/")
        self.cachedir = cachedir
        self.launchpad = Launchpad.login_with(
            'bug scripts', 'production', cachedir, 
            credential_save_failed=no_credentials)
        self.project_name = project_name
        self.project = self.launchpad.projects[project_name]
        self.debug = debug

    def get_person(self, name):
        return self.launchpad.people[name]

    def get_bugs(
        self, bug_reporter="", status=None, created_since="", *args, **kwargs):
        """
        The search paramters are the ones available for the searchTasks method
        call in the API. If you go to this page:
        
            https://launchpad.net/+apidoc/devel.html#
            
        and search for "searchTasks" (they're all the same on that page), you
        will find all the available parameters.
        """
        if bug_reporter:
            bug_reporter = self.get_person(bug_reporter)
            kwargs.update({"bug_reporter": bug_reporter})
        if status:
            if status == "all":
                status = [
                    "New",
                    "Incomplete",
                    "Invalid",
                    "Won't Fix",
                    "Confirmed",
                    "Triaged",
                    "In Progress",
                    "Fix Committed",
                    'Fix Released']
            kwargs.update({"status": status})
        if created_since:
            date, time = created_since.split()
            year, month, day = date.split("-")
            hour, minute, second = time.split(":")
            params = [int(x) for x in [year, month, day, hour, minute, second]]
            created_since = datetime(*params).isoformat()
            kwargs.update({"created_since": created_since})
        return self.project.searchTasks(*args, **kwargs)

    def tag_bug(self, bug_entry, tag):
        bug = bug_entry.bug
        bug.tags = bug.tags + [tag]
        bug.lp_save()

    def list_bugs(self, bug_entries):
        for bug in bug_entries:
            print bug.title

    def tag_bugs(self, bug_entries, tag):
        for bug in bug_entries:
            if self.debug:
                print bug.title
            api.tag_bug(bug, tag)
