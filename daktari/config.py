from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from daktari.check import Check


@dataclass
class Config:
    title: Optional[str]
    checks: List[Check]


def read_config(config_path: Path) -> Config:
    variables: Dict[str, Any] = {}
    exec(config_path.read_text(), variables)
    checks = variables.get("checks", [])
    title = variables.get("title", None)
    return Config(title, checks)
