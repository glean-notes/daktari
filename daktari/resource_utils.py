from importlib_resources import files


def get_resource(name: str) -> str:
    """Load a textual resource file."""
    return files("daktari.resources").joinpath(name).read_text(encoding="utf-8")
