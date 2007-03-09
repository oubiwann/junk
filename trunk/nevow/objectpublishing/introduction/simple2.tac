from nevow import rend
from nevow import loaders

class MyStuffResource(rend.Page):
    addSlash = True
    docFactory = loaders.xmlstr('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0
        Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en"
            xmlns:nevow="http://nevow.com/ns/nevow/0.1">
            <h1>My Stuff</h1>
            <ul>
            <li><a href="/">Home</a></li>
            </ul>
        </html>''')

class YourStuffResource(rend.Page):
    addSlash = True
    docFactory = loaders.xmlstr('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0
        Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en"
            xmlns:nevow="http://nevow.com/ns/nevow/0.1">
            <h1>Your Stuff</h1>
            <p>You are <span nevow:render="username"/> and your stuff is here.</p>
            <ul>
            <li><a href="/">Home</a></li>
            </ul>
        </html>''')

    def __init__(self, username='', *args, **kwds):
        super(YourStuffResource, self).__init__(*args, **kwds)
        self.username = username

    def render_username(self, context, data):
        return self.username

class SiteRoot(rend.Page):
    addSlash = True
    docFactory = loaders.xmlstr('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0
        Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en"
            xmlns:nevow="http://nevow.com/ns/nevow/0.1">
            <h1>Home</h1>
            <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/mystuff/">See My Stuff</a></li>
            <li><a href="/yourstuff/">See Your Stuff</a></li>
            </ul>
        </html>''')

    child_mystuff = MyStuffResource()

    def getUsernameFromCookie(self, context):
        return 'Joe'

    def child_yourstuff(self, context):
        username = self.getUsernameFromCookie(context)
        return YourStuffResource(username)

from twisted.application import service
from twisted.application import strports

from nevow import appserver

application = service.Application('Site')

root = SiteRoot()
site = appserver.NevowSite(root)

# setup the web server
server = strports.service('tcp:8080', site)
server.setServiceParent(application)
