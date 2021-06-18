import logging
import re
from typing import Optional

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stdout
from daktari.os import OS


class KubectlInstalled(Check):
    def __init__(self, minimum_version: Optional[float] = None):
        self.minimum_version = minimum_version
        self.name = "Kubectl.installed"
        self.suggestions = {
            OS.OS_X: "<cmd>brew install kubectl</cmd>",
            OS.UBUNTU: "<cmd>sudo snap install kubectl --classic</cmd>",
            OS.GENERIC: "Install kubectl: https://kubernetes.io/docs/tasks/tools/#kubectl",
        }

    def check(self) -> CheckResult:
        installed_version = get_kubectl_version()
        if installed_version is None:
            return self.failed("Kubectl is not installed")

        if self.minimum_version is None:
            return self.passed("Kubectl is installed")

        return self.verify(
            installed_version >= self.minimum_version,
            f"Kubectl version is <not/> >={self.minimum_version} ({installed_version})",
        )


version_pattern = re.compile("Client Version: v([0-9]+.[0-9]+)")


def get_kubectl_version() -> Optional[float]:
    raw_version = get_stdout("kubectl version --client=true --short")
    if raw_version:
        match = version_pattern.search(raw_version)
        if match:
            version_string = match.group(1)
            logging.debug(f"Kubectl version: {version_string}")
            return float(version_string)
    return None


class KubectlContextExists(Check):
    def __init__(self, context_name: str, provision_command: str = ""):
        self.context_name = context_name
        self.name = f"kubectl.contextExists.{context_name}"
        self.suggestions = {OS.GENERIC: provision_command}

    def check(self) -> CheckResult:
        output = get_stdout("kubectl config get-contexts")
        passed = bool(output and self.context_name in output)
        return self.verify(passed, f"{self.context_name} is <not/> configured for the current user")
