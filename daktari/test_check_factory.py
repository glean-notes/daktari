from daktari.check import Check, CheckResult


class DummyCheck(Check):
    def __init__(self, name: str = "check.name", depends_on=None, succeed: bool = True):
        if depends_on is None:
            depends_on = []
        self.name = name
        self.depends_on = depends_on
        self.was_run = False
        self.succeed = succeed

    def check(self) -> CheckResult:
        self.was_run = True
        return self.verify(self.succeed, "dummy check")


class ExplodingCheck(Check):
    name = "exploding.check"

    def check(self) -> CheckResult:
        raise Exception("boom")


class DummyCheck2(Check):
    def __init__(self, name: str = "check.name", depends_on=None):
        if depends_on is None:
            depends_on = []
        self.name = name
        self.depends_on = depends_on

    def check(self) -> CheckResult:
        return self.passed("no check")
