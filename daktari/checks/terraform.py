import logging
import re
from typing import Optional

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stdout
from daktari.os import OS


class TfenvInstalled(Check):
    name = "tfenv.installed"

    suggestions = {
        OS.OS_X: "<cmd>brew install tfenv</cmd>",
        OS.UBUNTU: """<cmd>git clone https://github.com/tfutils/tfenv.git ~/.tfenv</cmd>
                      <cmd>sudo ln -s ~/.tfenv/bin/* /usr/local/bin</cmd>""",
        OS.GENERIC: "Install tfenv: https://github.com/tfutils/tfenv",
    }

    def check(self) -> CheckResult:
        return self.verify_install("tfenv")


class TerraformInstalled(Check):
    def __init__(self, required_version: str = "", use_tfenv: bool = False):
        self.required_version = required_version
        self.name = "terraform.installed"
        self.use_tfenv = use_tfenv

        if use_tfenv:
            self.depends_on = [TfenvInstalled]

            # Read the required tf-version from tfenv (i.e. .terraform-version files)
            tfenv_version = open(".terraform-version", "r").read().strip()
            logging.debug(f"Terraform version required from .terraform-version file is: {tfenv_version}")
            self.required_version = tfenv_version
            self.suggestions = {OS.GENERIC: "<cmd>tfenv install</cmd>"}
        else:
            version_string = f"@{required_version}" if required_version else ""
            self.suggestions = {
                OS.OS_X: f"<cmd>brew tap hashicorp/tap && hashicorp/tap/terraform{version_string}</cmd>",
                OS.GENERIC: "Install Terraform: https://learn.hashicorp.com/tutorials/terraform/install-cli",
            }

    def check(self) -> CheckResult:
        installed_version = get_terraform_version()
        return self.validate_required_version(
            "Terraform", installed_version=installed_version, required_version=self.required_version
        )


version_pattern = re.compile("Terraform v([0-9]+.[0-9]+.[0-9]+)")


def get_terraform_version() -> Optional[str]:
    raw_version = get_stdout("terraform version")
    if raw_version:
        match = version_pattern.search(raw_version)
        if match:
            version_string = match.group(1)
            logging.debug(f"Terraform version: {version_string}")
            return str(version_string)
    return None
