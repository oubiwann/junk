import os

from genshi.template import MarkupTemplate
from genshi.template import TemplateLoader

from nevow import flat
from nevow import inevow
from nevow.loaders import xmlstr
from nevow.loaders import xmlfile

from cStringIO import StringIO

class genshistr(xmlstr):

    def load(self, ctx=None, preprocessors=()):
        attrs = inevow.IRenderer(ctx).__dict__
        tmpl = MarkupTemplate(self.template)
        xmlStr = tmpl.generate(**attrs).render('xhtml')
        self.template = xmlStr
        return  super(genshistr, self).load(ctx=ctx,
            preprocessors=preprocessors)

class genshifile(xmlfile):

    def _reallyLoad(self, path, ctx, preprocessors):

        attrs = inevow.IRenderer(ctx).__dict__
        absPath = os.path.abspath(self._filename)
        templateDir = os.path.dirname(absPath)
        loader = TemplateLoader([templateDir])
        tmpl = loader.load(absPath)
        xmlStr = tmpl.generate(**attrs).render('xhtml')

        fh = StringIO(xmlStr)
        doc = flat.flatsax.parse(fh, self.ignoreDocType,
            self.ignoreComment)
        for proc in preprocessors:
            doc = proc(doc)
        doc = flat.precompile(doc, ctx)

        if self.pattern is not None:
            doc = inevow.IQ(doc).onePattern(self.pattern)

        return doc
