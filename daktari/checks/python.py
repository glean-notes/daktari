from daktari.check import Check, CheckResult
from daktari.os import OS


class PythonInstalled(Check):
    def __init__(self, required_version: int):
        self.required_version = required_version
        self.name = f"python{required_version}.installed"
        self.suggestions = {
            OS.OS_X: f"<cmd>brew install python{required_version}</cmd>",
            OS.UBUNTU: f"<cmd>sudo apt install python{required_version}-dev</cmd>",
            OS.GENERIC: f"Download python {required_version}: https://www.python.org/downloads/",
        }

    def check(self) -> CheckResult:
        return self.verify_install(f"python{self.required_version}")
