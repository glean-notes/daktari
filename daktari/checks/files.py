from os.path import expanduser
from typing import List

from daktari.check import Check, CheckResult
from daktari.file_utils import file_exists
from daktari.os import OS


class FilesExist(Check):
    name = "files.exist"
    file_paths: List[str] = []
    pass_fail_message = ""

    def check(self) -> CheckResult:
        files_exist = all([file_exists(expanduser(file_path)) for file_path in self.file_paths])
        return self.verify(files_exist, self.pass_fail_message)


class FileExists(FilesExist):
    name = "file.exists"

    def __init__(self, file_path: str, suggestion: str):
        self.file_paths = [file_path]
        self.pass_fail_message = f"{file_path} is <not/> present"
        self.suggestions = {OS.GENERIC: suggestion}
