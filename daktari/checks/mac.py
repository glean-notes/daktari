from daktari.command_utils import get_stdout

class RosettaInstalled(Check):
    name = "rosetta.installed"

    suggestions = {
        OS.OS_X: "<cmd>softwareupdate --install-rosetta</cmd>",
        OS.GENERIC: "Error: Only required on MacOS",
    }

    def check(self) -> CheckResult:
        # internally Rosetta is called OAH, `pgrep oahd` prints a number to stdout if Rosetta is installed
        return self.verify(get_stdout("pgrep oahd") != "", "Rosetta is <not/> installed")

