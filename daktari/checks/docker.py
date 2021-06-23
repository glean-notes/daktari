import logging
import re
from typing import Optional

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stdout
from daktari.os import OS


class DockerInstalled(Check):
    name = "docker.installed"

    suggestions = {
        OS.GENERIC: "Install docker: https://docs.docker.com/get-docker/",
        OS.OS_X: "Install docker: https://docs.docker.com/docker-for-mac/install/",
    }

    def __init__(self, minimum_version: Optional[int] = None):
        self.minimum_version = minimum_version

    def check(self) -> CheckResult:
        installed_version = get_major_docker_version()
        return self.validate_minimum_version("Docker", installed_version, self.minimum_version)


major_version_pattern = re.compile("Docker version ([0-9]+)")


def get_major_docker_version() -> Optional[int]:
    raw_version = get_stdout("docker --version")
    if raw_version:
        match = major_version_pattern.search(raw_version)
        if match:
            major_version_string = match.group(1)
            logging.debug(f"Docker major version: {major_version_string}")
            return int(major_version_string)
    return None


class DockerComposeInstalled(Check):
    name = "docker-compose.installed"

    suggestions = {OS.GENERIC: "Install docker-compose: https://docs.docker.com/compose/install/"}

    def check(self) -> CheckResult:
        return self.verify_install("docker-compose")
