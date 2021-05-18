import logging
from typing import List, Set

from colors import yellow

from daktari.check import Check, CheckStatus
from daktari.check_sorter import sort_checks
from daktari.os import detect_os
from daktari.result_printer import print_check_result


def run_checks(checks: List[Check]) -> bool:
    return CheckRunner(checks).run()


class CheckRunner:
    def __init__(self, checks: List[Check]):
        self.checks = checks
        self.all_passed = True
        self.checks_passed: Set[str] = set()

    def run(self) -> bool:
        for check in sort_checks(self.checks):
            self.try_run_check(check)
        return self.all_passed

    def try_run_check(self, check: Check):
        if check.run_on and check.run_on != detect_os():
            return
        dependencies_met = all([dependency.name in self.checks_passed for dependency in check.depends_on])
        if dependencies_met:
            self.run_check(check)
        else:
            self.diagnose_missing_dependency(check)

    def run_check(self, check: Check):
        logging.info(f"Running check {check.name}")
        result = check.check()
        print_check_result(result)
        if result.status == CheckStatus.PASS:
            self.checks_passed.add(check.name)
        else:
            self.all_passed = False

    def diagnose_missing_dependency(self, check: Check):
        all_checks = {check.name for check in self.checks}
        check_dependencies = {dependency.name for dependency in check.depends_on}
        missing_checks = check_dependencies.difference(all_checks)
        if check_dependencies.difference(all_checks):
            print(f"⚠️  [{yellow(check.name)}] skipped due to missing dependent checks: {', '.join(missing_checks)}")
        else:
            print(f"⚠️  [{yellow(check.name)}] skipped due to previous failures")
