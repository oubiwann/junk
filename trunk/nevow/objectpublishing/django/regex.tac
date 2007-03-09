import re

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
            <li><a href="/yourstuff/blog"><span nevow:render="username"/>'s Blog</a></li>
            </ul>
        </html>''')

    def getUsernameFromCookie(self, context):
        return 'Joe'

    def render_username(self, context, data):
        return self.getUsernameFromCookie(context)

class BlogResource(YourStuffResource):
    addSlash = True
    docFactory = loaders.xmlstr('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0
        Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en"
            xmlns:nevow="http://nevow.com/ns/nevow/0.1">
            <h1><span nevow:render="username"/>'s Blog</h1>
            <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/yourstuff/blog">Blog Home</a></li>
            <li><a href="/yourstuff/blog/archives">Blog Archives</a></li>
            <li><a href="/yourstuff/blog/recent">Recent Posts</a></li>
            <li>Test permalink: <a href="/yourstuff/blog/2006/03/06/on_that_day.html">A post on 2006.03.06</a></li>
            </ul>
            <p><span nevow:render="note"/></p>
            <p><span nevow:render="moreNotes"/></p>
        </html>''')

    def render_note(self, context, data):
        if not hasattr(self, 'note'):
            return ''
        return self.note

    def render_moreNotes(self, context, data):
        return '''In a real blog application, we would parse those segments and
            return resources such as "archives", "recent posts", "post", etc.,
            as appropriate.'''
        
    def locateChild(self, context, segments):
        self.note = "In blog, we got the following path segments:", str(segments)
        return self, ()
        # in a real app, do a bunch of checks, returning appropriate resources,
        # and then finally returning the super():
        #return super(BlogResource, self).locateChild(context, segments)

urlPatterns = (
    (r'/mystuff(.*)', MyStuffResource),
    (r'/yourstuff/blog(.*)', BlogResource),
    (r'/yourstuff(.*)', YourStuffResource),
)

class SiteRoot(rend.Page):
    addSlash = True
    docFactory = loaders.xmlstr('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0
        Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en"
            xmlns:nevow="http://nevow.com/ns/nevow/0.1">
            <h1>Home</h1>
            <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/mystuff">See My Stuff</a></li>
            <li><a href="/yourstuff">See Your Stuff</a></li>
            </ul>
        </html>''')

    def locateChild(self, context, segments):
        path = '/'.join(('',) + segments)
        for regex, resource in urlPatterns:
            print regex, path
            match = re.match(regex, path)
            if match:
                print match.groups()
                newPath = match.groups()[0]
                r = resource()
                if newPath in ['', '/']:
                    return r, ()
                else:
                    newSegments = newPath.split('/')[1:]
                    return r.locateChild(context, newSegments)
        return super(SiteRoot, self).locateChild(context, segments)

from twisted.application import service
from twisted.application import strports

from nevow import appserver

application = service.Application('Site')

root = SiteRoot()
site = appserver.NevowSite(root)

# setup the web server
server = strports.service('tcp:8080', site)
server.setServiceParent(application)
