import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from colors import red, yellow
from packaging import version

from daktari import __version__
from daktari.check import Check
from daktari.result_printer import print_suggestion_text


@dataclass
class Config:
    min_version: Optional[str]
    title: Optional[str]
    checks: List[Check]


version_regex = re.compile('daktari_version.*"([0-9.]+)"')


def read_config(config_path: Path) -> Optional[Config]:
    raw_config = config_path.read_text()
    return parse_raw_config(config_path, raw_config)


def parse_raw_config(config_path: Path, raw_config: str) -> Optional[Config]:
    if not check_version_compatibility(config_path, raw_config):
        return None

    variables: Dict[str, Any] = {}
    try:
        exec(raw_config, variables)
    except Exception:
        print(red(f"❌  Failed to parse {config_path} - config is not valid."))
        logging.error(f"Exception reading {config_path}", exc_info=True)
        return None

    checks = variables.get("checks", [])
    title = variables.get("title", None)
    min_version = variables.get("daktari_version", None)
    return Config(min_version, title, checks)


def check_version_compatibility(config_path: Path, raw_config: str) -> bool:
    match = version_regex.search(raw_config)
    disclaimer = "Specifying daktari_version is recommended to ensure team members have compatible versions installed."
    if match is None:
        print(yellow(f"⚠️  No minimum version found in {config_path}. {disclaimer}"))
        return True

    my_version = version.parse(__version__)
    required_version = version.parse(match.group(1))

    if not isinstance(required_version, version.Version):
        print(red(f"❌  Invalid daktari_version in {config_path}: {required_version}"))
        return False

    logging.debug(f"Doing version check. Mine [{my_version}], required [{required_version}]")
    if required_version > my_version:
        print(
            red(
                f"❌  Installed version of daktari [{my_version}] is "
                f"too old for this project (needs at least {required_version}). "
            )
        )
        print_suggestion_text("pip install daktari -U")
        return False

    return True
