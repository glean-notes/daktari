import logging
import re
from typing import Optional
import json

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stdout
from daktari.os import OS, detect_os
from daktari.file_utils import file_exists
from pathlib import Path


class OnePassInstalled(Check):
    name = "onepass.installed"

    def __init__(self, minimum_version: Optional[float] = None):
        self.minimum_version = minimum_version
        self.suggestions = {
            OS.GENERIC: "Install OP (1Password CLI): "
            "https://support.1password.com/command-line-getting-started/#set-up-the-command-line-tool",
        }

    def check(self) -> CheckResult:
        installed_version = get_op_version()
        return self.validate_minimum_version("op", installed_version, self.minimum_version)


version_pattern = re.compile("([0-9]+.[0-9]+)")


def get_op_version() -> Optional[float]:
    raw_version = get_stdout("op --version")
    if raw_version:
        match = version_pattern.search(raw_version)
        if match:
            version_string = match.group(1)
            logging.debug(f"OP Version: {version_string}")
            return float(version_string)
    return None


class OPAccountExists(Check):
    depends_on = [OnePassInstalled]

    def __init__(self, context_name: str):
        self.context_name = context_name
        self.name = f"op.accountExists.{context_name}"
        self.suggestions = {
            OS.GENERIC: f"<cmd>op signin {context_name}.onepassword.com <your-email-here></cmd>",
        }

    def check(self) -> CheckResult:

        home = str(Path.home())
        if detect_os() == OS.OS_X:
            config_path = f"{home}/.op/config"
        else:
            config_path = f"{home}/.config/op/config"

        if file_exists(config_path):
            op_config = json.loads(open(config_path).read())
            account_json = op_config["accounts"]
            repo = next(
                filter(lambda op_contexts: op_contexts.get("shorthand") == self.context_name, account_json), None
            )
            if repo is None:
                return self.failed(f"{self.context_name} is not configured with OP CLI for the current user")

            return self.passed(f"{self.context_name} is configured with OP CLI for the current user")
        else:
            return self.failed("No 1Password config appears to be present on this machine.")
