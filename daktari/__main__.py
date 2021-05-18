import logging
import os
import sys

from pyfiglet import Figlet

from daktari.check_runner import run_checks
from daktari.config import read_config
from daktari.options import argument_parser


def print_logo(title: str):
    figlet = Figlet(font="slant")
    print(figlet.renderText(title))


def main() -> int:
    args = argument_parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    config = read_config(args.config_path)

    os.chdir(args.config_path.parent.absolute())

    if config.title:
        print_logo(config.title)
    all_passed = run_checks(config.checks)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
