import unittest

from semver import VersionInfo

from daktari.check import CheckResult, CheckStatus
from daktari.test_check_factory import DummyCheck

INSTALLED_VERSION = VersionInfo(10, 3, 1)


class TestConfig(unittest.TestCase):
    def test_no_version(self):
        result = DummyCheck().validate_semver_expression("Application", None)
        self._verify_result(result, CheckStatus.FAIL, "Application is not installed")

    def test_invalid_required_version(self):
        result = DummyCheck().validate_semver_expression("Application", INSTALLED_VERSION, required_version=">>zz")
        self._verify_result(result, CheckStatus.FAIL, "Invalid version specification: >zz is not valid SemVer string")

    def test_invalid_recommended_version(self):
        result = DummyCheck().validate_semver_expression("Application", INSTALLED_VERSION, recommended_version=">>zz")
        self._verify_result(result, CheckStatus.FAIL, "Invalid version specification: >zz is not valid SemVer string")

    def test_doesnt_meet_required_version(self):
        result = DummyCheck().validate_semver_expression("Application", INSTALLED_VERSION, required_version=">=10.4.0")
        self._verify_result(result, CheckStatus.FAIL, "Application version is not >=10.4.0 (10.3.1)")

    def test_doesnt_meet_recommended_version(self):
        result = DummyCheck().validate_semver_expression(
            "Application", INSTALLED_VERSION, recommended_version=">=10.4.0"
        )
        self._verify_result(
            result, CheckStatus.PASS_WITH_WARNING, "Application version is 10.3.1, >=10.4.0 recommended"
        )

    def test_meets_all_versions(self):
        result = DummyCheck().validate_semver_expression(
            "Application", INSTALLED_VERSION, required_version=">=10.0.0", recommended_version="<11.0.0"
        )
        self._verify_result(result, CheckStatus.PASS, "Application version is 10.3.1")

    def _verify_result(self, result: CheckResult, expected_status: CheckStatus, expected_message: str):
        self.assertEqual(result, CheckResult("check.name", expected_status, expected_message, {}))
