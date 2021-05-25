import logging
import re
from typing import Optional

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stdout
from daktari.os import OS


class DockerInstalled(Check):
    name = "docker.installed"

    suggestions = {
        OS.GENERIC: "Install docker: https://docs.docker.com/get-docker/"
    }

    def check(self) -> CheckResult:
        return self.verify_install("docker")


major_version_pattern = re.compile("([0-9]+)")


def get_major_docker_version() -> Optional[int]:
    raw_version = get_stdout("docker version --format '{{.Server.Version}}'")
    if raw_version:
        match = major_version_pattern.search(raw_version)
        if match:
            major_version_string = match.group(1)
            logging.debug(f"Docker major version: {major_version_string} (parsed from {raw_version})")
            return int(major_version_string)
    return None


class DockerVersion(Check):
    name = "docker.version"
    depends_on = [DockerInstalled]

    def __init__(self, required_version: int):
        self.required_version = required_version
        self.suggestions = {
            OS.GENERIC: f"Install a newer version of docker (at least {required_version}): https://docs.docker.com/get-docker/"
        }

    def check(self) -> CheckResult:
        major_version = get_major_docker_version()
        return self.verify(major_version >= self.required_version, f"Docker version is <not/> >={self.required_version} ({major_version})")


class DockerComposeInstalled(Check):
    name = "docker-compose.installed"

    suggestions = {
        OS.GENERIC: "Install docker-compose: https://docs.docker.com/compose/install/"
    }

    def check(self) -> CheckResult:
        return self.verify_install("docker-compose")
