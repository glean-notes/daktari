import json
import logging
import os.path
from json import JSONDecodeError

from daktari.check import Check, CheckResult
from daktari.command_utils import can_run_command
from daktari.file_utils import file_exists
from daktari.os import OS, detect_os


class GoogleCloudSdkInstalled(Check):
    name = "google.cloudSdkInstalled"

    suggestions = {
        OS.OS_X: """<cmd>brew install --cask google-cloud-sdk</cmd>

Then, add the gcloud components to your PATH.

For bash users, add this to ~/.bashrc:
source "$(brew --prefix)/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/path.bash.inc"

For zsh users, add this to ~/.zhsrc:
source "$(brew --prefix)/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/path.zsh.inc\" """,
        OS.UBUNTU: "<cmd>sudo snap install google-cloud-sdk --classic</cmd>",
        OS.GENERIC: "Install gcloud: https://cloud.google.com/sdk/docs/quickstart",
    }

    def check(self) -> CheckResult:
        return self.verify(can_run_command("gcloud --version"), "Google Cloud SDK is <not/> installed and on $PATH")


class CloudSqlProxyInstalled(Check):
    name = "google.cloudSqlProxyInstalled"
    depends_on = [GoogleCloudSdkInstalled]

    suggestions = {
        OS.GENERIC: "Install Cloud SQL Proxy: <cmd>gcloud components install cloud_sql_proxy</cmd>",
    }

    def check(self) -> CheckResult:
        return self.verify(can_run_command("cloud_sql_proxy --version"), "Cloud SQL Proxy is <not/> installed")


class GkeGcloudAuthPluginInstalled(Check):
    name = "google.gkeGcloudAuthPluginInstalled"
    depends_on = [GoogleCloudSdkInstalled]

    suggestions = {
        OS.UBUNTU: "<cmd>sudo apt-get install google-cloud-sdk-gke-gcloud-auth-plugin</cmd>",
        OS.GENERIC: "<cmd>gcloud components install gke-gcloud-auth-plugin</cmd>",
    }

    def check(self) -> CheckResult:
        return self.verify(can_run_command("gke-gcloud-auth-plugin --version "), "GKE auth plugin is <not/> installed")


class DockerGoogleCloudAuthConfigured(Check):
    name = "google.dockerGCloudAuthConfigured"
    depends_on = [GoogleCloudSdkInstalled]

    def __init__(self, cloud_project, region, region_number):
        self.suggestions = {
            OS.OS_X: f"""
                Setup gcloud auth and add gcloud auth helper to docker config. Run:
                <cmd>gcloud init</cmd>
                Select '{cloud_project}' as the cloud project.
                Select '{region}' as the region ({region_number}). Then run:
                <cmd>gcloud auth configure-docker</cmd>
                """,
            OS.GENERIC: f"""
                On Linux you should be running docker with sudo.
                If you haven't already initialise gcloud as root:
                <cmd>sudo gcloud init</cmd>
                Select '{cloud_project}' as the cloud project.
                Select '{region}' as the region ({region_number}).
                Then create the docker config as root:
                <cmd>sudo gcloud auth configure-docker</cmd>
                """,
        }

    def check(self) -> CheckResult:
        if detect_os() != OS.OS_X:
            return self.passed_with_warning("Not checking docker gcloud configuration as it might require sudo")

        docker_config_path = os.path.expanduser("~/.docker/config.json")
        if not file_exists(docker_config_path):
            return self.failed(f"{docker_config_path} does not exist")

        try:
            with open(docker_config_path, "rb") as docker_config_file:
                docker_config = json.load(docker_config_file)
        except IOError:
            logging.error(f"Exception reading {docker_config_path}", exc_info=True)
            return self.failed(f"Failed to read {docker_config_path}")
        except JSONDecodeError:
            logging.error(f"Exception parsing {docker_config_path}", exc_info=True)
            return self.failed(f"Failed to parse {docker_config_path}")

        if docker_config.get("credHelpers", {}).get("gcr.io") != "gcloud":
            return self.failed("docker gcloud auth not configured")

        return self.passed("docker gcloud auth configured")
