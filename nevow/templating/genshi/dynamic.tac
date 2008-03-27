from inspect import getmembers
from datetime import datetime

from nevow import rend
from nevow import page
from nevow import inevow
from nevow import loaders
from nevow.loaders import xmlstr

from genshi.template import MarkupTemplate

rendPageAttrs = [x[0] for x in getmembers(rend.Page)]

class genshistr(xmlstr):

    def load(self, ctx=None, preprocessors=()):
        data = {}
        renderer = inevow.IRenderer(ctx)
        for attr, val in getmembers(renderer):
            # skip non-public methods
            if attr.startswith('_'): continue
            # skip custom Nevow methods
            if attr.startswith('child_'): continue
            if attr.startswith('render_'): continue
            if attr.startswith('data_'): continue
            # skip nevow.rend.Page methods
            if attr in rendPageAttrs:
                continue
            obj = getattr(renderer, attr)
            if callable(obj):
                val = obj()
            data[attr] = val
        orig = self.template
        tmpl = MarkupTemplate(self.template)
        xmlStr = tmpl.generate(**data).render('xhtml')
        self.template = xmlStr
        nevowRun = super(genshistr, self).load(ctx=ctx,
            preprocessors=preprocessors)
        self._cache = None
        self.template = orig
        return nevowRun

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
            xmlns:nevow="http://nevow.com/ns/nevow/0.1"
            xmlns:genshi="http://genshi.edgewall.org/">
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

class GenshiStuffResource(YourStuffResource):
    addSlash = True
    docFactory = genshistr('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0
        Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en"
            xmlns:nevow="http://nevow.com/ns/nevow/0.1"
            xmlns:genshi="http://genshi.edgewall.org/">
            <h1>Genshi Test</h1>
            <ul>
            <li><a href="/">Home</a></li>
            </ul>
            <div>
              <span>Nevow thinks you are <span nevow:render="username"/></span>
            </div>
            <div>
              <span>Genshi thinks you are ${username}</span>
            </div>
            <div>
              <span genshi:with="y=7; x=y**2; z=x+10">$x $y $z</span>
            </div>
            <div>
              <span>Timestamp is ${date}</span>
            </div>
        </html>''')
    def __init__(self, *args, **kwds):
        super(GenshiStuffResource, self).__init__(*args, **kwds)

    def date(self):
        return datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    date = property(date)

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
            <li><a href="/genshistuff/">See Genshi Stuff</a></li>
            </ul>
        </html>''')

    child_mystuff = MyStuffResource()

    def getUsernameFromCookie(self, context):
        return 'Joe'

    def child_yourstuff(self, context):
        username = self.getUsernameFromCookie(context)
        return YourStuffResource(username)

    def child_genshistuff(self, context):
        username = self.getUsernameFromCookie(context)
        return GenshiStuffResource(username)

from twisted.application import service
from twisted.application import strports

from nevow import appserver

application = service.Application('Site')

root = SiteRoot()
site = appserver.NevowSite(root)

# setup the web server
server = strports.service('tcp:8080', site)
server.setServiceParent(application)
