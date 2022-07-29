import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from colors import red, yellow
from packaging import version
from yaml import YAMLError

from daktari import __version__
from daktari.check import Check
from daktari.check_utils import get_all_dependent_check_names
from daktari.result_printer import print_suggestion_text


@dataclass
class Config:
    min_version: Optional[str]
    title: Optional[str]
    checks: List[Check]


version_regex = re.compile('daktari_version.*"([0-9.]+)"')
LOCAL_CONFIG_PATH = "daktari-local.yml"


def read_config(config_path: Path) -> Optional[Config]:
    raw_config = config_path.read_text()
    config = parse_raw_config(config_path, raw_config)
    if config is None:
        return config

    return apply_local_config(config)


def apply_local_config(config: Config) -> Optional[Config]:
    if not Path(LOCAL_CONFIG_PATH).is_file():
        return config

    try:
        with open(LOCAL_CONFIG_PATH, "rb") as local_config_file:
            local_config = yaml.safe_load(local_config_file)
    except YAMLError:
        print(red(f"❌  Failed to parse {LOCAL_CONFIG_PATH} - config is not valid YAML. Error follows."))
        logging.error(f"Exception reading {LOCAL_CONFIG_PATH}", exc_info=True)
        return None

    ignored_checks: List[str] = local_config.get("ignoredChecks", [])
    checks = remove_ignored_checks(config.checks, ignored_checks)
    return Config(config.min_version, config.title, checks)


def remove_ignored_checks(checks: List[Check], ignored_checks: List[str]) -> List[Check]:
    return list(filter(lambda check: not check_should_be_ignored(check, ignored_checks), checks))


def check_should_be_ignored(check: Check, ignored_checks: List[str]) -> bool:
    dependents = get_all_dependent_check_names(check)
    return any([dependent in ignored_checks for dependent in dependents])


def parse_raw_config(config_path: Path, raw_config: str) -> Optional[Config]:
    if not check_version_compatibility(config_path, raw_config):
        return None

    variables: Dict[str, Any] = {}
    try:
        compiled_config = compile(raw_config, config_path, "exec")
        exec(compiled_config, variables)
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
