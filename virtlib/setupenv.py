import sys
import tarfile

import os.path
import logging, logging.config

from ConfigParser import SafeConfigParser as ConfigParser
from optparse import OptionParser

LOG = logging.getLogger(__name__)

def parse_cmdline():
    """Parse command line options."""

    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config",
                      default="/etc/virtlib/config.ini",
                      help="path to config file")
    parser.add_option("-p", "--path", dest="vm_path",
                      default="/var/lib/lxc",
                      help="path to directory with virtual machines")
    parser.add_option("-t", "--template", dest="template",
                      help="path to tarball with a VM template")

    (options, args) = parser.parse_args()
    if not options.template:
        print "No template specified. Exiting..."
        sys.exit(1)

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

    LOG.debug("Check preconditions")
    if not os.path.isdir(options.vm_path):
        LOG.error("The VM directory '%s' doesn't exist" % options.vm_path)
        sys.exit(1)
    if not os.path.exists(options.template):
        LOG.error("VM template not found")
        sys.exit(1)

    vm_dir = os.path.join(options.vm_path, "testvm")
    LOG.debug("Create VM folder '%s'" % vm_dir)
    os.mkdir(vm_dir, 0755)

    LOG.debug("Extract template")
    vm_tpl = tarfile.open(name=options.template)
    vm_tpl.extractall(path=vm_dir)
    vm_tpl.close()


if __name__ == '__main__':
    main()
