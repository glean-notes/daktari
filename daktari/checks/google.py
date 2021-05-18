from daktari.check import Check, CheckResult
from daktari.command_utils import can_run_command
from daktari.os import OS


class GoogleCloudSdkInstalled(Check):
    name = "google.cloudSdkInstalled"

    suggestions = {
        OS.OS_X: "<cmd>brew install --cask google-cloud-sdk</cmd>",
        OS.UBUNTU: "<cmd>sudo snap install google-cloud-sdk --classic</cmd>",
        OS.GENERIC: "Install gcloud: https://cloud.google.com/sdk/docs/quickstart",
    }

    def check(self) -> CheckResult:
        return self.verify(can_run_command("gcloud --version"), "Google Cloud SDK is <not/> installed")


class CloudSqlProxyInstalled(Check):
    name = "google.cloudSqlProxyInstalled"
    depends_on = [GoogleCloudSdkInstalled]

    suggestions = {
        OS.GENERIC: "Install Cloud SQL Proxy: <cmd>gcloud components install cloud_sql_proxy</cmd>",
    }

    def check(self) -> CheckResult:
        return self.verify(can_run_command("cloud_sql_proxy --version"), "Cloud SQL Proxy is <not/> installed")
