class ConanInstalled(Check):
    name = "conan.installed"

    def __init__(self, required_version: Optional[str] = None, recommended_version: Optional[str] = None):
        self.required_version = required_version
        self.recommended_version = recommended_version
        self.suggestions = {
            OS.GENERIC: "Install conan: <cmd>pip install conan</cmd>"
        }

    def check(self) -> CheckResult:
        return self.validate_semver_expression(
            "conan", installed_version, self.required_version, self.recommended_version
        )


class ConanProfileDetected(Check):
    name = "conan.profileDetected"

    def __init__(self, expected_string: str):
        self.suggestions = {OS.GENERIC: "<cmd>conan profile detect</cmd>"}

    def check(self) -> CheckResult:
        default_profile_detected = "default" in get_stdout("conan profile list")
        return self.verify(default_profile_detected, "Default conan profile <not /> detected")
