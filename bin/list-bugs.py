#!/usr/bin/env python
from lpapi.api import API


# XXX obviously, this needs to be changed to accept command line paramters
api = API("burlington", debug=True)
bugs = api.get_bugs(
    status="all",
    bug_reporter="oubiwann",
    created_since="2011-07-20 19:01:00")
api.list_bugs(bugs)
