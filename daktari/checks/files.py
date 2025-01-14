from os.path import expanduser
from typing import List

from daktari.check import Check, CheckResult
from daktari.file_utils import dir_exists, file_exists, get_file_owner
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


class DirsExist(Check):
    name = "directories.exist"
    dir_paths: List[str] = []
    pass_fail_message = ""

    def check(self) -> CheckResult:
        dirs_exist = all([dir_exists(expanduser(dir_path)) for dir_path in self.dir_paths])
        return self.verify(dirs_exist, self.pass_fail_message)


class DirExists(DirsExist):
    name = "dir.exists"

    def __init__(self, dir_path: str, suggestion: str):
        self.dir_paths = [dir_path]
        self.pass_fail_message = f"{dir_path} is <not/> present"
        self.suggestions = {OS.GENERIC: suggestion}


class FilesOwnedByUser(Check):
    name = "files.ownedByUser"

    def __init__(
        self,
        file_paths: List[str],
        expected_owner: str = "root",
        pass_fail_message: str = "",
        follow_symlinks: bool = False,
    ):
        self.file_paths = file_paths
        self.expected_owner = expected_owner
        file_paths_str = ", ".join(file_paths)
        self.pass_fail_message = pass_fail_message or f"{file_paths_str} are <not/> owned by {expected_owner}"
        self.follow_symlinks = follow_symlinks

    def check(self) -> CheckResult:
        for file_path in self.file_paths:
            expanded_file_path = expanduser(file_path)
            if file_exists(expanded_file_path):
                if get_file_owner(expanded_file_path, self.follow_symlinks) != self.expected_owner:
                    return self.verify(False, self.pass_fail_message)
            else:
                return self.failed(f"{expanded_file_path} is not present")

        return self.verify(True, self.pass_fail_message)
