import os
from inspect import getmembers
from cStringIO import StringIO

from nevow import flat
from nevow import inevow
from nevow.loaders import xmlstr
from nevow.loaders import xmlfile

from genshi.template import MarkupTemplate
from genshi.template import TemplateLoader

rendPageAttrs = [x[0] for x in getmembers(rend.Page)]

def getObjectData(obj)
    for attr, val in getmembers(obj):
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
    return data

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
        data = {}
        renderer = inevow.IRenderer(ctx)
        data = getObjectData(renderer)
        # save a copy of the original, unmolested template, complete with
        # Genshi markup
        orig = self.template
        tmpl = MarkupTemplate(self.template)
        xmlStr = tmpl.generate(**data).render('xhtml')
        self.template = xmlStr
        nevowRun = super(genshistr, self).load(ctx=ctx,
            preprocessors=preprocessors)
        # null out Nevow's caching of the template
        self._cache = None
        # revert to the unparsed Genshi template so that genshi attrs/methods
        # have the chance to generate fresh data
        self.template = orig
        return nevowRun

class genshifile(xmlfile):

    def _reallyLoad(self, path, ctx, preprocessors):

        renderer = inevow.IRenderer(ctx)
        data = getObjectData(renderer)
        absPath = os.path.abspath(self._filename)
        templateDir = os.path.dirname(absPath)
        loader = TemplateLoader([templateDir])
        orig = self.template
        tmpl = loader.load(absPath)
        xmlStr = tmpl.generate(**data).render('xhtml')
        fh = StringIO(xmlStr)
        doc = flat.flatsax.parse(fh, self.ignoreDocType,
            self.ignoreComment)
        for proc in preprocessors:
            doc = proc(doc)
        doc = flat.precompile(doc, ctx)
        if self.pattern is not None:
            doc = inevow.IQ(doc).onePattern(self.pattern)
        return doc
