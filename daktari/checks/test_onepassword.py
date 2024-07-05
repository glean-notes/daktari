import unittest

from daktari.checks.onepassword import account_exists, contains_account


class TestOnePassword(unittest.TestCase):

    def test_account_exists(self):
        self.assertTrue(account_exists("checks/test_resources/op_config_with_account.json", "account-name"))
        self.assertFalse(
            account_exists("checks/test_resources/op_config_with_account.json", "non-existent-account-name")
        )

    def test_contains_account(self):
        account_url = "test.1password.com"

        correct_output = """
        URL                    EMAIL                        USER ID
        test.1password.com     test.email@domain.com        test-user-id
        """

        incorrect_output = """
        URL                    EMAIL                        USER ID
        my.1password.com       test.email@domain.com        test-user-id
        """

        empty_output = ""

        self.assertTrue(contains_account(correct_output, account_url))
        self.assertFalse(contains_account(incorrect_output, account_url))
        self.assertFalse(contains_account(empty_output, account_url))
