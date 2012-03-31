import time
import sys

import logging, logging.config
import os.path

from ConfigParser import SafeConfigParser as ConfigParser
from optparse import OptionParser

from lxcrunner.vmsuite import VMSuite

LOG = logging.getLogger(__name__)

def parse_cmdline():
    """Parse command line options."""

    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config",
                      default="/etc/lxcrunner/config.ini",
                      help="path to config file")
    parser.add_option("-s", "--suite", dest="suite",
                      help="name of suite in config file")
    parser.add_option("-e", "--end-stage", dest="endstage",
                      choices=["prepare", "startsuite", "run", "cleanup"],
                      help="name of final stage when lxcrunner must stop. "
                           "The stages are 'prepare', 'startsuite', 'run', "
                           "'cleanup'")
    parser.add_option("-u", "--unique", dest="unique",
                      action="store_true", default=False,
                      help="add unique suffix to VM guests")

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

    if options.suite:
        suite_name = options.suite
    else:
        suite_name = config.get("DEFAULT", "vm_suite")

    LOG.debug("Deploy suite '%s'", suite_name)
    vmsuite = VMSuite(suite_name, config, options.unique)
    vmsuite.prepare()

    if options.endstage == "prepare":
        LOG.info("'prepare' is the final stage: exiting...")
        return

    LOG.debug("Start suite...")
    vmsuite.start_suite()
    time.sleep(5)

    if options.endstage == "startsuite":
        LOG.info("'startsuite' is the final stage: exiting...")
        return

    try:
        vmsuite.run()
    finally:
        if options.endstage == "run":
            LOG.info("'run' is the final stage: don't clean up")
            return
        vmsuite.cleanup()

if __name__ == '__main__':
    main()
