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
    parser.add_option("-d", "--no-run", action="store_true",
                      dest="norun", default=False,
                      help="create environment but do not run tests")
    parser.add_option("-s", "--setup", dest="setup",
                      help="name of setup in config file")

    (options, _) = parser.parse_args()
    return options

def main():
    """Entry point."""

    options = parse_cmdline()

    if os.path.exists(options.config):
        logging.config.fileConfig(options.config,
                                  disable_existing_loggers=False)
        config = ConfigParser()
        config.read(options.config)
        LOG.debug("Used config file: %s" % options.config)
        # TODO: update 'options' from 'config' or vice versa

    else:
        logging.basicConfig(level=logging.DEBUG)
        LOG.error("Config file not found. Exiting...")
        sys.exit(1)

    if options.setup:
        setup_name = options.setup
    else:
        setup_name = config.get("DEFAULT", "vm_setup")

    LOG.debug("Deploy derek setup")
    vmsetup = VMSetup(setup_name, config)
    vmsetup.prepare()

    if options.norun:
        LOG.debug("--no-run was specified: exiting...")
        return

    LOG.debug("Testing...")
    time.sleep(5)
    vmsetup.run()
    vmsetup.cleanup()

if __name__ == '__main__':
    main()
