import os, tempfile, unittest

from pyopenerp import const, util


class ConfigUtilTestCase(unittest.TestCase):

    def setUp(self):
        self.src = os.path.abspath("../" + const.SAMPLE_CONFIG)
        self.fd, self.fullpath = tempfile.mkstemp()

    def test_read_config(self):
        data = util.read_config(self.src, self.fullpath)
        self.assertEqual(data, open(self.src).read())
