import unittest

from semver import VersionInfo

from daktari.check import CheckStatus
from daktari.checks.intellij_idea import IntelliJProjectSdkJavaVersion, get_intellij_version_from_product_info


class TestIntellijIdea(unittest.TestCase):
    def test_parse_product_info(self):
        product_info_path = "checks/test_resources/intellij-product-info.json"
        result = get_intellij_version_from_product_info(product_info_path)
        self.assertEqual(result, VersionInfo(2023, 3, 5))

    def test_project_sdk_unset(self):
        check = IntelliJProjectSdkJavaVersion(17)
        check.file_path = "checks/test_resources/intellij_misc_no_sdk.xml"
        result = check.check()
        self.assertEqual(result.status, CheckStatus.FAIL)
        self.assertEqual(result.summary, "IntelliJ Project SDK is not a Java JDK")

    def test_project_sdk_python(self):
        check = IntelliJProjectSdkJavaVersion(17)
        check.file_path = "checks/test_resources/intellij_misc_python_sdk.xml"
        result = check.check()
        self.assertEqual(result.status, CheckStatus.FAIL)
        self.assertEqual(result.summary, "IntelliJ Project SDK is not a Java JDK: Python SDK")

    def test_project_sdk_wrong_java_version(self):
        check = IntelliJProjectSdkJavaVersion(21)
        check.file_path = "checks/test_resources/intellij_misc_java_17.xml"
        result = check.check()
        self.assertEqual(result.status, CheckStatus.FAIL)
        self.assertEqual(result.summary, "IntelliJ Project SDK is not set to Java 21: JDK_17")

    def test_project_sdk_correct_java_version(self):
        check = IntelliJProjectSdkJavaVersion(17)
        check.file_path = "checks/test_resources/intellij_misc_java_17.xml"
        result = check.check()
        self.assertEqual(result.status, CheckStatus.PASS)
        self.assertEqual(result.summary, "IntelliJ Project SDK is set to Java 17: JDK_17")
