from nevow import rend
from nevow import loaders

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

class SiteRoot(rend.Page):
    addSlash = True
    docFactory = loaders.xmlfile('templates/home.xhtml')
    child_mystuff = MyStuffResource()

    def getUsernameFromCookie(self, context):
        return 'Joe'

    def child_yourstuff(self, context):
        username = self.getUsernameFromCookie(context)
        return YourStuffResource(username)
