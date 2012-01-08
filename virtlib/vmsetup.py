import logging
import tarfile
import os.path
import subprocess

from ConfigParser import NoOptionError
from jinja2 import Environment as JinjaEnv, FileSystemLoader as JinjaLoader

LOG = logging.getLogger(__name__)

class VMError(Exception):
    pass

class VMGuest(object):
    """Represents VM guest."""

    ST_INCOMPLETE = "incomplete"
    ST_STOPPED = "stopped"
    ST_RUNNING = "running"

    _TRANSITIONS = {
        ST_INCOMPLETE: (ST_STOPPED),
        ST_STOPPED: (ST_INCOMPLETE, ST_RUNNING),
        ST_RUNNING: (ST_STOPPED)
    }

    def __init__(self, name, config, context = None):
        """Constructor."""

        if context is None:
            context = {}
        else:
            context = context.copy()

        self.name = name
        vmguest_section = "vmguest_%s" % name
        self.type = config.get(vmguest_section, "tpl_type")
        tpl_section = "tpl_%s" % self.type
        self.vm_dir = config.get(tpl_section, "vm_dir")
        try:
            tpls = [tpl.strip()
                    for tpl in config.get(tpl_section, "tpls").split(",")]
        except NoOptionError:
            tpls = []
        self.tpls = [(tpl_name, config.get(tpl_section, tpl_name))
                     for tpl_name in tpls]
        self.tarball = config.get(tpl_section, "tarball")

        # target command
        def get_opt(optname):
            trg_defaults = {
                "target_user": "nobody",
                "target_cmd": None
            }
            try:
                return config.get(vmguest_section, optname)
            except NoOptionError:
                return trg_defaults[optname]
        self.target = {
            "cmd": get_opt("target_cmd"),
            "user": get_opt("target_user")
        }

        # context
        context.update(
            dict([(n[4:], v) for (n, v) in config.items(vmguest_section)
                             if n.startswith("ctx_")]))
        context["name"] = name
        self.context = context
        self.state = self.ST_INCOMPLETE

        self._check_preconditions()

    def create(self):
        """Create VM guest."""

        def renderfile(tpl, path, context):
            """Render file from template."""
            file_h = open(path, 'w')
            file_h.write(tpl.render(context))
            file_h.close()

        self._check_transition(self.ST_STOPPED)

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
        jenv.globals["split"] = lambda x: x.split(",")

        # VM config
        LOG.debug("Render VM config")
        tpl = jenv.get_template("vm_config.tpl")
        renderfile(tpl, os.path.join(vm_path, "config"),
                   {"rootfs": rootfs_path})

        for tpl_name, tpl_path in self.tpls:
            LOG.debug("Render %s" % tpl_path)
            tpl = jenv.get_template("%s.tpl" % tpl_name)
            renderfile(tpl, os.path.join(rootfs_path, tpl_path), self.context)
        LOG.debug("Used context %r" % self.context)
        self.state = self.ST_STOPPED

    def start(self):
        """Start VM guest."""

        LOG.debug("Starting '%s'" % self.name)
        self._check_transition(self.ST_RUNNING)
        try:
            subprocess.check_call(["/usr/bin/lxc-start", "-n", self.name, "-d",
                                   "-o", "/var/log/lxc.%s.log" % self.name,
                                   "-l", "DEBUG"],
                                  close_fds=True)
            subprocess.check_call(["/usr/bin/lxc-wait", "-n", self.name,
                                   "-o", "/var/log/lxc.%s.log" % self.name,
                                   "-l", "DEBUG", "-s", "RUNNING"],
                                  close_fds=True)
        except subprocess.CalledProcessError, err:
            raise VMError("Can't start %s" % self.name)
        self.state = self.ST_RUNNING

    def stop(self):
        """Stop VM guest."""

        LOG.debug("Stopping '%s'" % self.name)
        self._check_transition(self.ST_STOPPED)
        try:
            subprocess.check_call(["/usr/bin/lxc-stop", "-n", self.name,
                                   "-o", "/var/log/lxc.%s.log" % self.name,
                                   "-l", "DEBUG"],
                                  close_fds=True)
            subprocess.check_call(["/usr/bin/lxc-wait", "-n", self.name,
                                   "-o", "/var/log/lxc.%s.log" % self.name,
                                   "-l", "DEBUG", "-s", "STOPPED"],
                                  close_fds=True)
        except subprocess.CalledProcessError, err:
            raise VMError("Can't stop %s" % self.name)
        self.state = self.ST_STOPPED

    def destroy(self):
        """Destroy VM guest."""

        LOG.debug("Destroying '%s'" % self.name)
        self._check_transition(self.ST_INCOMPLETE)
        subprocess.check_call(["/usr/bin/lxc-destroy", "-n", self.name])
        self.state = self.ST_INCOMPLETE

    def run_target(self):
        """Run target command."""

        if not self.target["cmd"]:
            LOG.debug("No target command defined for %s" % self.name)
            return
        trgcmd = ["su", "-", self.target["user"], "-c"]
        trgcmd.append(self.target["cmd"])
        LOG.debug("Target command: %r" % trgcmd)
        subprocess.call(trgcmd)

    def _check_preconditions(self):
        """Verify the environment is ready."""
        if not os.path.isdir(self.vm_dir):
            msg = "VM directory '%s' doesn't exists" % self.vm_dir
            LOG.error(msg)
            raise VMError(msg)
        if not os.path.exists(self.tarball):
            msg = "VM template '%s' not found" % self.tarball
            LOG.error(msg)
            raise VMError(msg)

    def _check_transition(self, new_state):
        """Check if transition to new state is allowed."""
        if new_state not in self._TRANSITIONS[self.state]:
            raise VMError("Transition '%s -> %s' is impossible" % \
                          (self.state, new_state))

class VMSetup(object):
    """Setup of VM guest collection."""

    def __init__(self, name, config):
        """Constructor."""

        self.name = name
        context = dict([(n[4:], v) for (n, v) in config.items(name)
                                   if n.startswith("ctx_")])
        self.guests = [VMGuest(n.strip(), config, context)
                       for n in config.get(name, "vmguests").split(",")]

    def prepare(self):
        """Prepare virtual environment."""

        LOG.debug("Prepare environment for '%s'" % self.name)
        for guest in self.guests:
            guest.create()
            guest.start()

    def run(self):
        """Run target commands inside guests."""

        LOG.debug("Run targets")
        for guest in self.guests:
            guest.run_target()

    def cleanup(self):
        """Clean up."""
        LOG.debug("Do cleanup.")
        for guest in self.guests:
            guest.stop()
            guest.destroy()

