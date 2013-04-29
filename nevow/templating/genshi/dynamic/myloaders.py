from inspect import getmembers

from nevow import rend
from nevow import inevow
from nevow.loaders import xmlstr

from genshi.template import MarkupTemplate

rendPageAttrs = [x[0] for x in getmembers(rend.Page)]

def getObjectData(obj):
    data = {}
    for attr, val in getmembers(obj):
        if not isinstance(attr, str):
            print "Member name is not a string!"
            print attr, val
            continue
        # skip non-public methods
        if attr.startswith('_'):
            continue
        # skip custom Nevow methods
        if attr.startswith('child_'):
            continue
        if attr.startswith('render_'):
            continue
        if attr.startswith('data_'):
            continue
        # skip nevow.rend.Page methods
        if attr in rendPageAttrs:
            continue
        member = getattr(obj, attr)
        if callable(member):
            val = member()
        print attr, val
        try:
            data[attr] = val
        except Exception, err:
            import pdb;pdb.set_trace()
    return data

def getGenshiString(template, data):
    tmpl = MarkupTemplate(template)
    return tmpl.generate(**data).render('xhtml')

class genshistr(xmlstr):

    def load(self, ctx=None, preprocessors=()):
        """
        Changes made to this 'dynamic' example (i.e., how it differs from the
        orginal, simple example):
         * the Python 'inspect' module is used to check for the methods and
           attributes of the renderer
         * any methods/attributes that are Nevow-specific are skipped
         * any callables are called
         * the origial template -- in its pre-parse form -- is preserved
         * Nevow template caching is disabled

        The method used below allows for the use of both Genshi and Nevow
        syntax in the template(s). If you will only be using Genshi, you can
        enable your own caching mechanism and not up-call to the parent class.
        """
        renderer = inevow.IRenderer(ctx)
        data = getObjectData(renderer)
        # save a copy of the original, unmolested template, complete with
        # Genshi markup
        orig = self.template
        self.template = getGenshiString(self.template, data)
        nevowRun = super(genshistr, self).load(ctx=ctx,
            preprocessors=preprocessors)
        # null out Nevow's caching of the template
        self._cache = None
        # revert to the unparsed Genshi template so that genshi attrs/methods
        # have the chance to generate fresh data
        self.template = orig
        return nevowRun

class genshifile(xmlstr):

    def __init__(self, filename):
        self._filename = filename

    def load(self, ctx=None, preprocessors=()):
        if not hasattr(self, 'orig'):
            self.orig = open(self._filename).read()
            #self._reallyLoad(self._filename, ctx, preprocessors)
        renderer = inevow.IRenderer(ctx)
        data = getObjectData(renderer)
        self.template = getGenshiString(self.orig, data)
        nevowRun = super(genshifile, self).load(ctx=ctx,
            preprocessors=preprocessors)
        # null out Nevow's caching of the template
        self._cache = None
        # revert to the unparsed Genshi template so that genshi attrs/methods
        # have the chance to generate fresh data
        self.template = self.orig
        return nevowRun
