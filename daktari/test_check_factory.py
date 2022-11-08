from daktari.check import Check, CheckResult


class DummyCheck(Check):
    def __init__(self, name: str = "check.name", depends_on=None):
        if depends_on is None:
            depends_on = []
        self.name = name
        self.depends_on = depends_on

    def check(self) -> CheckResult:
        return self.passed("no check")
