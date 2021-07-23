import json
import logging
import re
from typing import Optional

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stdout
from daktari.os import OS


class KubectlInstalled(Check):
    def __init__(self, minimum_version: Optional[float] = None):
        self.minimum_version = minimum_version
        self.name = "kubectl.installed"
        self.suggestions = {
            OS.OS_X: "<cmd>brew install kubectl</cmd>",
            OS.UBUNTU: "<cmd>sudo snap install kubectl --classic</cmd>",
            OS.GENERIC: "Install kubectl: https://kubernetes.io/docs/tasks/tools/#kubectl",
        }

    def check(self) -> CheckResult:
        installed_version = get_kubectl_version()
        return self.validate_minimum_version("Kubectl", installed_version, self.minimum_version)


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


class HelmInstalled(Check):
    name = "helm.installed"

    def __init__(self, minimum_version: Optional[float] = None):
        self.minimum_version = minimum_version
        self.suggestions = {
            OS.OS_X: "<cmd>brew install helm</cmd>",
            OS.UBUNTU: "<cmd>sudo snap install helm --classic</cmd>",
            OS.GENERIC: "Install Helm: https://helm.sh/docs/intro/install/",
        }

    def check(self) -> CheckResult:
        installed_version = get_helm_version()
        return self.validate_minimum_version("Helm", installed_version, self.minimum_version)


helm_version_pattern = re.compile("v([0-9]+.[0-9]+)")


def get_helm_version() -> Optional[float]:
    raw_version = get_stdout("helm version --short")
    if raw_version:
        match = helm_version_pattern.search(raw_version)
        if match:
            version_string = match.group(1)
            logging.debug(f"Helm Version: {version_string}")
            return float(version_string)
    return None


class HelmRepoExists(Check):
    depends_on = [HelmInstalled]

    def __init__(self, repo_name: str, repo_url: str):
        self.repo_name = repo_name
        self.repo_url = repo_url.strip("/")
        self.name = f"helm.repoExists.{repo_name}"
        self.suggestions = {
            OS.GENERIC: f"<cmd>helm repo add {repo_name} {repo_url} --force-update</cmd>",
        }

    def check(self) -> CheckResult:
        output = get_stdout("helm repo list -o json")
        if not output:
            return self.failed("No helm repos appear to be configured for the current user.")
        repo_json = json.loads(output)
        repo = next(filter(lambda repo_details: repo_details.get("name") == self.repo_name, repo_json), None)
        if repo is None:
            return self.failed(f"{self.repo_name} is not configured for the current user")

        installed_url = repo["url"].strip("/")
        logging.debug(f"{self.repo_name} helm repo is installed with URL {installed_url}.")

        if installed_url != self.repo_url:
            return self.failed(
                f"{self.repo_name} is configured to use the wrong URL. Expected {self.repo_url}, got {installed_url}"
            )

        return self.passed(f"{self.repo_name} is configured for the current user")
