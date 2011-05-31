from pyopenerp import model, scripts
from pyopenerp.config import get_config_data


class Monthly(scripts.Script):

    def __init__(self, config_data):
        self.openerp = model.Model(config_data)

    def run(self):
        pass
