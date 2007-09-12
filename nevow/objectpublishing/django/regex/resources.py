from nevow import rend
from nevow import loaders

class MyStuffResource(rend.Page):
    addSlash = True
    docFactory = loaders.xmlfile('templates/mystuff.xhtml')

class YourStuffResource(rend.Page):
    addSlash = True
    docFactory = loaders.xmlfile('templates/yourstuff.xhtml')

    def getUsernameFromCookie(self, context):
        return 'Joe'

    def render_username(self, context, data):
        return self.getUsernameFromCookie(context)

class BlogResource(YourStuffResource):
    addSlash = True
    docFactory = loaders.xmlfile('templates/blog.xhtml')

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

