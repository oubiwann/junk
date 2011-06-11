import csv, urllib2

from oempmwiki import config, const


def get_google_csv_reader(data_key):
    data_url = const.DATA_URL_TEMPLATE % data_key
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
