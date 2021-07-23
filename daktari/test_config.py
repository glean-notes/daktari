import sys
import unittest
from io import StringIO
from pathlib import Path

from colors import red, yellow
from packaging import version
from packaging.version import Version

from daktari import __version__
from daktari.config import check_version_compatibility, parse_raw_config

config_path = Path("./.daktari.config")
current_version: Version = Version(__version__)
next_version = version.parse(f"{current_version.major}.{current_version.minor}.{current_version.micro + 1}")


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.capturedOutput = StringIO()
        sys.stdout = self.capturedOutput

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_empty_version(self):
        result = check_version_compatibility(config_path, "")
        self.assertEqual(result, True)
        self.verify_warning(
            "⚠️  No minimum version found in .daktari.config. Specifying daktari_version is "
            "recommended to ensure team members have compatible versions installed."
        )

    def test_invalid_version(self):
        result = check_version_compatibility(config_path, 'daktari_version="....9"')
        self.assertEqual(result, False)
        self.verify_error("❌  Invalid daktari_version in .daktari.config: ....9")

    def test_correct_version(self):
        result = check_version_compatibility(config_path, f'daktari_version="{current_version}"')
        self.assertEqual(result, True)
        self.verify_no_logging()

    def test_too_old_version(self):
        result = check_version_compatibility(config_path, f'daktari_version="{next_version}"')
        self.assertEqual(result, False)
        self.verify_error(
            f"❌  Installed version of daktari [{current_version}] is "
            f"too old for this project (needs at least {next_version}). "
        )

    def test_invalid_version_returns_none(self):
        result = parse_raw_config(config_path, f'daktari_version="{next_version}"')
        self.assertEqual(result, None)

    def test_invalid_config_prints_error(self):
        result = parse_raw_config(config_path, "checks = [NonExistentCheck()]")
        self.assertEqual(result, None)
        self.verify_error("❌  Failed to parse .daktari.config - config is not valid.")

    def verify_no_logging(self):
        self.assertEqual(self.capturedOutput.getvalue(), "")

    def verify_warning(self, warning_text: str):
        self.assertIn(yellow(warning_text), self.capturedOutput.getvalue())

    def verify_error(self, warning_text: str):
        self.assertIn(red(warning_text), self.capturedOutput.getvalue())


if __name__ == "__main__":
    unittest.main()
