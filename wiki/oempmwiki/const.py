LOGIN_FORM = "gaia_loginform"
data_host = "spreadsheets1.google.com"
data_path = "/a/canonical.com/spreadsheet/pub"
data_query = "hl=en_US&hl=en_US&single=true&&output=csv"
data_url = "https://%s%s?%s" % (data_host, data_path, data_query)
TAB_TEMPLATE = "&gid=%s"
DATA_URL_TEMPLATE = data_url + "&key=%s"
AGENT_STRING = ("Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.3) "
                "Gecko/20100404 Ubuntu/10.04 (lucid) Firefox/3.6.3")
OK = 1
WARN = 2
ALERT = 3

PROJ_SUMM_KEY = "0AvtVCtEQ2EvXdEluMU9TUXV4anNYUXUta0RETU5GeEE"
PREMIUM = 0
INTERNAL = 2
MAINSTREAM = 3
PREM_MAINT = 4

CONFIG_TEMPLATE = "./etc/config.ini"
CONFIG_DIR = "~/.oempmwiki"
CONFIG_FILE = "%s/config.ini" % CONFIG_DIR
