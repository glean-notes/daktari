import abc
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Type


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
