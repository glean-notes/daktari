import logging
import re
from typing import Optional
from semver import VersionInfo

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stderr
from daktari.os import OS

java_version_pattern = re.compile('^.*version "(.*?)".*$', re.MULTILINE)
one_dot_pattern = re.compile("1\\.([0-9]+)")
other_pattern = re.compile("([0-9]+)")


def get_java_version() -> Optional[VersionInfo]:
    version_output = get_stderr("java -version")
    return parse_java_version_output(version_output)


def parse_java_version_output(version_output: str) -> Optional[VersionInfo]:
    if version_output:
        match = java_version_pattern.search(version_output)
        if match:
            version_string = match.group(1)
            logging.debug(f"Java version string: {version_string}")
            return parse_java_version_string(version_string)
    return None


def parse_java_version_string(version_string: str) -> Optional[VersionInfo]:
    try:
        return VersionInfo.parse(version_string)
    except ValueError:
        return parse_legacy_java_number(version_string)


def parse_legacy_java_number(version_string: str) -> Optional[int]:
    one_dot_match = one_dot_pattern.search(version_string)
    if one_dot_match:
        return VersionInfo(int(one_dot_match.group(1)))
    return None


class JavaVersion(Check):
    name = "java.version"

    def __init__(self, required_version: str):
        self.required_version = required_version

    suggestions = {
        OS.GENERIC: "Install Java",
    }

    def check(self) -> CheckResult:
        java_version = get_java_version()
        logging.info(f"Java version: {java_version}")
        return self.validate_semver_expression("Java", java_version, self.required_version)
