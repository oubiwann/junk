import re

from nevow import rend
from nevow import loaders

import resources

urlPatterns = (
    (r'/mystuff(.*)', resources.MyStuffResource),
    (r'/yourstuff/blog(.*)', resources.BlogResource),
    (r'/yourstuff(.*)', resources.YourStuffResource),
)

class SiteRoot(rend.Page):
    addSlash = True
    docFactory = loaders.xmlfile('templates/home.xhtml')

    def locateChild(self, context, segments):
        path = '/'.join(('',) + segments)
        for regex, resource in urlPatterns:
            match = re.match(regex, path)
            if match:
                newPath = match.groups()[0]
                r = resource()
                if newPath in ['', '/']:
                    return r, ()
                else:
                    newSegments = newPath.split('/')[1:]
                    return r.locateChild(context, newSegments)
        return super(SiteRoot, self).locateChild(context, segments)
