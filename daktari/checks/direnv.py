import re

from daktari.command_utils import get_stdout

from daktari.os import OS
from daktari.check import Check, CheckResult
from daktari.version_utils import get_simple_cli_version
from typing import Optional


class DirenvInstalled(Check):
    name = "direnv.installed"

    def __init__(self, required_version: Optional[str] = None, recommended_version: Optional[str] = None):
        self.required_version = required_version
        self.recommended_version = recommended_version
        self.suggestions = {
            OS.OS_X: "<cmd>brew install direnv</cmd>",
            OS.GENERIC: "Install kubectl: https://direnv.net/#getting-started",
        }

    def check(self) -> CheckResult:
        installed_version = get_simple_cli_version("direnv")
        return self.validate_semver_expression(
            "direnv", installed_version, self.required_version, self.recommended_version
        )


class DirenvAllowed(Check):
    name = "direnv.allowed"

    def __init__(self, parent_file_name: str):
        self.file_name = parent_file_name
        self.suggestions = {
            OS.GENERIC: "<cmd>direnv allow .</cmd>"
        }

    def check(self) -> CheckResult:
        direnv_status = get_stdout("direnv status")
        query = f"Found RC path .*/{self.parent_file_name}/.envrc\n.*\n.*\nFound RC allowed true"
        return re.search(query, direnv_status) is not None

