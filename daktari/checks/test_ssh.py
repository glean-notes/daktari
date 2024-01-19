import unittest

from daktari.checks.ssh import is_ssh_configured_to_use_macos_keychain


class TestSSH(unittest.TestCase):
    def test_ssh_configured_correctly(self):
        self.assertTrue(is_ssh_configured_to_use_macos_keychain("checks/test_resources/good_ssh_config"))

    def test_ssh_not_configured(self):
        self.assertFalse(is_ssh_configured_to_use_macos_keychain("checks/test_resources/bad_ssh_config"))

    def test_ssh_no_config_file(self):
        self.assertFalse(is_ssh_configured_to_use_macos_keychain("/some/file/path/that/does/not/exist"))

    def test_ssh_half_configured_file(self):
        self.assertFalse(is_ssh_configured_to_use_macos_keychain("checks/test_resources/half_configured_ssh_config"))

    def test_ssh_incorrectly_configured_file(self):
        self.assertFalse(
            is_ssh_configured_to_use_macos_keychain("checks/test_resources/incorrectly_configured_ssh_config")
        )
