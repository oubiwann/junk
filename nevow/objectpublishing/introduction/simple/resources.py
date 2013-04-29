from nevow import rend
from nevow import loaders

class MyStuffResource(rend.Page):

    docFactory = loaders.xmlfile('templates/mystuff.xhtml')

class SiteRoot(rend.Page):

    docFactory = loaders.xmlfile('templates/home.xhtml')
    child_mystuff = MyStuffResource()
