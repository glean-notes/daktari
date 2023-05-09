import logging
import os
import sys

from pyfiglet import Figlet

from daktari.check_runner import run_checks
from daktari.config import read_config, Config, write_local_config_template
from daktari.options import argument_parser


def print_logo(title: str):
    figlet = Figlet(font="slant")
    print(figlet.renderText(title))


def main() -> int:
    args = argument_parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.generate_local_config:
        write_local_config_template()
        return 0

    config = read_config(args.config_path)
    if config is None:
        return 1

    os.chdir(args.config_path.parent.absolute())
    print_config_messages(config, args)

    all_passed = run_checks(config.checks, args.quiet_mode or config.quiet_mode, args.fail_fast)
    print("")
    return 0 if all_passed else 1


def print_config_messages(config: Config, args):
    if config.title:
        print_logo(config.title)

    ignored_count = len(config.ignored_checks)
    if ignored_count > 0:
        if args.show_ignored:
            print("ⓘ  The following checks have been ignored:\n")
            for check in config.ignored_checks:
                print(f"[{check.name}]")
            print("")
        elif not args.quiet_mode:
            print(f"ⓘ  {ignored_count} check(s) have been marked as ignored. Run with --show-ignored to list them.\n")


if __name__ == "__main__":
    sys.exit(main())
