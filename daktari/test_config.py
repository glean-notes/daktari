import os
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from colors import red, yellow
from packaging import version
from packaging.version import Version

from daktari import __version__
from daktari.checks.intellij_idea import IntelliJIdeaInstalled, IntelliJProjectImported
from daktari.checks.misc import EnvVarSet
from daktari.config import check_version_compatibility, parse_raw_config, LOCAL_CONFIG_PATH, Config, apply_local_config
from daktari.resource_utils import get_resource

config_path = Path("./.daktari.config")
current_version: Version = Version(__version__)
next_version = version.parse(f"{current_version.major}.{current_version.minor}.{current_version.micro + 1}")

TEST_CHECKS = [
    EnvVarSet(variable_name="SOME_ENV_VAR"),
    IntelliJIdeaInstalled(),
    IntelliJProjectImported(),
]


class TestConfig(unittest.TestCase):
    def tearDown(self):
        if os.path.exists(LOCAL_CONFIG_PATH):
            os.remove(LOCAL_CONFIG_PATH)

    def test_empty_version(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            result = check_version_compatibility(config_path, "")
            self.assertEqual(result, True)
            self.verify_warning(
                fake_out,
                "⚠️  No minimum version found in .daktari.config. Specifying daktari_version is "
                "recommended to ensure team members have compatible versions installed.",
            )

    def test_invalid_version(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            result = check_version_compatibility(config_path, 'daktari_version="....9"')
            self.assertEqual(result, False)
            self.verify_error(fake_out, "❌  Invalid daktari_version in .daktari.config: ....9")

    def test_correct_version(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            result = check_version_compatibility(config_path, f'daktari_version="{current_version}"')
            self.assertEqual(result, True)
            self.verify_no_logging(fake_out)

    def test_too_old_version(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            result = check_version_compatibility(config_path, f'daktari_version="{next_version}"')
            self.assertEqual(result, False)
            self.verify_error(
                fake_out,
                f"❌  Installed version of daktari [{current_version}] is "
                f"too old for this project (needs at least {next_version}). ",
            )

    def test_invalid_version_returns_none(self):
        result = parse_raw_config(config_path, f'daktari_version="{next_version}"')
        self.assertEqual(result, None)

    def test_invalid_config_prints_error(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            result = parse_raw_config(config_path, "checks = [NonExistentCheck()]")
            self.assertEqual(result, None)
            self.verify_error(fake_out, "❌  Failed to parse .daktari.config - config is not valid.")

    def test_local_config_does_not_exist(self):
        config = Config(None, None, TEST_CHECKS)
        updated_config = apply_local_config(config)
        self.assertEqual(Config(None, None, TEST_CHECKS, True), updated_config)

        expected_contents = get_resource("daktari-local-template.yml")
        with open(LOCAL_CONFIG_PATH, "r", encoding="utf-8") as local_config_file:
            actual_contents = local_config_file.read()
            self.assertEqual(expected_contents, actual_contents)

    def test_local_config_invalid_yml(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            self.write_to_local_config("{{ invalid yaml }")

            config = Config(None, None, TEST_CHECKS)
            updated_config = apply_local_config(config)
            self.assertEqual(None, updated_config)
            self.verify_error(
                fake_out, f"❌  Failed to parse {LOCAL_CONFIG_PATH} - config is not valid YAML. Error follows."
            )

    def test_local_config_missing_ignored_checks(self):
        self.write_to_local_config("someOtherSetting: []")

        config = Config(None, None, TEST_CHECKS)
        updated_config = apply_local_config(config)
        self.assertEqual(config, updated_config)

    def test_local_config_empty_ignored_checks(self):
        self.write_to_local_config("ignoredChecks: []")

        config = Config(None, None, TEST_CHECKS)
        updated_config = apply_local_config(config)
        self.assertEqual(config, updated_config)

    def test_local_config_template(self):
        template_text = get_resource("daktari-local-template.yml")
        self.write_to_local_config(template_text)

        config = Config(None, None, TEST_CHECKS)
        updated_config = apply_local_config(config)
        self.assertEqual(config, updated_config)

    def test_local_config_ignored_check_dynamic_name(self):
        self.write_to_local_config("ignoredChecks: ['env.variableSet.SOME_ENV_VAR']")

        config = Config(None, None, TEST_CHECKS)
        updated_config = apply_local_config(config)
        self.assertEqual([IntelliJIdeaInstalled(), IntelliJProjectImported()], updated_config.checks)

    def test_local_config_ignored_check_with_dependants(self):
        self.write_to_local_config("ignoredChecks: ['intellij.installed']")

        config = Config(None, None, TEST_CHECKS)
        updated_config = apply_local_config(config)
        self.assertEqual([EnvVarSet(variable_name="SOME_ENV_VAR")], updated_config.checks)

    def write_to_local_config(self, contents: str):
        with open(LOCAL_CONFIG_PATH, "a") as log_file:
            log_file.write(contents)

    def verify_no_logging(self, fake_out: StringIO):
        self.assertEqual(fake_out.getvalue(), "")

    def verify_warning(self, fake_out: StringIO, warning_text: str):
        self.assertIn(yellow(warning_text), fake_out.getvalue())

    def verify_error(self, fake_out: StringIO, warning_text: str):
        self.assertIn(red(warning_text), fake_out.getvalue())


if __name__ == "__main__":
    unittest.main()
