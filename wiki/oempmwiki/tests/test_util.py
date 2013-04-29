import unittest

from oempmwiki import const, util


class ColorCellTestCase(unittest.TestCase):

    def test_get_status_for_name(self):
        self.assertEqual(util.get_status("going swimmingly"), const.OK)
        self.assertEqual(util.get_status("SOME concerns"), const.WARN)
        self.assertEqual(util.get_status("we're in trouble"), const.ALERT)

    def test_get_name_color(self):
        self.assertEqual(util.get_name_color("Going Swimmingly"), "#CCFFCC")
        self.assertEqual(util.get_name_color("some concerns"), "#FFFFCC")
        self.assertEqual(util.get_name_color("we're IN trouble"), "#FFCCCC")

    def test_get_status_color(self):
        self.assertEqual(util.get_status_color(const.OK), "#CCFFCC")
        self.assertEqual(util.get_status_color(const.WARN), "#FFFFCC")
        self.assertEqual(util.get_status_color(const.ALERT), "#FFCCCC")

    def test_color_cell(self):
        self.assertEqual(
            util.color_cell("going swimmingly"),
            "<#CCFFCC> going swimmingly")
        self.assertEqual(
            util.color_cell("some concerns"),
            "<#FFFFCC> some concerns")
        self.assertEqual(
            util.color_cell("we're in trouble"),
            "<#FFCCCC> we're in trouble")
