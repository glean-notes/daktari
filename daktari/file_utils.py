from daktari.command_utils import get_stdout


def is_ascii(path: str) -> bool:
    file_output = get_stdout(["file", path]) or ""
    parts = file_output.strip().split(": ")
    return parts[1] == "ASCII text"
