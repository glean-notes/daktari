import logging
import re
from typing import Optional

from daktari.file_utils import dir_exists
from semver import VersionInfo

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stdout
from daktari.os import OS
from daktari.version_utils import try_parse_semver


class DockerInstalled(Check):
    name = "docker.installed"

    suggestions = {
        OS.GENERIC: "Install docker: https://docs.docker.com/get-docker/",
        OS.OS_X: "Install docker: https://docs.docker.com/docker-for-mac/install/",
    }

    def __init__(self, required_version: Optional[str] = None):
        self.required_version = required_version

    def check(self) -> CheckResult:
        installed_version = get_docker_version()
        return self.validate_semver_expression("Docker", installed_version, self.required_version)


major_version_pattern = re.compile("Docker version ([0-9.]+)")


def get_docker_version() -> Optional[VersionInfo]:
    raw_version = get_stdout("docker --version")
    if raw_version:
        match = major_version_pattern.search(raw_version)
        if match:
            version_string = match.group(1)
            version = try_parse_semver(version_string)
            logging.debug(f"Docker version - raw: {version_string}, parsed: {version}")
            return version
    return None


class DockerComposeInstalled(Check):
    name = "docker-compose.installed"

    suggestions = {OS.GENERIC: "Install docker-compose: https://docs.docker.com/compose/install/"}

    def check(self) -> CheckResult:
        return self.verify_install("docker-compose")


def get_orbstack_version() -> Optional[VersionInfo]:
    raw_output = get_stdout("orb version")
    if raw_output:
        match = re.match("Version: ([0-9.]+) ", raw_output)
        if match:
            version = try_parse_semver(match.group(1))
            logging.debug(f"Orbstack version: {version}")
            return version
    return None


class OrbStackInstalled(Check):
    name = "orbstack.installed"
    suggestions = {OS.GENERIC: "Install orbstack: https://docs.orbstack.dev/install and sign in."}

    def __init__(self, required_version: Optional[str] = None):
        self.required_version = required_version

    def check(self) -> CheckResult:
        installed_version = get_orbstack_version()
        return self.validate_semver_expression("Orbstack", installed_version, self.required_version)


class DockerDesktopNotInstalled(Check):
    name = "docker-desktop.not-installed"
    run_on = OS.OS_X
    suggestions = {
        OS.OS_X: "Uninstall Docker Desktop. Open Applications and delete Docker.app",
    }

    def check(self) -> CheckResult:
        return self.verify(not dir_exists("/Applications/Docker.app"), "Docker Desktop should not be installed")
