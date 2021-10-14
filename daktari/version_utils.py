from typing import Optional

from semver import VersionInfo


def try_parse_semver(version_str: Optional[str]) -> Optional[VersionInfo]:
    try:
        return None if version_str is None else VersionInfo.parse(version_str)
    except ValueError:
        return None
