from semver import VersionInfo
from typing import Optional


def try_parse_semver(version_str: str) -> Optional[VersionInfo]:
    try:
        return VersionInfo.parse(version_str)
    except ValueError:
        return None
