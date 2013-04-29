import os, tempfile, unittest

from pyopenerp import config, const


class ConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.src = os.path.abspath("../" + const.SAMPLE_CONFIG)
        self.fd, self.fullpath = tempfile.mkstemp()

    def test_read_config_data(self):
        config_data = config.get_config_data(self.src, self.fullpath)
        self.assertEqual(len(config_data.get("servers")), 4)

    def test_get_server(self):
        server_config = config.get_server(
            "host3", "db3", self.src, self.fullpath)
        self.assertEqual(
            server_config.get("url"), "https://secure-xmlrpc.host.domain/")
        self.assertEqual(
            server_config.get("username"), "carol")
        self.assertEqual(
            server_config.get("password"), "love3angle")
