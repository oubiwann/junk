import csv, urllib2


data_host = "spreadsheets1.google.com"
data_path = "/a/canonical.com/spreadsheet/pub"
data_key = "0ArIWq6t1tnKldGtGRkxGRzVuczBJcW83b3VlRlYyUGc"
data_query = "hl=en_US&hl=en_US&key=%s&single=true&gid=0&output=csv" % data_key
data_url = "https://%s%s?%s" % (data_host, data_path, data_query)


data = urllib2.urlopen(data_url).read()
print data

