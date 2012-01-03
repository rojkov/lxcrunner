import sys
import tarfile

import os.path
import logging, logging.config

from ConfigParser import SafeConfigParser as ConfigParser
from optparse import OptionParser
from jinja2 import Environment as JinjaEnv, FileSystemLoader as JinjaLoader

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

    return options

class VMEnvError(Exception):
    pass

class VMGuest(object):
    """Represents VM guest."""

    def __init__(self, name, config, context = None):
        """Constructor."""

        if context is None:
            context = {}

        self.name = name
        vmguest_section = "vmguest_%s" % name
        self.type = config.get(vmguest_section, "tpl_type")
        tpl_section = "tpl_%s" % self.type
        self.vm_dir = config.get(tpl_section, "vm_dir")
        tpls = [tpl.strip()
                for tpl in config.get(tpl_section, "tpls").split(",")]
        self.tpls = [(tpl_name, config.get(tpl_section, tpl_name))
                     for tpl_name in tpls]
        self.tarball = config.get(tpl_section, "tarball")
        context.update(
            dict([(n[4:], v) for (n, v) in config.items(vmguest_section)
                             if n.startswith("ctx_")]))
        context["name"] = name
        self.context = context

        self._check_preconditions()

    def create(self):
        """Create VM guest."""

        def renderfile(tpl, path, context):
            """Render file from template."""
            file_h = open(path, 'w')
            file_h.write(tpl.render(context))
            file_h.close()

        vm_path = os.path.join(self.vm_dir, self.name)
        LOG.debug("Create VM folder '%s'" % vm_path)
        os.mkdir(vm_path, 0755)

        LOG.debug("Extract template")
        vm_tpl = tarfile.open(name=self.tarball)
        vm_tpl.extractall(path=vm_path)
        vm_tpl.close()

        rootfs_path = os.path.join(vm_path, "rootfs")
        jenv = JinjaEnv(loader=JinjaLoader(os.path.join("templates",
                                                        self.type)))
        # VM config
        LOG.debug("Render VM config")
        tpl = jenv.get_template("vm_config.tpl")
        renderfile(tpl, os.path.join(vm_path, "config"),
                   {"rootfs": rootfs_path})

        for tpl_name, tpl_path in self.tpls:
            LOG.debug("Render %s" % tpl_path)
            tpl = jenv.get_template("%s.tpl" % tpl_name)
            renderfile(tpl, os.path.join(rootfs_path, tpl_path), self.context)

    def _check_preconditions(self):
        """Verify the environment is ready."""
        if not os.path.isdir(self.vm_dir):
            msg = "VM directory '%s' doesn't exists" % self.vm_dir
            LOG.error(msg)
            raise VMEnvError(msg)
        if not os.path.exists(self.tarball):
            msg = "VM template '%s' not found" % self.tarball
            LOG.error(msg)
            raise VMEnvError(msg)


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

    LOG.debug("Deploy derek setup")
    context = dict([(n[4:], v) for (n, v) in config.items("derek_setup")
                               if n.startswith("ctx_")])
    guests = (VMGuest(name.strip(), config, context)
              for name in config.get("derek_setup", "vmguests").split(","))
    for guest in guests:
        guest.create()

if __name__ == '__main__':
    main()
