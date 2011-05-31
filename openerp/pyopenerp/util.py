import os

from pyopenerp import const, exceptions


def write_default_config(dest_dir=""):
    """
    Create a default config file.

    This function's parameters are used only for testing purposes.
    """
    src_file = os.path.abspath(const.CONFIG_TEMPLATE)
    if not os.path.isfile(src_file):
        raise exceptions.PyOpenERPConfigurationError(
            "Could not locate default configuration file '%s'." % src_file)
    src = open(src_file)
    data = src.read()
    src.close()
    basedir = os.path.expanduser(dest_dir or const.CONFIG_DIR)
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    dest_file = os.path.join(basedir, const.CONFIG_FILE)
    dest = open(dest_file, "w+")
    dest.write(data)
    dest.close()


def read_config(default_config="", dest_dir=""):
    """
    Read the config file; if it's not there, create a default one and then
    re-attempt a read.

    This function's parameters are used only for testing purposes.
    """
    config_file = os.path.expanduser(default_config or const.DEFAULT_CONFIG)
    if not os.path.isfile(config_file):
        write_default_config(dest_dir)
    config = open(config_file)
    data = config.read()
    config.close()
    return data
