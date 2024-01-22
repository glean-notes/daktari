import json
import logging
from typing import Optional

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stdout
from daktari.os import OS


class ConanInstalled(Check):
    name = "conan.installed"

    def __init__(self, required_version: Optional[str] = None, recommended_version: Optional[str] = None):
        self.required_version = required_version
        self.recommended_version = recommended_version
        self.suggestions = {OS.GENERIC: "Install conan: <cmd>pip install conan</cmd>"}

    def check(self) -> CheckResult:
        return self.verify_install("conan")


class ConanProfileDetected(Check):
    name = "conan.profileDetected"

    def __init__(self, expected_string: str):
        self.suggestions = {OS.GENERIC: "<cmd>conan profile detect</cmd>"}
        self.expected_string = expected_string
        self.depends_on = [ConanInstalled]

    def check(self) -> CheckResult:
        output = get_stdout("conan profile list")
        expected_profile_detected = output is not None and self.expected_string in output
        return self.verify(expected_profile_detected, f"conan profile {self.expected_string} <not/> detected")


class ConanRemoteDetected(Check):
    name = "conan.remoteDetected"

    def __init__(self, remote_name: str, remote_url: str):
        self.suggestions = {OS.GENERIC: f"<cmd>conan remote add {remote_name} {remote_url}</cmd>"}
        self.remote_name = remote_name
        self.remote_url = remote_url
        self.depends_on = [ConanInstalled]

    def check(self) -> CheckResult:
        output = get_stdout("conan remote list -f json")
        if output is None:
            return self.failed("No conan remotes configured for the current user.")
        remote_json = json.loads(output)
        remote = next(filter(lambda remote_details: remote_details.get("name") == self.remote_name, remote_json), None)
        if remote is None:
            return self.failed(f"{self.remote_name} conan remote is not configured for the current user.")

        configured_url = remote["url"].strip("/")
        logging.debug(f"{self.remote_name} conan remote is configured with URL {configured_url}.")

        if configured_url != self.remote_url:
            self.suggestions = {
                OS.GENERIC: f"<cmd>conan remote update --url {self.remote_url} {self.remote_name}</cmd>"
            }
            return self.failed(
                f"{self.remote_name} conan remote is configured with URL {configured_url}, expected {self.remote_url}"
            )

        if not remote["enabled"]:
            self.suggestions = {OS.GENERIC: f"<cmd>conan remote enable {self.remote_name}</cmd>"}
            return self.failed(f"{self.remote_name} conan remote is not enabled.")

        return self.passed(f"{self.remote_name} conan remote is configured for the current user.")


class ConanRemoteAuthenticated(Check):
    name = "conan.remoteAuthenticated"

    def __init__(self, remote_name: str, authentication_command: Optional[str] = None):
        self.suggestions = (
            {OS.GENERIC: authentication_command}
            if authentication_command
            else {OS.GENERIC: f"<cmd>conan remote login {remote_name}</cmd>"}
        )
        self.remote_name = remote_name
        self.depends_on = [ConanRemoteDetected]

    def check(self) -> CheckResult:
        output = get_stdout("conan remote list-users -f json")
        if output is None:
            return self.failed("No conan remotes configured for the current user.")
        remote_json = json.loads(output)
        remote = next(filter(lambda remote_details: remote_details.get("name") == self.remote_name, remote_json), None)
        if remote is None:
            return self.failed(f"{self.remote_name} conan remote is not configured for the current user.")

        if not remote["authenticated"]:
            return self.failed(f"{self.remote_name} conan remote is not authenticated.")

        return self.passed(f"{self.remote_name} conan remote is authenticated for the current user.")
