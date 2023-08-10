from pathlib import Path

from daktari.command_utils import get_stdout

import os
import re


def get_absolute_path(path: str) -> str:
    return os.path.expanduser(path)


def is_ascii(path: str) -> bool:
    file_output = get_stdout(["file", path]) or ""
    parts = file_output.strip().split(": ")
    return parts[1] == "ASCII text"


def file_exists(path: str) -> bool:
    testing_file = Path(path)
    return testing_file.is_file()


def file_contains_text(path: str, text: str) -> bool:
    if not file_exists(path):
        return False
    with open(path, "r") as file:
        for line in file:
            if text in line:
                return True
    return False


def file_contains_text_regex(path: str, regex: str) -> bool:
    if not file_exists(path):
        return False
    with open(path, "r") as file:
        for line in file:
            if re.search(regex, line):
                return True
    return False


def dir_exists(path: str) -> bool:
    testing_dir = Path(path)
    return testing_dir.is_dir()
