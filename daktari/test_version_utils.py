import unittest
from unittest import mock

from daktari.version_utils import get_simple_cli_version


class TestVersionUtils(unittest.TestCase):
    @mock.patch("daktari.version_utils.get_stdout", return_value="1.2.3")
    def test_get_simple_cli_version(self, _):
        self.assertEqual(get_simple_cli_version("foo"), "1.2.3")

    @mock.patch("daktari.version_utils.get_stdout", return_value="pre-commit 4.5.1")
    def test_get_simple_cli_version_with_binary_name(self, _):
        self.assertEqual(get_simple_cli_version("foo"), "4.5.1")

    @mock.patch("daktari.version_utils.get_stdout", return_value="pre-commit has an update available")
    def test_get_simple_cli_version_no_match(self, _):
        self.assertEqual(get_simple_cli_version("foo"), None)

    @mock.patch("daktari.version_utils.get_stdout", return_value="Cloud SQL Auth proxy: 1.27.0+darwin.arm64")
    def test_with_version_suffix(self, _):
        self.assertEqual(get_simple_cli_version("foo"), "1.27.0")

    @mock.patch("daktari.version_utils.get_stdout", return_value="pre-commit 100")
    def test_get_simple_cli_version_invalid_version(self, _):
        self.assertEqual(get_simple_cli_version("foo"), None)
