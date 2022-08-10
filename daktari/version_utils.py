import logging
from typing import Optional

from semver import VersionInfo

from daktari.command_utils import get_stdout


def get_simple_cli_version(binary_name: str) -> Optional[VersionInfo]:
    raw_version = get_stdout(f"{binary_name} --version")
    if raw_version:
        version = try_parse_semver(raw_version)
        logging.debug(f"{binary_name} version: {version}")
        return version
    return None


def try_parse_semver(version_str: Optional[str]) -> Optional[VersionInfo]:
    try:
        return None if version_str is None else VersionInfo.parse(version_str)
    except ValueError:
        return None


def sanitise_version_string(version_str: str) -> str:
    return version_str + ".0" if version_str.count(".") == 1 else version_str
