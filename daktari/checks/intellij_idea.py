import json
import logging
import os.path
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Optional

import dpath.util
from semver import VersionInfo

from daktari.check import Check, CheckResult
from daktari.checks.files import FilesExist
from daktari.checks.xml import XmlFileXPathCheck
from daktari.command_utils import CommandErrorException, run_command
from daktari.os import OS, detect_os
from daktari.version_utils import try_parse_semver, sanitise_version_string

BUNDLE_ID_INTELLIJ_IDEA = "com.jetbrains.intellij"
BUNDLE_ID_INTELLIJ_IDEA_CE = "com.jetbrains.intellij.ce"

SNAP_NAME_INTELLIJ_IDEA = "intellij-idea-ultimate"
SNAP_NAME_INTELLIJ_IDEA_CE = "intellij-idea-community"


def locate_intellij_idea_mac():
    from AppKit import NSWorkspace

    for bundle_id in (BUNDLE_ID_INTELLIJ_IDEA, BUNDLE_ID_INTELLIJ_IDEA_CE):
        url = NSWorkspace.sharedWorkspace().URLForApplicationWithBundleIdentifier_(bundle_id)
        if url is not None:
            logging.debug(f"IntelliJ IDEA location (via NSWorkspace): {url}")
            return url

    logging.debug("Could not find IntelliJ IDEA (via NSWorkspace)")
    return None


def get_intellij_idea_version_mac() -> Optional[VersionInfo]:
    intellij_url = locate_intellij_idea_mac()
    if intellij_url is None:
        return None
    else:
        from Foundation import NSBundle

        version_str = NSBundle.bundleWithURL_(intellij_url).objectForInfoDictionaryKey_("CFBundleShortVersionString")

        version_str = sanitise_version_string(version_str)
        version = try_parse_semver(version_str)

        logging.debug(f"IntelliJ IDEA version (via NSBundle): {version}")
        return version


def get_intellij_idea_version_snap() -> Optional[VersionInfo]:
    if not Path("/run/snapd.socket").is_socket():
        logging.debug("/run/snapd.socket does not exist, not querying snapd")
        return None

    from requests_unixsocket import Session

    session = Session()
    snaps_req = session.get(
        f"http+unix://%2Frun%2Fsnapd.socket/v2/snaps?snaps={SNAP_NAME_INTELLIJ_IDEA},{SNAP_NAME_INTELLIJ_IDEA_CE}"
    )
    snaps_info = snaps_req.json()
    logging.debug(f"response from snapd: {snaps_info}")
    version_str = dpath.util.get(snaps_info, "/result/0/version", default=None)
    logging.debug(f"raw snapd version: {version_str}")

    version_str = sanitise_version_string(version_str)

    version = try_parse_semver(version_str)
    logging.debug(f"IntelliJ IDEA version (via snapd): {version}")
    return version


def get_intellij_idea_version_tarball() -> Optional[VersionInfo]:
    try:
        idea_bin_path = run_command(["sh", "-c", "which idea.sh"]).stdout.rstrip("\n")
    except CommandErrorException:
        logging.debug("Could not locate idea.sh", exc_info=True)
        return None

    product_info_path = os.path.join(os.path.dirname(idea_bin_path), "..", "product-info.json")
    try:
        with open(product_info_path, "rb") as product_info_file:
            product_info = json.load(product_info_file)
    except IOError:
        logging.debug("Failed to read IntelliJ IDEA product-info.json", exc_info=True)
        return None
    except JSONDecodeError:
        logging.debug("Failed to parse IntelliJ IDEA product-info.json", exc_info=True)
        return None

    version_str = product_info.get("version", None)
    version = try_parse_semver(version_str)
    logging.debug(f"IntelliJ IDEA version (via product-info.json): {version}")
    return version


def get_intellij_idea_version() -> Optional[VersionInfo]:
    os = detect_os()
    if os == OS.OS_X:
        return get_intellij_idea_version_mac()
    elif os == OS.UBUNTU:
        return get_intellij_idea_version_snap() or get_intellij_idea_version_tarball()
    else:
        return get_intellij_idea_version_tarball()


class IntelliJIdeaInstalled(Check):
    name = "intellij.installed"

    suggestions = {OS.GENERIC: "Install IntelliJ Ultimate: https://www.jetbrains.com/idea/download/"}

    def __init__(self, required_version: Optional[str] = None, recommended_version: Optional[str] = None):
        self.required_version = required_version
        self.recommended_version = recommended_version

    def check(self) -> CheckResult:
        intellij_version = get_intellij_idea_version()
        return self.validate_semver_expression(
            "IntelliJ IDEA", intellij_version, self.required_version, self.recommended_version
        )


class IntelliJProjectImported(FilesExist):
    name = "intellij.projectImported"
    file_paths = [".idea/workspace.xml"]
    pass_fail_message = "Project <not/> imported into IntelliJ"
    depends_on = [IntelliJIdeaInstalled]
    suggestions = {
        OS.GENERIC: """
            From the IntelliJ start screen, click 'Open or Import' and choose the repository root directory
            """
    }


class IntelliJNodePackageManagerConfigured(XmlFileXPathCheck):
    name = "intellij.nodePackageManagerConfigured"
    file_path = ".idea/workspace.xml"
    xpath_query = "./component[@name='PropertiesComponent']"
    depends_on = [IntelliJProjectImported]

    def __init__(self, package_manager_path: str):
        self.package_manager_path = package_manager_path
        self.pass_fail_message = f"IntelliJ package manager has <not/> been set to {package_manager_path}"

        self.suggestions = {
            OS.GENERIC: f"""
                Follow the steps to configure {self.package_manager_path} as your package manager:
                https://www.jetbrains.com/help/idea/installing-and-removing-external-software-using-node-package-manager.html#ws_npm_yarn_set_yarn_default
                """
        }

    def validate_query_result(self, result):
        key_json = None if result is None else json.loads(result.text)
        logging.debug(f"Raw properties json: {key_json}")
        current_package_manager = str(key_json["keyToString"]["nodejs_package_manager_path"])
        logging.debug(f"IntelliJ node package manager set to: {current_package_manager}")
        return current_package_manager.__contains__(self.package_manager_path)
