import unittest

from ConfigParser import ConfigParser

from virtlib.vmsetup import VMGuest

class TestVMGuest(unittest.TestCase):
    """Tests for VMGuest."""

    def setUp(self):
        config = ConfigParser()
        config.add_section("vmguest_test")
        config.set("vmguest_test", "tpl_type", "testhost")
        config.add_section("tpl_testhost")
        config.set("tpl_testhost", "vm_dir", "/tmp")
        config.set("tpl_testhost", "tarball", "/tmp/1.tgz")
        self.config = config

    def test_init(self):
        vmguest = VMGuest("test", self.config)

if __name__ == "__main__":
    unittest.main()
