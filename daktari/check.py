import abc
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Type

from semver import VersionInfo

from daktari.command_utils import can_run_command


class CheckStatus(Enum):
    PASS = "PASS"
    PASS_WITH_WARNING = "PASS_WITH_WARNING"
    FAIL = "FAIL"
    ERROR = "ERROR"


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    summary: str
    suggestions: Dict[str, str]


class Check:
    name: str
    depends_on: List[Type["Check"]] = []
    suggestions: Dict[str, str] = {}
    run_on: Optional[str] = None

    def passed(self, message: str) -> CheckResult:
        return CheckResult(self.name, CheckStatus.PASS, message, self.suggestions)

    def failed(self, message: str) -> CheckResult:
        return CheckResult(self.name, CheckStatus.FAIL, message, self.suggestions)

    def passed_with_warning(self, message: str) -> CheckResult:
        return CheckResult(self.name, CheckStatus.PASS_WITH_WARNING, message, self.suggestions)

    def verify(self, passed: bool, dual_message: str) -> CheckResult:
        pattern = re.compile(" <not/> ")
        if passed:
            return self.passed(pattern.sub(" ", dual_message))
        else:
            return self.failed(pattern.sub(" not ", dual_message))

    def validate_semver_expression(
        self,
        application: str,
        installed_version: Optional[VersionInfo],
        required_version: Optional[str] = None,
        recommended_version: Optional[str] = None,
    ) -> CheckResult:
        if installed_version is None:
            return self.failed(f"{application} is not installed")

        try:
            matches_required = required_version is None or installed_version.match(required_version)
            matches_recommended = recommended_version is None or installed_version.match(recommended_version)
        except ValueError as err:
            return self.failed(f"Invalid version specification: {err}")

        if not matches_required:
            return self.failed(f"{application} version is not {required_version} ({installed_version})")

        if not matches_recommended:
            return self.passed_with_warning(
                f"{application} version is {installed_version}, {recommended_version} recommended"
            )

        return self.passed(f"{application} version is {installed_version}")

    def verify_install(self, program: str, version_flag: str = "--version") -> CheckResult:
        return self.verify(can_run_command(f"{program} {version_flag}"), f"{program} is <not/> installed")

    @abc.abstractmethod
    def check(self) -> CheckResult:
        raise NotImplementedError("check must be implemented")

    def override_suggestions(self, suggestions: Dict[str, str]) -> "Check":
        self.suggestions = suggestions
        return self

    def suggest(self, os: str, text: str) -> "Check":
        return self.override_suggestions({os: text})

    def only_on(self, os: str) -> "Check":
        self.run_on = os
        return self

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name
