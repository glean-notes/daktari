from daktari.check import Check, CheckResult
from daktari.command_utils import can_run_command
from daktari.os import OS


class WatchmanInstalled(Check):
    name = "watchman.installed"

    suggestions = {
        OS.OS_X: "<cmd>brew install watchman</cmd>",
        OS.GENERIC: "Install watchman: https://facebook.github.io/watchman/docs/install.html#buildinstall",
    }

    def check(self) -> CheckResult:
        return self.verify(can_run_command("watchman --version"), "Watchman is <not/> installed")


class MkcertInstalled(Check):
    name = "mkcert.installed"

    suggestions = {
        OS.OS_X: "<cmd>brew install mkcert</cmd>",
        OS.GENERIC: "Install mkcert: https://mkcert.dev/#installation",
    }

    def check(self) -> CheckResult:
        return self.verify(can_run_command("mkcert -version"), "mkcert is <not/> installed")


class KtlintInstalled(Check):
    name = "ktlint.installed"

    suggestions = {
        OS.OS_X: "<cmd>brew install ktlint</cmd>",
        OS.GENERIC: "Install ktlint: https://github.com/pinterest/ktlint#installation",
    }

    def check(self) -> CheckResult:
        return self.verify(can_run_command("ktlint --version"), "ktlint is <not/> installed")
