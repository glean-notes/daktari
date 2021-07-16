from daktari.command_utils import get_stdout
from pathlib import Path


def is_ascii(path: str) -> bool:
    file_output = get_stdout(["file", path]) or ""
    parts = file_output.strip().split(": ")
    return parts[1] == "ASCII text"


def file_exists(path: str) -> bool:
    testing_file = Path(path)
    if testing_file.is_file():
        return True
    else:
        return False
