import json
import logging
import re
from typing import Optional, List

from semver import VersionInfo

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stdout, can_run_command
from daktari.os import OS
from daktari.version_utils import try_parse_semver
from daktari.checks.google import GkeGcloudAuthPluginInstalled


class KubectlInstalled(Check):
    def __init__(self, required_version: Optional[str] = None, recommended_version: Optional[str] = None):
        self.required_version = required_version
        self.recommended_version = recommended_version
        self.name = "kubectl.installed"
        self.suggestions = {
            OS.OS_X: "<cmd>brew install kubectl</cmd>",
            OS.UBUNTU: "<cmd>sudo snap install kubectl --classic</cmd>",
            OS.GENERIC: "Install kubectl: https://kubernetes.io/docs/tasks/tools/#kubectl",
        }

    def check(self) -> CheckResult:
        installed_version = get_kubectl_version()
        return self.validate_semver_expression(
            "Kubectl", installed_version, self.required_version, self.recommended_version
        )


version_pattern = re.compile("Client Version: v(.*)")


def get_kubectl_version() -> Optional[VersionInfo]:
    raw_version = get_stdout("kubectl version --client=true --short")
    # Handle deprecation of --short
    if raw_version is None:
        raw_version = get_stdout("kubectl version --client=true")

    if raw_version:
        match = version_pattern.search(raw_version)
        if match:
            version = try_parse_semver(match.group(1))
            logging.debug(f"Kubectl version: {version}")
            return version
    return None


class KubectlContextExists(Check):
    depends_on = [GkeGcloudAuthPluginInstalled]

    def __init__(self, context_name: str, provision_command: str = ""):
        self.context_name = context_name
        self.name = f"kubectl.contextExists.{context_name}"
        self.suggestions = {OS.GENERIC: provision_command}

    def check(self) -> CheckResult:
        output = get_stdout("kubectl config get-contexts")
        passed = bool(output and self.context_name in output)
        if not passed:
            return self.failed(f"{self.context_name} is <not/> configured for the current user")

        can_connect = can_run_command(f"kubectl get ns --context {self.context_name}")
        return self.verify(can_connect, f"Could <not/> connect to context {self.context_name}")


class KubectlNoExtraneousContexts(Check):
    def __init__(self, expected_contexts: List[str]):
        self.expected_contexts = expected_contexts
        self.name = "kubectl.noExtraneousContexts"

    def check(self) -> CheckResult:
        output = get_stdout("kubectl config get-contexts -o name")
        if not output:
            return self.failed("Failed to list kubectl contexts")

        contexts = output.splitlines()
        extraneous_contexts = list(filter(lambda context: context not in self.expected_contexts, contexts))
        if extraneous_contexts:
            suggestion = "\n".join(
                f"<cmd>kubectl config delete-context {context}</cmd>" for context in extraneous_contexts
            )
            self.suggestions = {
                OS.GENERIC: suggestion,
            }
            return self.passed_with_warning(f"{len(extraneous_contexts)} extraneous kubectl context(s) found")

        return self.passed("No extraneous kubectl contexts found")


class HelmInstalled(Check):
    name = "helm.installed"

    def __init__(self, required_version: Optional[str] = None, recommended_version: Optional[str] = None):
        self.required_version = required_version
        self.recommended_version = recommended_version
        self.suggestions = {
            OS.OS_X: "<cmd>brew install helm</cmd>",
            OS.UBUNTU: "<cmd>sudo snap install helm --classic</cmd>",
            OS.GENERIC: "Install Helm: https://helm.sh/docs/intro/install/",
        }

    def check(self) -> CheckResult:
        installed_version = get_helm_version()
        return self.validate_semver_expression(
            "Helm", installed_version, self.required_version, self.recommended_version
        )


helm_version_pattern = re.compile("v([0-9\\.]+)")


def get_helm_version() -> Optional[VersionInfo]:
    raw_version = get_stdout("helm version --short")
    if raw_version:
        match = helm_version_pattern.search(raw_version)
        if match:
            version = try_parse_semver(match.group(1))
            logging.debug(f"Helm Version: {version}")
            return version
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
