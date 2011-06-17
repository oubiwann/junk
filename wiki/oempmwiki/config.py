import ConfigParser
import os

from oempmwiki import const


project_states = {
    const.OK: {
        "name": "going swimmingly",
        "color": "#CCFFCC",
        },
    const.WARN: {
        "name": "some concerns",
        "color": "#FFFFCC",
        },
    const.ALERT: {
        "name": "we're in trouble",
        "color": "#FFCCCC",
        },
    }


class Config(object):

    def __init__(self, section_name):
        from oempmwiki import util
        config_file = os.path.expanduser(const.CONFIG_FILE)
        config = ConfigParser.SafeConfigParser()
        config.read(config_file)
        attrs = [
            "google_username", "google_password", "google_doc_key",
            "wiki_username", "wiki_password", "wiki_url"]
        for attr in attrs:
            value = config.get(section_name, attr)
            if attr == "google_username" and "@" in value:
                value = value.split("@")[0]
            if "password" in attr:
                value = util.decode(value)
            setattr(self, attr, value)
