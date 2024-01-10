import re

from daktari.command_utils import get_stdout

from daktari.os import OS
from daktari.check import Check, CheckResult
from daktari.version_utils import get_simple_cli_version
from daktari.file_utils import file_contains_text
from typing import Optional
from os import getcwd


class DirenvInstalled(Check):
    name = "direnv.installed"

    def __init__(self, required_version: Optional[str] = None, recommended_version: Optional[str] = None):
        self.required_version = required_version
        self.recommended_version = recommended_version
        self.suggestions = {
            OS.GENERIC: "Install direnv: https://direnv.net/#getting-started",
            OS.OS_X: "Install direnv using brew: <cmd>brew install direnv</cmd>",
            OS.UBUNTU: "Install direnv using apt-get: <cmd>sudo apt-get install direnv</cmd>",
        }

    def check(self) -> CheckResult:
        installed_version = get_simple_cli_version("direnv")
        return self.validate_semver_expression(
            "direnv", installed_version, self.required_version, self.recommended_version
        )


class EnvrcContainsText(Check):
    name = "direnv.envrc.containsText"

    def __init__(self, expected_string: str, suggestion: str):
        self.file_path = f"{getcwd()}/.envrc"
        self.expected_string = expected_string
        self.pass_fail_message = f"{self.file_path} does <not/> contain '{expected_string}'"
        self.suggestions = {OS.GENERIC: suggestion}

    def check(self) -> CheckResult:
        return self.verify(file_contains_text(self.file_path, self.expected_string), self.pass_fail_message)


class DirenvAllowed(Check):
    name = "direnv.allowed"
    depends_on = [DirenvInstalled, EnvrcContainsText]

    def __init__(self):
        self.suggestions = {OS.GENERIC: "<cmd>direnv allow .</cmd>"}

    def check(self) -> CheckResult:
        direnv_status = get_stdout("direnv status")
        if direnv_status is None:
            return self.failed("direnv status returned no output")
        cwd = getcwd()
        query = f"Found RC path {cwd}/.envrc(\n.*)*Found RC allowed (true|0)"
        direnv_allowed = re.search(query, direnv_status) is not None
        return self.verify(direnv_allowed, f"{cwd} is <not/> allowed to use direnv")
