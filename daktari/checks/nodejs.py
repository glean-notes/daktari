import logging
from typing import Optional
from semver import VersionInfo

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stdout
from daktari.os import OS
from daktari.semver_utils import try_parse_semver


def get_nodejs_version() -> Optional[VersionInfo]:
    version_output = get_stdout("node --version")
    version_output = None if version_output is None else version_output.removeprefix("v")
    return try_parse_semver(version_output)


class NodeJsVersion(Check):
    name = "nodejs.version"

    def __init__(self, required_version: str, recommended_version: Optional[str] = None):
        self.required_version = required_version
        self.recommended_version = recommended_version

    suggestions = {
        OS.GENERIC: "Install node.js",
    }

    def check(self) -> CheckResult:
        nodejs_version = get_nodejs_version()
        logging.info(f"node.js version: {nodejs_version}")
        return self.validate_semver_expression(
            "node.js", nodejs_version, self.required_version, self.recommended_version
        )
