from nevow import rend
from nevow import loaders

class MyStuffResource(rend.Page):

    docFactory = loaders.xmlstr('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0
        Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en"
            xmlns:nevow="http://nevow.com/ns/nevow/0.1">
            <h1>My Stuff</h1>
            <a href="/">Home</a>
        </html>''')

class SiteRoot(rend.Page):

    docFactory = loaders.xmlstr('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0
        Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en"
            xmlns:nevow="http://nevow.com/ns/nevow/0.1">
            <h1>Home</h1>
            <a href="/mystuff">My Stuff</a>
        </html>''')

    child_mystuff = MyStuffResource()

from twisted.application import service
from twisted.application import strports

from nevow import appserver

application = service.Application('Site')

root = SiteRoot()
site = appserver.NevowSite(root)

# setup the web server
server = strports.service('tcp:8080', site)
server.setServiceParent(application)
