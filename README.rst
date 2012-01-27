LXC runner
==========

The lxcrunner package provides an utility to run scripts inside Linux
Containers. The main purpose of the utility is to

- setup a test environment with one or many LXC containers,
- run unit and functional tests inside the test environment and then
- tear down the LXC containers safely.

Configuration
-------------

All the aspects of the lxcrunner utility can be configured with a config
file. The default location of the file is `/etc/lxcrunner/config.ini`, but
it can be overriden with the `--config` option.

The config file consists of two major parts:

  1. description of containers to set up and
  2. logging configuration.

For the latter part see the documentation of the standard python logging
library: http://docs.python.org/library/logging.html.

The `DEFAULT` section of the config file should contain the following options:

vm_dir
  directory where LXC containers reside;

tpl_dir
  path to templates used to modify configuarion files of LXC  containers;

vm_setup
  (optional) name of a setup. This option can be overriden with the command
  line option `--setup` of the lxcrunner utility. The setup name is used to
  refer a section in the config file with settings specific to the environment
  setup.

Any environment setup sections must contain the option `vmguests` with a
comma-separated list of guest (LXC containers) names.

Additionally the section may contain arbitrary number of context variables used
in template files. Values of the options with names like `ctx_<variable_name>`
are transformed to templates variables with `<variable_name>` as their name.

An example of the config file::

    [DEFAULT]
    vm_dir: /var/lib/lxc
    tpl_dir: /etc/lxcrunner/templates
    vm_setup: derek_setup

    ; VM setup
    [derek_setup]
    vmguests: riaktest1,riaktest2,unittesthost
    ; set template variables netmask and gateway common for all guests
    ctx_netmask: 255.255.255.0
    ctx_gateway: 192.168.132.1

    [vmguest_riaktest1]
    ; use the riaknode template ([tpl_riaknode]) for the riaktest1 guest
    tpl_type: riaknode
    ctx_ip_address: 192.168.132.31

    [vmguest_riaktest2]
    tpl_type: riaknode
    ctx_ip_address: 192.168.132.32

    [vmguest_unittesthost]
    tpl_type: unittesthost
    ctx_ip_address: 192.168.132.40
    ctx_riak_hosts: 192.168.132.31,192.168.132.32
    ; run the command target_cmd as rozhkov
    target_user: rozhkov
    target_cmd: ssh -o StrictHostKeyChecking=no derek@%(ctx_ip_address)s run_tests.sh

    [tpl_riaknode]
    ; rootstrap used to deploy riaknode guests
    tarball: /home/rozhkov/backups/lxcs/riaknode-template.tgz
    tpls: hosts,hostname,interfaces,checkroot,riak_app_config,riak_vm_args,riak_initd
    ; templates used to modify files inside guests
    hosts: etc/hosts
    hostname: etc/hostname
    interfaces: etc/network/interfaces
    checkroot: etc/init.d/checkroot.sh
    riak_app_config: etc/riak/app.config
    riak_vm_args: etc/riak/vm.args
    riak_initd: etc/init.d/riak

    [tpl_unittesthost]
    tarball: /home/rozhkov/backups/lxcs/testhost-template.tgz
    tpls: hosts,hostname,interfaces,checkroot,haproxy_cfg,run_tests
    ; templates used to modify files inside guests
    hosts: etc/hosts
    hostname: etc/hostname
    interfaces: etc/network/interfaces
    checkroot: etc/init.d/checkroot.sh
    haproxy_cfg: etc/haproxy/haproxy.cfg
    run_tests: home/derek/bin/run_tests.sh

Usage
-----

Simply run::

    # lxcrunner
