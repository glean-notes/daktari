import unittest

from daktari.checks.onepassword import account_exists


class TestOnePassword(unittest.TestCase):

    def test_account_exists(self):
        self.assertTrue(account_exists("checks/test_resources/op_config_with_account.json", "account-name"))
        self.assertFalse(
            account_exists("checks/test_resources/op_config_with_account.json", "non-existent-account-name")
        )
