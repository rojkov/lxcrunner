auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
  address {{ip_address}}
  netmask {{netmask}}
  gateway {{gateway}}
