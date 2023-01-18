import re

from daktari.command_utils import get_stdout

from daktari.os import OS
from daktari.check import Check, CheckResult
from daktari.version_utils import get_simple_cli_version
from typing import Optional
from os import getcwd


class DirenvInstalled(Check):
    name = "direnv.installed"

    def __init__(self, required_version: Optional[str] = None, recommended_version: Optional[str] = None):
        self.required_version = required_version
        self.recommended_version = recommended_version
        self.suggestions = {
            OS.GENERIC: "Install direnv: https://direnv.net/#getting-started",
        }

    def check(self) -> CheckResult:
        installed_version = get_simple_cli_version("direnv")
        return self.validate_semver_expression(
            "direnv", installed_version, self.required_version, self.recommended_version
        )


class DirenvAllowed(Check):
    name = "direnv.allowed"
    depends_on = [DirenvInstalled]

    def __init__(self):
        self.suggestions = {OS.GENERIC: "<cmd>direnv allow .</cmd>"}

    def check(self) -> CheckResult:
        direnv_status = get_stdout("direnv status")
        if direnv_status is None:
            return self.failed("direnv status returned no output")
        cwd = getcwd()
        query = f"Found RC path {cwd}/.envrc\n.*\n.*\nFound RC allowed true"
        direnv_allowed = re.search(query, direnv_status) is not None
        return self.verify(direnv_allowed, f"{cwd} is <not/> allowed to use direnv")
