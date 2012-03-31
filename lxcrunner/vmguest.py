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

    def __str__(self):
        """Return string representation."""
        return self.container

    def __init__(self, name, config, context = None, suffix = ""):
        """Constructor."""

        if context is None:
            context = {}
        else:
            context = context.copy()

        self.name = name
        if suffix:
            self.container = "%s-%s" % (name, suffix)
        else:
            self.container = name
        vmguest_section = "vmguest_%s" % name
        self.type = config.get(vmguest_section, "tpl_type")
        tpl_section = "tpl_%s" % self.type
        self.vm_dir = config.get(tpl_section, "vm_dir")
        self.tpl_dir = config.get(vmguest_section, "tpl_dir")
        try:
            tpls = [tpl.strip()
                    for tpl in config.get(tpl_section, "tpls").split(",")]
        except NoOptionError:
            tpls = []
        self.tpls = [(tpl_name, config.get(tpl_section, tpl_name))
                     for tpl_name in tpls]
        self.tarball = config.get(tpl_section, "tarball")

        try:
            self.execute_cmd = config.get(vmguest_section, "execute")
        except NoOptionError:
            self.execute_cmd = None
        self.is_executable = self.execute_cmd is not None

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

        vm_path = os.path.join(self.vm_dir, self.container)
        LOG.debug("Create VM folder '%s'" % vm_path)
        os.mkdir(vm_path, 0755)

        LOG.debug("Extract template")
        vm_tpl = tarfile.open(name=self.tarball)
        vm_tpl.extractall(path=vm_path)
        vm_tpl.close()

        rootfs_path = os.path.join(vm_path, "rootfs")
        self.context["rootfs"] = rootfs_path

        jenv = JinjaEnv(loader=JinjaLoader(os.path.join(self.tpl_dir,
                                                        self.type)))
        jenv.globals["split"] = lambda x: x.split(",")

        # VM config
        LOG.debug("Render VM config")
        tpl = jenv.get_template("vm_config.tpl")
        renderfile(tpl, os.path.join(vm_path, "config"), self.context)

        for tpl_name, tpl_info in self.tpls:
            # "path/to/tpl 744" => {'path': 'path/to/tpl', 'chmod': 744}
            tinfo = dict(zip(["path", "chmod"], tpl_info.split()))
            LOG.debug("Render %s" % tinfo['path'])
            tpl = jenv.get_template("%s.tpl" % tpl_name)
            path = os.path.join(rootfs_path, tinfo['path'])
            renderfile(tpl, path, self.context)
            if 'chmod' in tinfo:
                LOG.debug("chmod %s to %s" % (path, tinfo['chmod']))
                os.chmod(path, int(tinfo['chmod'], 8))
        LOG.debug("Used context %r" % self.context)
        self.state = self.ST_STOPPED

    def start(self):
        """Start VM guest."""

        assert not self.is_executable

        LOG.debug("Starting '%s'" % self.container)
        self._check_transition(self.ST_RUNNING)
        try:
            subprocess.check_call(["/usr/bin/lxc-start", "-n", self.container,
                                   "-d",
                                   "-o", "/var/log/lxc.%s.log" % self.container,
                                   "-l", "DEBUG"],
                                  close_fds=True)
            subprocess.check_call(["/usr/bin/lxc-wait", "-n", self.container,
                                   "-o", "/var/log/lxc.%s.log" % self.container,
                                   "-l", "DEBUG", "-s", "RUNNING"],
                                  close_fds=True)
        except subprocess.CalledProcessError, err:
            raise VMError("Can't start %s" % self.container)
        self.state = self.ST_RUNNING

    def execute(self):
        """Execute a command inside VM guest."""

        assert self.is_executable

        LOG.debug("Executing command '%s' in '%s'" % (self.execute_cmd,
                                                      self.container))
        self._check_transition(self.ST_RUNNING)
        try:
            cmd = ["/usr/bin/lxc-start", "-n", self.container, "-o",
                   "/var/log/lxc.%s.log" % self.container, "-l", "DEBUG"]
            cmd.extend(self.execute_cmd.split())
            subprocess.check_call(cmd, close_fds=True)
        except subprocess.CalledProcessError, err:
            msg = "Can't start %s: %s" % (self.container, err)
            LOG.error(msg)
            raise VMError(msg)

    def stop(self):
        """Stop VM guest."""

        LOG.debug("Stopping '%s'" % self.container)
        self._check_transition(self.ST_STOPPED)
        try:
            subprocess.check_call(["/usr/bin/lxc-stop", "-n", self.container,
                                   "-o", "/var/log/lxc.%s.log" % self.container,
                                   "-l", "DEBUG"],
                                  close_fds=True)
            subprocess.check_call(["/usr/bin/lxc-wait", "-n", self.container,
                                   "-o", "/var/log/lxc.%s.log" % self.container,
                                   "-l", "DEBUG", "-s", "STOPPED"],
                                  close_fds=True)
        except subprocess.CalledProcessError, err:
            raise VMError("Can't stop %s" % self.container)
        self.state = self.ST_STOPPED

    def destroy(self):
        """Destroy VM guest."""

        LOG.debug("Destroying '%s'" % self.container)
        self._check_transition(self.ST_INCOMPLETE)
        subprocess.check_call(["/usr/bin/lxc-destroy", "-n", self.container])
        self.state = self.ST_INCOMPLETE

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
