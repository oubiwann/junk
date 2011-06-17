import mechanize

from zope.testbrowser.browser import fix_exception_name, Browser as BaseBrowser


class Browser(BaseBrowser):
    """
    We need to override some behaviours from zope.testbrowser...
    """
    def open(self, url, data=None):
        url = str(url)
        self._start_timer()
        try:
            try:
                try:
                    self.mech_browser.open(url, data)                                                                                                             
                except Exception, e:
                    fix_exception_name(e)
                    raise
            except mechanize.HTTPError, e:
                if e.code >= 200 and e.code <= 299:
                    # 200s aren't really errors
                    pass
                if e.code in [403, 404]:
                    # 403s and 404s can still return content
                    pass
                elif self.raiseHttpErrors:
                    raise
        finally:
            self._stop_timer()
            self._changed()



