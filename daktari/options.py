from argparse import ArgumentParser
from pathlib import Path

from daktari import __version__


def validate_as_file_path(parser: ArgumentParser, arg: str) -> Path:
    path = Path(arg)
    if not path.is_file():
        parser.error(f"Could not find config file {arg}")
    else:
        return path


argument_parser = ArgumentParser(description="Check developer environment configuration.")
argument_parser.add_argument("-d", "--debug", action="store_true", help="turn on debug logging")
argument_parser.add_argument(
    "-g", "--generate-local-config", action="store_true", help="generate a template file for local configuration"
)
argument_parser.add_argument(
    "-i", "--show-ignored", action="store_true", help="show checks affected by ignoredChecks local setting"
)
argument_parser.add_argument(
    "-c",
    "--config",
    default=".daktari.py",
    dest="config_path",
    required=False,
    help="Python configuration file",
    metavar="FILE",
    type=lambda arg: validate_as_file_path(argument_parser, arg),
)
argument_parser.add_argument("--version", action="version", version="%(prog)s {version}".format(version=__version__))
