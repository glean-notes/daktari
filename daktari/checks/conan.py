from typing import Optional

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stdout
from daktari.os import OS
from daktari.version_utils import get_simple_cli_version


class ConanInstalled(Check):
    name = "conan.installed"

    def __init__(self, required_version: Optional[str] = None, recommended_version: Optional[str] = None):
        self.required_version = required_version
        self.recommended_version = recommended_version
        self.suggestions = {
            OS.GENERIC: "Install conan: <cmd>pip install conan</cmd>"
        }

    def check(self) -> CheckResult:
        installed_version = get_simple_cli_version("direnv")
        return self.validate_semver_expression(
            "conan", installed_version, self.required_version, self.recommended_version
        )


class ConanProfileDetected(Check):
    name = "conan.profileDetected"

    def __init__(self, expected_string: str):
        self.suggestions = {OS.GENERIC: "<cmd>conan profile detect</cmd>"}
        self.expected_string = expected_string

    def check(self) -> CheckResult:
        expected_profile_detected = self.expected_string in get_stdout("conan profile list")
        return self.verify(expected_profile_detected, f"conan profile ${self.expected_string} <not /> detected")
