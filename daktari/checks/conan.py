from typing import Optional

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stdout
from daktari.os import OS


class ConanInstalled(Check):
    name = "conan.installed"

    def __init__(self, required_version: Optional[str] = None, recommended_version: Optional[str] = None):
        self.required_version = required_version
        self.recommended_version = recommended_version
        self.suggestions = {OS.GENERIC: "Install conan: <cmd>pip install conan</cmd>"}

    def check(self) -> CheckResult:
        return self.verify_install("conan")


class ConanProfileDetected(Check):
    name = "conan.profileDetected"

    def __init__(self, expected_string: str):
        self.suggestions = {OS.GENERIC: "<cmd>conan profile detect</cmd>"}
        self.expected_string = expected_string
        self.depends_on = [ConanInstalled]

    def check(self) -> CheckResult:
        output = get_stdout("conan profile list")
        expected_profile_detected = output is not None and self.expected_string in output
        return self.verify(expected_profile_detected, f"conan profile {self.expected_string} <not/> detected")
