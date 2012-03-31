==========
LXC runner
==========

The lxcrunner package provides an utility to run scripts inside Linux
Containers. The main purpose of the utility is to

- setup a test environment with one or many LXC containers,
- run unit and functional tests inside the test environment and then
- tear down the LXC containers safely.

Configuration
=============

All the aspects of the lxcrunner utility can be configured with a config
file. The default location of the file is `/etc/lxcrunner/config.ini`, but
it can be overriden with the `--config` option.

The config file consists of two major parts:

  1. description of containers to set up and
  2. logging configuration.

For the latter part see the documentation of the standard python logging
library: http://docs.python.org/library/logging.html.

DEFAULT section
---------------

The `DEFAULT` section of the config file should contain the following options:

vm_dir
  directory where LXC containers reside;

tpl_dir
  path to templates used to modify configuarion files of LXC  containers;

vm_suite
  (optional) name of a suite. This option can be overriden with the command
  line option `--suite` of the lxcrunner utility. The suite name is used to
  refer a section in the config file with settings specific to the suite's
  environment setup.

Suite sections
--------------

Any suite sections must contain the option `vmguests` with a
comma-separated list of guest (LXC containers) names. These names are used
to refer config sections for guests: guest section names as prefixed with
the string `vmguest_`, i.e. `vmguest_<guest_name>`.

Additionally the section may contain arbitrary number of context variables used
in template files. Values of the options with names like `ctx_<variable_name>`
are transformed to templates variables with `<variable_name>` as their name.

Guest sections
--------------

A guest section must contain the field `tpl_type` whose value refers to
a template section `tpl_<tpl_type_value>`.

Guest sections may contain context variable in the same format as in
suite sections.

Optionally a guest section may contain the field `execute` with a path to
a script inside the guest container as its value. If this option is specified
then the guest is never get demonized, but the script is executed inside
the container instead.

Template sections
-----------------

A template section must contain the field `tarball`. The value of the field
is a path to a tarball to unpack in `vm_dir`.

Any other fields are names of templates that need to be rendered to
specified paths inside a container. lxcrunner looks for templates in
the folder `tpl_dir`. For example the field `hosts` inside a template
section refers to the template file `<tpl_dir>/hosts.tpl`. Values of the
fields are paths relative to container's root. Optionally the value
may contain a permission descriptor for the file::

    hosts: etc/hosts 0644


Example
-------

An example of the config file::

    [DEFAULT]
    vm_dir: /var/lib/lxc
    tpl_dir: /etc/lxcrunner/templates
    vm_suite: derek_setup

    ; VM suite
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
    execute: /bin/run_tests.sh

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
    run_tests: run_tests.sh 0744

Usage
=====

In case the default suite is specified in the default config file then you can
simply run::

    # lxcrunner

In oder to run an alternative non-default suite then use the option `--suite`::

    # lxcrunner --suite mysuite

To see the full list of options run::

    $ lxcrunner --help
    Usage: lxcrunner [options]

    Options:
      -h, --help            show this help message and exit
      -c CONFIG, --config=CONFIG
                            path to config file
      -s SUITE, --suite=SUITE
                            name of suite in config file
      -e ENDSTAGE, --end-stage=ENDSTAGE
                            name of final stage when lxcrunner must stop. The
                            stages are 'prepare', 'startsuite', 'run', 'cleanup'
      -u, --unique          add unique suffix to VM guests
