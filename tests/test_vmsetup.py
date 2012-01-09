import unittest

from ConfigParser import ConfigParser, NoOptionError

from virtlib.vmsetup import VMGuest

class TestVMGuest(unittest.TestCase):
    """Tests for VMGuest."""

    def setUp(self):
        config = ConfigParser()
        config.add_section("vmguest_test")
        config.set("vmguest_test", "tpl_type", "testhost")
        config.set("vmguest_test", "tpl_dir", "/tmp")
        config.add_section("tpl_testhost")
        config.set("tpl_testhost", "vm_dir", "/tmp")
        config.set("tpl_testhost", "tarball", "tests/test_vmsetup.py")
        self.config = config

    def test_init(self):
        # no templates defined
        VMGuest("test", self.config)
        VMGuest("test", self.config, {})
        # some templates defined
        self.config.set("tpl_testhost", "tpls", "tpl1,tpl2")
        self.config.set("tpl_testhost", "tpl1", "fake_path1")
        self.assertRaises(NoOptionError, VMGuest, "test", self.config)
        self.config.set("tpl_testhost", "tpl2", "fake_path2")
        VMGuest("test", self.config)

if __name__ == "__main__":
    unittest.main()
