import logging
import re
from dataclasses import dataclass, replace, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from colors import red, yellow
from packaging import version
from yaml import YAMLError

from daktari import __version__
from daktari.check import Check
from daktari.check_utils import get_all_dependent_check_names
from daktari.resource_utils import get_resource
from daktari.result_printer import print_suggestion_text


@dataclass
class Config:
    min_version: Optional[str]
    title: Optional[str]
    checks: List[Check]
    ignored_checks: List[Check] = field(default_factory=list)


version_regex = re.compile('daktari_version.*"([0-9.]+)"')
LOCAL_CONFIG_PATH = ".daktari-local.yaml"
LOCAL_CONFIG_TEMPLATE = "daktari-local-template.yaml"


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

    # E.g. the file has been entirely commented out
    if local_config is None:
        return config

    ignored_checks: List[str] = local_config.get("ignoredChecks", [])
    return remove_ignored_checks(config, ignored_checks)


def write_local_config_template():
    contents = get_resource(LOCAL_CONFIG_TEMPLATE)
    with open(LOCAL_CONFIG_PATH, "w") as config_file:
        config_file.write(contents)

    print(
        f"A local config file has been generated at {LOCAL_CONFIG_PATH}. "
        f"Use this to override daktari behaviour - see the file for more details."
    )


def remove_ignored_checks(config: Config, ignored_check_names: List[str]) -> Config:
    ignored_checks = [check for check in config.checks if check_should_be_ignored(check, ignored_check_names)]
    remaining_checks = [check for check in config.checks if check not in ignored_checks]
    return replace(config, checks=remaining_checks, ignored_checks=ignored_checks)


def check_should_be_ignored(check: Check, ignored_check_names: List[str]) -> bool:
    dependents = get_all_dependent_check_names(check)
    return check.name in ignored_check_names or any([dependent in ignored_check_names for dependent in dependents])


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
