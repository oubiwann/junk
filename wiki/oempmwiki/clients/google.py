import io

from zope.testbrowser.browser import Browser

from oempmwiki import const
from oempmwiki import exceptions


class Client(object):
    """
    """
    def __init__(self, config, tab_id):
        self.config = config
        self.tab_id = tab_id
        self.url = ""
        self.data = None
        self.browser = Browser()
        self.connected = False
        self.max_connect_attempts = 0
        self._connect_attempts = 0

    def get_url(self):
        data_url = const.DATA_URL_TEMPLATE % self.config.google_doc_key
        if self.tab_id != None:
            data_url = data_url + const.TAB_TEMPLATE % self.tab_id
        self.url = data_url
        return self.url

    def is_connected(self):
        try:
            url = self.browser.url.split("?")[0]
        except:
            url = ""
            self.connected = False
        if url and "ServiceLogin" not in url and "LoginAction" not in url:
            self.connected = True
        return self.connected

    def get_data(self):
        if not self.is_connected():
            self.connect()
        if self.is_connected():
            return self.browser.contents

    def get_data_stream(self):
        data = self.get_data()
        return io.BytesIO(data)

    def connect(self):
        # check to see if we've already got the page open
        if self.is_connected():
            return
        # we don't, so let's get the page
        self.browser.open(self.get_url())
        # now check to see if we need to login
        if self.is_connected():
            return
        # we do, so let's login
        form = self.browser.getForm(id=const.LOGIN_FORM)
        form.getControl(name="Email").value = self.config.google_username
        form.getControl(name="Passwd").value = self.config.google_password
        form.submit()
        self._connect_attempts += 1
        # once connected, let's get the data
        if not self.is_connected():
            if self._connect_attempts <= self.max_connect_attempts:
                self.connect()
            else:
                raise exceptions.ConnectionFailure(
                    "Maximum connection attempts reached")
