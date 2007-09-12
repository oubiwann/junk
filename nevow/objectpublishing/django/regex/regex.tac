from twisted.application import service
from twisted.application import strports

from nevow import appserver

from root import SiteRoot

application = service.Application('Site')

root = SiteRoot()
site = appserver.NevowSite(root)

# setup the web server
server = strports.service('tcp:8080', site)
server.setServiceParent(application)
