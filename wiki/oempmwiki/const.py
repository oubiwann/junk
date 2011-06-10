data_host = "spreadsheets1.google.com"
data_path = "/a/canonical.com/spreadsheet/pub"
data_query = "hl=en_US&hl=en_US&single=true&gid=0&output=csv"
data_url = "https://%s%s?%s" % (data_host, data_path, data_query)
DATA_URL_TEMPLATE = data_url + "&key=%s"
AGENT_STRING = ("Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.3) "
                "Gecko/20100404 Ubuntu/10.04 (lucid) Firefox/3.6.3")
