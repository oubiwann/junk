data_host = "spreadsheets1.google.com"
data_path = "/a/canonical.com/spreadsheet/pub"
data_query = "hl=en_US&hl=en_US&single=true&gid=0&output=csv"
data_url = "https://%s%s?%s" % (data_host, data_path, data_query)
DATA_URL_TEMPLATE = data_url + "&key=%s"
