import logging
import uuid
import os.path

from lxcrunner.vmguest import VMGuest

LOG = logging.getLogger(__name__)

class VMSuite(object):
    """Suite of VM guests."""

    def __init__(self, name, config, unique=False):
        """Constructor."""

        self.name = name
        context = dict([(n[4:], v) for (n, v) in config.items(name)
                                   if n.startswith("ctx_")])
        if unique:
            suffix = uuid.uuid4().hex[:16]
        else:
            suffix = ""
        self.guests = [VMGuest(n.strip(), config, context, suffix=suffix)
                       for n in config.get(name, "vmguests").split(",")]

    def prepare(self):
        """Prepare virtual environment."""

        # check if container exists already
        for guest in self.guests:
            assert not os.path.exists(os.path.join(guest.vm_dir,
                                                   guest.container)), \
                    "Guest '%s' already exists" % guest

        LOG.debug("Prepare environment for '%s'" % self.name)
        for guest in self.guests:
            guest.create()

    def start_suite(self):
        """Start suite guests."""

        LOG.debug("Start suite of guests for '%s'" % self.name)
        for guest in self.guests:
            if not guest.is_executable:
                guest.start()

    def run(self):
        """Run commands inside guests."""

        LOG.debug("Run targets")
        for guest in self.guests:
            if guest.is_executable:
                guest.execute()

    def cleanup(self):
        """Clean up."""
        LOG.debug("Do cleanup.")
        for guest in self.guests:
            if not guest.is_executable:
                guest.stop()
            guest.destroy()
