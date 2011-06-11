from optparse import OptionParser

from oempmwiki import table, util, writer


class Script(object):
    """
    The base class for OEM PM Wiki scripts.
    """
    def get_option_parser(self):
        """ 
        Options common to all scripts.
        """
        return OptionParser(usage=self.get_usage())

    def get_usage(self):
        usage = "Usage: %prog [options]"
        description = self.__doc__
        return "%s\n%s" % (usage, description)

    def get_options(self):
        parser = self.get_option_parser()
        (options, args) = parser.parse_args()
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
        if None in [options.url, options.username, options.password]:
            parser.error("Options -U, -u and -p are all required. "
                         "For more information, use --help.")
        return options


class ProjectStatusScript(WikiScript):
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

