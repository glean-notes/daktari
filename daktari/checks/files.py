from os.path import expanduser
from pathlib import Path

from daktari.check import Check, CheckResult
from daktari.os import OS


class FileExists(Check):
    name = "file.exists"

    def __init__(self, file_path: str, suggestion: str):
        self.file_path = file_path.replace("~", expanduser("~"))
        self.suggestions = {OS.GENERIC: suggestion}

    def check(self) -> CheckResult:
        return self.verify(Path(self.file_path).exists(), f"{self.file_path} is <not/> present")
