from argparse import ArgumentParser
from pathlib import Path


def validate_as_file_path(parser: ArgumentParser, arg: str) -> Path:
    path = Path(arg)
    if not path.is_file():
        parser.error(f"Could not find config file {arg}")
    else:
        return path


argument_parser = ArgumentParser(description="Check developer environment configuration.")
argument_parser.add_argument("--debug", default=False, action="store_true", help="turn on debug logging")
argument_parser.add_argument(
    "--config",
    default=".daktari.py",
    dest="config_path",
    required=False,
    help="Python configuration file",
    metavar="FILE",
    type=lambda arg: validate_as_file_path(argument_parser, arg),
)
