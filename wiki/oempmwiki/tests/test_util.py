import unittest

from oempmwiki import const, util


class ColorCellTestCase(unittest.TestCase):

    def test_get_status_for_name(self):
        self.assertEqual(util.get_status("going swimmingly"), const.OK)
        self.assertEqual(util.get_status("SOME concerns"), const.WARN)
        self.assertEqual(util.get_status("we're in trouble"), const.ALERT)

    def test_get_name_color(self):
        self.assertEqual(util.get_name_color("Going Swimmingly"), "#66FFFF")
        self.assertEqual(util.get_name_color("some concerns"), "#FFFF66")
        self.assertEqual(util.get_name_color("we're IN trouble"), "#FF6666")

    def test_get_status_color(self):
        self.assertEqual(util.get_status_color(const.OK), "#66FFFF")
        self.assertEqual(util.get_status_color(const.WARN), "#FFFF66")
        self.assertEqual(util.get_status_color(const.ALERT), "#FF6666")

    def test_color_cell(self):
        self.assertEqual(
            util.color_cell("going swimmingly"),
            "<#66FFFF> going swimmingly")
        self.assertEqual(
            util.color_cell("some concerns"),
            "<#FFFF66> some concerns")
        self.assertEqual(
            util.color_cell("we're in trouble"),
            "<#FF6666> we're in trouble")
