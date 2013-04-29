from datetime import datetime

from nevow import rend
from nevow import loaders

import myloaders

class MyStuffResource(rend.Page):
    addSlash = True
    docFactory = loaders.xmlfile('templates/mystuff.xhtml')

class YourStuffResource(rend.Page):
    addSlash = True
    docFactory = loaders.xmlfile('templates/yourstuff.xhtml')

    def __init__(self, username='', *args, **kwds):
        super(YourStuffResource, self).__init__(*args, **kwds)
        self.username = username

    def render_username(self, context, data):
        return self.username

class GenshiStuffResource(YourStuffResource):
    addSlash = True
    docFactory = myloaders.genshifile('templates/genshimix.xhtml')

    def __init__(self, *args, **kwds):
        super(GenshiStuffResource, self).__init__(*args, **kwds)
        self.key = {'value': 'this is the value of the key'}
        self.doIt = True
        self.items = xrange(10)
        evenOdd = ['odd', 'even']
        self.altItems = [ (x, {'class': evenOdd[x % 2]})
            for x in list(xrange(10))]

    def date(self):
        return datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    date = property(date)

    def render_username(self, context, data):
        return self.username

class SiteRoot(rend.Page):
    addSlash = True
    docFactory = loaders.xmlfile('templates/home.xhtml')
    child_mystuff = MyStuffResource()

    def getUsernameFromCookie(self, context):
        return 'Joe'

    def child_yourstuff(self, context):
        username = self.getUsernameFromCookie(context)
        return YourStuffResource(username)

    def child_genshistuff(self, context):
        username = self.getUsernameFromCookie(context)
        return GenshiStuffResource(username)
