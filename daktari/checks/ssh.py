from daktari.check import Check, CheckResult
from daktari.file_utils import file_contains_text, get_absolute_path
from daktari.os import OS, detect_os


class SSHConfigSetup(Check):
    name = "ssh.config.setup"

    suggestions = {
        OS.OS_X: """
            Add "IgnoreUnknown UseKeychain" and "UseKeychain yes" to ~/.ssh/config.
            E.g:
                Host *
                    IgnoreUnknown UseKeychain
                    UseKeychain yes
                    IdentityFile ~/.ssh/id_rsa
            """
    }

    def check(self) -> CheckResult:
        if detect_os() != OS.OS_X:
            return self.passed("Setup not required on non-Macbook devices")
        else:
            ssh_config_path = get_absolute_path("~/.ssh/config")
            if not file_contains_text(ssh_config_path, "IgnoreUnknown UseKeychain") or not file_contains_text(
                ssh_config_path, "UseKeychain yes"
            ):
                return self.failed("'IgnoreUnknown UseKeychain' or 'UseKeychain yes' not present in ~/.ssh/config")
            return self.passed("~/.ssh/config setup correctly")
