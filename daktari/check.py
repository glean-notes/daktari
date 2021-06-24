import abc
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Type, Union

from daktari.command_utils import can_run_command


class CheckStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    summary: str
    suggestions: Dict[str, str]


class Check:
    name: str
    depends_on: List[Type] = []
    suggestions: Dict[str, str] = {}
    run_on: Optional[str] = None

    def passed(self, message: str) -> CheckResult:
        return CheckResult(self.name, CheckStatus.PASS, message, self.suggestions)

    def failed(self, message: str) -> CheckResult:
        return CheckResult(self.name, CheckStatus.FAIL, message, self.suggestions)

    def verify(self, passed: bool, dualMessage: str) -> CheckResult:
        pattern = re.compile(" <not/> ")
        if passed:
            return self.passed(pattern.sub(" ", dualMessage))
        else:
            return self.failed(pattern.sub(" not ", dualMessage))

    def validate_required_version(
        self, application: str, installed_version: Union[float, str, None], required_version: Union[float, str]
    ) -> CheckResult:
        if installed_version is None:
            return self.failed(f"{application} is not installed")

        if required_version == "":
            return self.passed(f"{application} is installed")

        return self.verify(
            installed_version == required_version,
            f"{application} version is <not/> ={required_version} ({installed_version})",
        )

    def validate_minimum_version(
        self, application: str, installed_version: Optional[float], minimum_version: Optional[float]
    ) -> CheckResult:
        if installed_version is None:
            return self.failed(f"{application} is not installed")

        if minimum_version is None:
            return self.passed(f"{application} is installed")

        return self.verify(
            installed_version >= minimum_version,
            f"{application} version is <not/> >={minimum_version} ({installed_version})",
        )

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
