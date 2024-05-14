import json
from typing import Optional

from daktari.check import Check, CheckResult
from daktari.os import OS
from daktari.command_utils import get_stdout
from daktari.version_utils import get_simple_cli_version


class OnePasswordCliInstalled(Check):
    name = "onePasswordCli.installed"

    def __init__(self, required_version: Optional[str] = None, recommended_version: Optional[str] = None):
        self.required_version = required_version
        self.recommended_version = recommended_version
        self.suggestions = {
            OS.GENERIC: """
                Install the 1Password CLI (op):
                https://support.1password.com/command-line-getting-started/#set-up-the-command-line-tool""",
            OS.OS_X: """
                Use these commands to update 1pass-cli to correct version:
                <cmd>brew tap glean-notes/homebrew-tap git@github.com:glean-notes/homebrew-tap</cmd>
                <cmd>brew reinstall glean-notes/homebrew-tap/1password-cli</cmd>""",
        }

    def check(self) -> CheckResult:
        installed_version = get_simple_cli_version("op")
        return self.validate_semver_expression(
            "1Password CLI", installed_version, self.required_version, self.recommended_version
        )


class OnePasswordAccountConfigured(Check):
    depends_on = [OnePasswordCliInstalled]
    name = "onePassword.accountConfigured"

    def __init__(self, account_shorthand: str):
        self.account_shorthand = account_shorthand
        self.account_url = f"{account_shorthand}.1password.com"
        self.suggestions = {
            OS.GENERIC: f"<cmd>op signin --account {self.account_url}</cmd>",
        }

    def check(self) -> CheckResult:
        output = get_stdout("op account list")
        if output is None:
            return self.failed("1Password CLI command failed. Make sure it's installed and configured.")

        account_present = contains_account(output, self.account_url)

        if account_present:
            return self.passed(f"{self.account_shorthand} is configured with OP CLI for the current user")
        else:
            return self.failed(f"{self.account_shorthand} is not configured with OP CLI for the current user")


def contains_account(op_account_list_output: str, account_url: str) -> bool:
    return account_url in op_account_list_output


def account_exists(path: str, account_shorthand: str) -> bool:
    with open(path) as f:
        config = json.load(f)
    return any(account.get("shorthand") == account_shorthand for account in config.get("accounts", []))
