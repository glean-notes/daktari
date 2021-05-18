import logging

from daktari.check import Check, CheckResult
from daktari.command_utils import can_run_command, get_stdout
from daktari.file_utils import is_ascii
from daktari.os import OS


class GitInstalled(Check):
    name = "git.installed"

    suggestions = {
        OS.OS_X: "<cmd>brew install git</cmd>",
        OS.UBUNTU: "<cmd>sudo apt install git</cmd>",
        OS.GENERIC: "Install Git: https://git-scm.com/downloads",
    }

    def check(self) -> CheckResult:
        if can_run_command("git version"):
            return self.passed("Git is installed")
        else:
            return self.failed("Could not find git on the path")


class GitLfsInstalled(Check):
    name = "git.lfs.installed"
    depends_on = [GitInstalled]

    suggestions = {
        OS.OS_X: "<cmd>brew install git-lfs</cmd>",
        OS.UBUNTU: "<cmd>sudo apt install git-lfs</cmd>",
        OS.GENERIC: "Install Git LFS: https://github.com/git-lfs/git-lfs/wiki/Installation",
    }

    def check(self) -> CheckResult:
        return self.verify(can_run_command("git lfs version"), "Git LFS is <not/> installed")


class GitLfsSetUpForUser(Check):
    name = "git.lfs.setUpForUser"
    depends_on = [GitLfsInstalled]

    suggestions = {
        OS.GENERIC: """Set up Git LFS for your user account:
                       <cmd>git lfs install</cmd>"""
    }

    def check(self) -> CheckResult:
        output = get_stdout("git lfs env")
        passed = bool(output and "git config filter.lfs" in output)
        return self.verify(passed, "Git LFS is <not/> set up for the current user")


class GitLfsFilesDownloaded(Check):
    name = "git.lfs.filesDownloaded"
    depends_on = [GitLfsSetUpForUser]

    suggestions = {
        OS.GENERIC: """Download all Git LFS files and update working copy with the downloaded content:
                       <cmd>git lfs pull</cmd>"""
    }

    def check(self) -> CheckResult:
        output = get_stdout("git lfs ls-files") or ""
        files_not_downloaded = [line.split()[2] for line in output.splitlines() if line.split()[1] == "-"]
        for file in files_not_downloaded:
            logging.info(f"Git LFS file not downloaded: {file}")
        passed = len(files_not_downloaded) == 0
        return self.verify(passed, "Git LFS files have <not/> been downloaded")


class GitCryptInstalled(Check):
    name = "git.crypt.installed"
    depends_on = [GitInstalled]

    suggestions = {
        OS.OS_X: "<cmd>brew install git-crypt</cmd>",
        OS.UBUNTU: "<cmd>sudo apt install git-crypt</cmd>",
        OS.GENERIC: "Install git-crypt: https://www.agwa.name/projects/git-crypt/",
    }

    def check(self) -> CheckResult:
        return self.verify(can_run_command("git crypt version"), "git-crypt is <not/> installed")


class GitCryptUnlocked(Check):
    name = "git.crypt.unlocked"
    depends_on = [GitCryptInstalled]

    def __init__(self, fileToCheck: str):
        self.fileToCheck = fileToCheck

    suggestions = {
        OS.GENERIC: """Unlock this repository with:
                       <cmd>git-crypt unlock</cmd>""",
    }

    def check(self) -> CheckResult:
        is_unlocked = is_ascii(self.fileToCheck)
        return self.verify(is_unlocked, "Encrypted files have <not/> been unlocked")


class PreCommitInstalled(Check):
    name = "preCommit.installed"
    depends_on = [GitInstalled]

    suggestions = {
        OS.OS_X: "<cmd>brew install pre-commit</cmd>",
        OS.GENERIC: "Install pre-commit: https://pre-commit.com/#installation",
    }

    def check(self) -> CheckResult:
        return self.verify(can_run_command("pre-commit --version"), "pre-commit is <not/> installed")
