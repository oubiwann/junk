import csv, os, urllib2
import ConfigParser
from datetime import datetime

from oempmwiki import config, const


def get_google_csv_reader(data_key, tab_id=None):
    data_url = const.DATA_URL_TEMPLATE % data_key
    if tab_id != None:
        data_url = data_url + const.TAB_TEMPLATE % tab_id
    file_handle = urllib2.urlopen(data_url)
    return csv.reader(file_handle)


def normalize(name):
    return name.lower().strip()


def get_status(name):
    for status, data in config.project_states.items():
        if data.get("name") == normalize(name):
            return status


def get_status_color(status):
    status = config.project_states.get(status)
    if status != None:
        return status.get("color")


def get_name_color(name):
    status = get_status(normalize(name))
    if status != None:
        return get_status_color(status)


def color_cell(cell_data):
    color = get_name_color(cell_data) or ""
    if color:
        color = "<%s> " % color
    return "%s%s" % (color, cell_data)


def write_default_config(dest_dir=""):
    """
    Create a default config file.

    This function's parameters are used only for testing purposes.
    """
    src_file = os.path.abspath(const.CONFIG_TEMPLATE)
    if not os.path.isfile(src_file):
        src_file = const.CONFIG_TEMPLATE
        if not os.path.isfile(src_file):
            src_file = os.path.join("..", const.CONFIG_TEMPLATE)
            if not os.path.isfile(src_file):
                raise IOError(
                    "File not found: could not locate default configuration "
                    "file '%s'." % src_file)
    src = open(src_file)
    data = src.read()
    src.close()
    basedir = os.path.expanduser(dest_dir or const.CONFIG_DIR)
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    dest_file = os.path.expanduser(const.CONFIG_FILE)
    dest = open(dest_file, "w+")
    dest.write(data)
    dest.close()
    # set the perms on it to 600
    os.chmod(dest_file, 0600)
    return dest_file


def read_config(config_file="", dest_dir=""):
    """
    Read the config file; if it's not there, create a default one and then
    re-attempt a read.

    This function's parameters are used only for testing purposes.
    """
    if not os.path.isfile(config_file):
        raise IOError(
            "File not found: you need to create a configuration file; see "
            "the '--bootstrap' option by re-running the script with '--help'")
    config = open(config_file)
    data = config.read()
    config.close()
    return data


def encode(string):
    return string.ljust(32).encode("base64").strip()


def decode(string):
    return string.decode("base64").strip()


def get_bootstrap_config_data():
    print "Obtianing configuration data..."
    data = {}
    data["google_username"] = raw_input("What is your google username/email? ")
    data["google_password"] = encode(
        raw_input("What is your google password? "))
    data["google_doc_key"] = raw_input(
        "What is the key ID for the google spreadsheet? ")
    data["wiki_username"] = raw_input("What is your wiki username? ")
    data["wiki_password"] = encode(raw_input("What is your wiki password? "))
    data["wiki_url"] = raw_input("What is the wiki page URL? ")
    return data


def backup_config(filename):
    if os.path.exists(filename):
        now = datetime.now()
        os.rename(filename, "%s.backup-%s" % (
            filename, now.strftime("%Y%m%d.%H%M%S")))


def update_config(data):
    config = ConfigParser.SafeConfigParser(data)
    with open(os.path.expanduser(const.CONFIG_FILE), "wb") as config_file:
        config.write(config_file)


def bootstrap_config(default_config=None):
    config_file = os.path.expanduser(default_config or const.CONFIG_FILE)
    backup_config(config_file)
    write_default_config()
    data = get_bootstrap_config_data()
    update_config(data)
