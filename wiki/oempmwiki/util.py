import csv, urllib2

from oempmwiki import const


def get_google_csv_reader(data_key):
    data_url = const.DATA_URL_TEMPLATE % data_key
    file_handle = urllib2.urlopen(data_url)
    return csv.reader(file_handle)
