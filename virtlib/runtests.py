import time
import sys

import logging, logging.config
import os.path

from ConfigParser import SafeConfigParser as ConfigParser
from optparse import OptionParser

from virtlib.vmsetup import VMSetup

LOG = logging.getLogger(__name__)

def parse_cmdline():
    """Parse command line options."""

    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config",
                      default="/etc/virtlib/config.ini",
                      help="path to config file")

    (options, _) = parser.parse_args()
    return options

def main():
    """Entry point."""

    options = parse_cmdline()

    if os.path.exists(options.config):
        LOG.debug("Reading config file %s" % options.config)
        logging.config.fileConfig(options.config,
                                  disable_existing_loggers=False)
        config = ConfigParser()
        config.read(options.config)
        # TODO: update 'options' from 'config' or vice versa

    else:
        logging.basicConfig(level=logging.DEBUG)
        LOG.error("Config file not found. Exiting...")
        sys.exit(1)

    LOG.debug("Deploy derek setup")
    vmsetup = VMSetup("derek_setup", config)
    vmsetup.prepare()
    LOG.debug("Testing...")
    time.sleep(5)
    vmsetup.run()
    vmsetup.cleanup()

if __name__ == '__main__':
    main()
