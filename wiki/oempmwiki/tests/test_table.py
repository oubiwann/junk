import unittest

from oempmwiki import table


class BaseTestCase(unittest.TestCase):
    """
    """
    def setUp(self):
        self.test_data = [
            # header
            ['Project', 'Staus', 'Next Milestone'],
            # subheader
            ['', '', 'Name', 'Date'],
            ['Flex', 'Some concerns', 'MA3', '7/1/2011'],
            ['Dell', 'Going Swimmingly', 'GM', '6/25/2011'],
            ['Bohica', "We're in trouble", 'Z22', '5/10/2011'],
            ]


class WikiRawLineTestCase(BaseTestCase):
    """
    """
    def test_render(self):
        row = table.WikiRawLine(self.test_data[-1])
        expected = ['Bohica', "We're in trouble", 'Z22', '5/10/2011']
        self.assertEqual(row.render(), expected)


class WikiRowTestCase(BaseTestCase):
    """
    """
    def test_init(self):
        row = table.WikiRow(self.test_data[-1])
        expected = ['Bohica', "We're in trouble", 'Z22', '5/10/2011']
        self.assertEqual(row.cells, expected)

    def test_render(self):
        row = table.WikiRow(self.test_data[-1])
        expected = u"||Bohica||We're in trouble||Z22||5/10/2011||"
        self.assertEqual(row.render(), expected)


class ProjectStatusRowTestCase(unittest.TestCase):
    """
    """


class WikiTableTestCase(BaseTestCase):
    """
    """
    def test_process_headers(self):
        wiki_table = table.WikiTable(
            self.test_data, has_headers=True, has_subheaders=True)
        result = wiki_table.rows[0].cells
        self.assertEqual(result, [u'Project', u'Staus', u'Next Milestone'])
        result = wiki_table.rows[1].cells
        self.assertEqual(result, [u'', u'', u'Name', u'Date'])

    def test_compile(self):
        wiki_table = table.WikiTable(self.test_data[2:])
        result = wiki_table.rows[0].cells
        expected = [u'Flex', u'Some concerns', u'MA3', u'7/1/2011']
        self.assertEqual(result, expected)

    def test_render(self):
        wiki_table = table.WikiTable(self.test_data[2:])
        expected = (u"||Flex||Some concerns||MA3||7/1/2011||\n"
                     "||Dell||Going Swimmingly||GM||6/25/2011||\n"
                     "||Bohica||We're in trouble||Z22||5/10/2011||")
        self.assertEqual(wiki_table.render(), expected)

    def test_render_with_headers(self):
        test_data = [self.test_data[0]] + self.test_data[2:]
        wiki_table = table.WikiTable(test_data, has_headers=True)
        expected = (u"||Project||Staus||Next Milestone||\n"
                     "||Flex||Some concerns||MA3||7/1/2011||\n"
                     "||Dell||Going Swimmingly||GM||6/25/2011||\n"
                     "||Bohica||We're in trouble||Z22||5/10/2011||")
        self.assertEqual(wiki_table.render(), expected)

    def test_render_with_subheaders(self):
        wiki_table = table.WikiTable(
            self.test_data, has_headers=True, has_subheaders=True)
        expected = (u"||Project||Staus||Next Milestone||\n"
                     "||||||Name||Date||\n"
                     "||Flex||Some concerns||MA3||7/1/2011||\n"
                     "||Dell||Going Swimmingly||GM||6/25/2011||\n"
                     "||Bohica||We're in trouble||Z22||5/10/2011||")
        self.assertEqual(wiki_table.render(), expected)


class ProjectStatusTableTestCase(BaseTestCase):
    """
    """
    def test_render_with_subheaders(self):
        wiki_table = table.ProjectStatusTable(
            self.test_data, has_headers=True, has_subheaders=True)
        expected = (u"||Project||Staus||Next Milestone||\n"
                     "||||||Name||Date||\n"
                     "||Flex||<#FFFF66> Some concerns||MA3||7/1/2011||\n"
                     "||Dell||<#66FFFF> Going Swimmingly||GM||6/25/2011||\n"
                     "||Bohica||<#FF6666> We're in trouble||Z22||5/10/2011||")
        self.assertEqual(wiki_table.render(), expected)
