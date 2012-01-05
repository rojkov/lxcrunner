lxc.network.type = veth
lxc.network.flags = up
lxc.network.link = br0
lxc.tty = 0
lxc.pts = 1024
lxc.rootfs = {{rootfs}}
lxc.cgroup.devices.deny = a
# /dev/null and zero
lxc.cgroup.devices.allow = c 1:3 rwm
lxc.cgroup.devices.allow = c 1:5 rwm
# consoles
lxc.cgroup.devices.allow = c 5:1 rwm
lxc.cgroup.devices.allow = c 5:0 rwm
lxc.cgroup.devices.allow = c 4:0 rwm
lxc.cgroup.devices.allow = c 4:1 rwm
# /dev/{,u}random
lxc.cgroup.devices.allow = c 1:9 rwm
lxc.cgroup.devices.allow = c 1:8 rwm
lxc.cgroup.devices.allow = c 136:* rwm
lxc.cgroup.devices.allow = c 5:2 rwm
# rtc
lxc.cgroup.devices.allow = c 254:0 rwm

# mounts point
lxc.mount.entry=proc {{rootfs}}/proc proc nodev,noexec,nosuid 0 0
lxc.mount.entry=devpts {{rootfs}}/dev/pts devpts defaults 0 0
lxc.mount.entry=sysfs {{rootfs}}/sys sysfs defaults  0 0
