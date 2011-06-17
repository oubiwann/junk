import csv
from optparse import OptionParser
import StringIO
import sys

from oempmwiki import config, google, table, util, writer


class Script(object):
    """
    The base class for OEM PM Wiki scripts.
    """
    def __init__(self):
        self.config = None

    def get_option_parser(self):
        """ 
        Options common to all scripts.
        """
        parser = OptionParser(usage=self.get_usage())
        parser.add_option(
            "-b", "--bootstrap", dest="is_bootstrap", action="store_true",
            help=("indicate whether you want to create a new config file "
                  "populated with default values"))
        parser.add_option(
            "-c", "--config", dest="section_name", action="store",
            help="the name of the section in your INI config file that "
                 "contains the configuration values you want to use for "
                 "this run of the script")
        return parser

    def get_usage(self):
        usage = "Usage: %prog [options]"
        description = self.__doc__
        return "%s\n%s" % (usage, description)

    def get_options(self):
        parser = self.get_option_parser()
        (options, args) = parser.parse_args()
        if options.is_bootstrap:
            util.bootstrap_config()
            sys.exit(0)
        if options.section_name:
            self.config = config.Config(options.section_name)
        return options


class WikiScript(Script):
    """
    Scripts that need to operate against a moinmoin wiki should use this as a
    baseclass.
    """
    def get_option_parser(self):
        """
        Options common to all wiki scripts.
        """
        parser = super(WikiScript, self).get_option_parser()
        config_option = parser.get_option("--config")
        config_option.help += " (e.g., the values for logging into the wiki)"
        parser.add_option(
            "-U", "--url", dest="url", action="store",
            help="the wiki URL for the page you will be working with")
        parser.add_option(
            "-u", "--username", dest="username", action="store",
            help=("the username (or email address) you use to log in to "
                  "the wiki"))
        parser.add_option(
            "-p", "--password", dest="password", action="store",
            help="the password for your username")
        return parser

    def get_options(self):
        parser = self.get_option_parser()
        options = super(WikiScript, self).get_options()
        if not options.section_name and None in [
            options.url, options.username, options.password]:
            parser.error("Options -U, -u and -p are all required if no  "
                         "configuration section name is provided. "
                         "For more information, use --help.")
        return options


class GoogleWikiScript(WikiScript):
    """
    Scripts that need to pull data from Google docs and operate against a
    moinmoin wiki should use this as a baseclass.
    """
    def __init__(self, *args, **kwargs):
        super(GoogleWikiScript, self).__init__(*args, **kwargs)
        options = self.get_options()
        self.client = google.Client(self.config, options.tab_id)

    def get_option_parser(self):
        """
        Options common to all google-wiki scripts.
        """
        parser = super(GoogleWikiScript, self).get_option_parser()
        parser.add_option(
            "-t", "--tab-id", dest="tab_id", action="store", default=0,
            help=("The ID of the spreadsheet tab that contains the desired "
                  "data"))
        return parser


class DemoProjectStatusScript(GoogleWikiScript):
    """
    Get the project status from a Google resource and write it to the wiki page
    at the given URL.
    """
    def run(self):
        data_key = "0ArIWq6t1tnKldGtGRkxGRzVuczBJcW83b3VlRlYyUGc"
        options = self.get_options()
        print "Getting data from Google..."
        reader = util.get_google_csv_reader(data_key)
        wiki_writer = writer.WikiWriter(
            options.url, options.username, options.password)
        data = [x for x in reader]
        wiki_table = table.ProjectStatusTable(
            data, has_headers=True, writer=wiki_writer)
        wiki_table.write()


class ProjectStatusScript(GoogleWikiScript):
    """
    Get the project status from a Google resource and write it to the wiki page
    at the given URL.
    """
    def run(self):
        print "Getting data from Google..."
        data = self.client.get_data()
        file_object = StringIO.StringIO()
        file_object.write(data)
        reader = csv.reader(file_object)
        wiki_writer = writer.WikiWriter(
            self.config.wiki_url, self.config.wiki_username, 
            self.config.wiki_password)
        data = [x for x in reader]
        wiki_table = table.ProjectStatusTable(
            data, has_headers=True, writer=wiki_writer)
        wiki_table.write()
