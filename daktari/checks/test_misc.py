import unittest

from daktari.check import CheckStatus
from daktari.checks.misc import HostAliasesConfigured


class TestHostAliasesConfigured(unittest.TestCase):
    def test_checking_hosts_does_not_blow_up_on_success(self):
        result = HostAliasesConfigured({}).check()
        self.assertEqual(result.status, CheckStatus.PASS)

    def test_checking_hosts_does_not_blow_up_on_failure(self):
        result = HostAliasesConfigured({"host": "no.such.entry.surely"}).check()
        self.assertEqual(result.status, CheckStatus.FAIL)


if __name__ == "__main__":
    unittest.main()
