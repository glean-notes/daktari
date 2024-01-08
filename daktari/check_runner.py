import logging
from typing import List, Set

from daktari.check import Check, CheckStatus, CheckResult
from daktari.check_sorter import sort_checks
from daktari.os import detect_os
from daktari.result_printer import print_check_result


def run_checks(checks: List[Check], quiet_mode: bool, fail_fast: bool) -> bool:
    return CheckRunner(checks, quiet_mode, fail_fast).run()


class CheckRunner:
    def __init__(self, checks: List[Check], quiet_mode: bool, fail_fast: bool):
        self.checks = [check for check in checks if check.should_run(detect_os())]
        self.all_passed = True
        self.checks_passed: Set[str] = set()
        self.quiet_mode = quiet_mode
        self.fail_fast = fail_fast

    def run(self) -> bool:
        for idx, check in enumerate(sort_checks(self.checks)):
            self.try_run_check(idx, check)
            if self.early_exit():
                break

        return self.all_passed

    def early_exit(self) -> bool:
        return self.fail_fast and not self.all_passed

    def try_run_check(self, idx: int, check: Check):
        dependencies_met = all([dependency.name in self.checks_passed for dependency in check.depends_on])
        result = self.run_check(check) if dependencies_met else self.diagnose_missing_dependency(check)
        print_check_result(result, self.early_exit(), self.quiet_mode, idx, len(self.checks))

    def run_check(self, check: Check) -> CheckResult:
        logging.info(f"Running check {check.name}")
        result = self.run_check_in_try(check)
        if result.status in (CheckStatus.PASS, CheckStatus.PASS_WITH_WARNING):
            self.checks_passed.add(check.name)
        else:
            self.all_passed = False

        return result

    def run_check_in_try(self, check: Check) -> CheckResult:
        try:
            return check.check()
        except Exception as err:
            logging.debug(f"Exception running check {check.name}", exc_info=True)
            return CheckResult(check.name, CheckStatus.ERROR, f"Check failed with unhandled {type(err).__name__}", {})

    def diagnose_missing_dependency(self, check: Check) -> CheckResult:
        all_checks = {check.name for check in self.checks}
        check_dependencies = {dependency.name for dependency in check.depends_on}
        missing_checks = check_dependencies.difference(all_checks)

        summary = (
            f"skipped due to missing dependent checks: {', '.join(missing_checks)}"
            if missing_checks
            else "skipped due to previous failures"
        )
        return CheckResult(check.name, CheckStatus.PASS_WITH_WARNING, summary, {})
