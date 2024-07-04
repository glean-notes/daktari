import grp
import json
import os
from pathlib import Path
from stat import S_IMODE, S_ISGID
from typing import Optional

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stdout
from daktari.file_utils import file_exists
from daktari.os import OS
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
        self.suggestions = {
            OS.GENERIC: f"<cmd>op signin {account_shorthand}.1password.com <your-email-here></cmd>",
        }

    def check(self) -> CheckResult:
        home = str(Path.home())
        possible_paths = [f"{home}/.op/config", f"{home}/.config/op/config"]

        for config_path in possible_paths:
            if file_exists(config_path):
                op_config = json.loads(open(config_path).read())
                accounts = op_config.get("accounts", [])
                repo = next(filter(lambda account: account.get("shorthand") == self.account_shorthand, accounts), None)
                if repo is None:
                    return self.failed(f"{self.account_shorthand} is not configured with OP CLI for the current user")

                return self.passed(f"{self.account_shorthand} is configured with OP CLI for the current user")

        return self.failed("No 1Password config appears to be present on this machine.")


# If not set up, this breaks the integration between cli and desktop app (at least on Ubuntu)
# https://github.com/NeoHsu/asdf-1password-cli/issues/6#issuecomment-1587502411
class OnePasswordCliOwnedByCorrectGroup(Check):
    depends_on = [OnePasswordCliInstalled]
    name = "onePasswordCli.ownedByCorrectGroup"
    run_on = OS.UBUNTU

    def __init__(self):
        self.suggestions = {
            OS.UBUNTU: """
            Ensure the onepassword-cli group exists:
            <cmd>sudo groupadd -f onepassword-cli</cmd>
            Then update the group ownership and set group id when executing:
            <cmd>sudo chgrp onepassword-cli $(asdf which op) && sudo chmod g+s $(asdf which op)</cmd>
            """,
        }

    def check(self) -> CheckResult:
        op_path = get_stdout(["sh", "-c", "asdf which op"])
        if op_path is None:
            return self.failed("op not found")

        op_stat = os.stat(op_path)
        group_id = op_stat.st_gid
        group_name = grp.getgrgid(group_id)[0]

        if group_name != "onepassword-cli":
            return self.failed(f"op group should be onepassword-cli, but was {group_name}")

        if S_IMODE(op_stat.st_mode) & S_ISGID == 0:
            return self.failed("op does not set groupid when running")

        return self.passed("op has correct group and sets groupid when running")


def account_exists(path: str, account_shorthand: str) -> bool:
    with open(path) as f:
        config = json.load(f)
    return any(account.get("shorthand") == account_shorthand for account in config.get("accounts", []))
