from daktari.check import Check, CheckResult
from daktari.command_utils import can_run_command, get_stdout
from daktari.os import OS


class AWSCLIInstalled(Check):
    name = "aws.cliInstalled"

    suggestions = {
        OS.OS_X: """<cmd>curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg" && \
    sudo installer -pkg AWSCLIV2.pkg -target /</cmd>""",
        OS.UBUNTU: """"<cmd>curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    sudo ./aws/install</cmd>""",
    }

    def check(self) -> CheckResult:
        return self.verify(can_run_command("aws --version"), "AWS CLI is <not/> installed and on $PATH")


class AWSProfileExists(Check):
    depends_on = [AWSCLIInstalled]

    def __init__(self, profile_name: str, suggestions: dict[str, str]):
        self.profile_name = profile_name
        self.name = f"aws.profileExists.{profile_name}"
        self.suggestions = suggestions

    def check(self) -> CheckResult:
        output = get_stdout("aws configure list-profiles")
        passed = bool(output and self.profile_name in output)
        if not passed:
            return self.failed(f"{self.profile_name} is not configured for the current user")
        return self.passed(f"{self.profile_name} is configured for the current user")
