from importlib_resources import files
from importlib_resources.abc import Traversable


def get_resource(name: str) -> str:
    """Load a textual resource file."""
    return get_resource_path(name).read_text(encoding="utf-8")


def get_resource_path(name: str) -> Traversable:
    return files("daktari.resources").joinpath(name)
