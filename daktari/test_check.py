import unittest

from semver import VersionInfo

from daktari.check import CheckResult, CheckStatus
from daktari.os import OS
from daktari.test_check_factory import DummyCheck, DummyCheck2

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

    def test_with_dependencies_adds_dependency(self):
        check = DummyCheck(depends_on=None).with_dependencies(DummyCheck, DummyCheck2)
        self.assertEqual(check.depends_on, [DummyCheck, DummyCheck2])

    def test_with_dependencies_keeps_existing_dependencies(self):
        check = DummyCheck(depends_on=[DummyCheck]).with_dependencies(DummyCheck2)
        self.assertEqual(check.depends_on, [DummyCheck, DummyCheck2])

    def test_override_suggest(self):
        generic = DummyCheck().suggest("Do the thing")
        self.assertEqual(generic.suggestions, {OS.GENERIC: "Do the thing"})

        ubuntu = DummyCheck().suggest("Do the thing", OS.UBUNTU)
        self.assertEqual(ubuntu.suggestions, {OS.UBUNTU: "Do the thing"})

    def test_conditional_override(self):
        some_condition = True
        overridden = DummyCheck().suggest_if(some_condition, "Do the thing")
        self.assertEqual(overridden.suggestions, {OS.GENERIC: "Do the thing"})

        not_overridden = DummyCheck().suggest_if(not some_condition, "Do the thing")
        self.assertEqual(not_overridden.suggestions, {})

    def test_should_run(self):
        self.assertTrue(DummyCheck().should_run(OS.GENERIC))

        self.assertTrue(DummyCheck().only_on(OS.UBUNTU).should_run(OS.UBUNTU))
        self.assertFalse(DummyCheck().only_on(OS.UBUNTU).should_run(OS.OS_X))

        self.assertTrue(DummyCheck().skip_if(False).should_run(OS.GENERIC))
        self.assertFalse(DummyCheck().skip_if(True).should_run(OS.GENERIC))

    def test_warn_only(self):
        check = DummyCheck(succeed=False).warn_only()
        result = check.check()
        self._verify_result(result, CheckStatus.PASS_WITH_WARNING, "dummy check")

    def _verify_result(self, result: CheckResult, expected_status: CheckStatus, expected_message: str):
        self.assertEqual(result, CheckResult("check.name", expected_status, expected_message, {}))
