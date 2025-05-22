from daktari.check import Check, CheckResult
from daktari.os import OS


class EtcHostsFormattedCorrectly(Check):
    name = "etc.hosts.formattedCorrectly"
    description = "Check if /etc/hosts is formatted correctly with consistent use of tabs and spaces"

    def __init__(self):
        self.suggestions = {
            OS.GENERIC: "Reformat /etc/hosts to use a single space consistently in blankspace:\n\n" + r"<cmd>sudo sed -Ei 's:( |\t)+: :g' /etc/hosts</cmd>",
        }

    def check(self) -> CheckResult:
        with open("/etc/hosts", "r") as f:
            content = f.read()
            if "\t" in content or "  " in content:
                return self.failed("/etc/hosts is usess tabs or multiple spaces in blankspace.")
            else:
                return self.passed("/etc/hosts is formatted correctly")

