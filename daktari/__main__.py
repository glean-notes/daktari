import logging
import os
import sys

from pyfiglet import Figlet

from daktari.check_runner import run_checks, CheckRunner
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

    core_result = run_checks(config.checks)
    all_passed = core_result.all_passed

    for group_name, group_checks in config.extra_checks.items():
        print(f"\n{group_name}\n")
        runner = CheckRunner(group_checks, core_result.checks_passed)
        runner.run()
        all_passed = runner.all_passed and all_passed

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
        else:
            print(f"ⓘ  {ignored_count} check(s) have been marked as ignored. Run with --show-ignored to list them.\n")


if __name__ == "__main__":
    sys.exit(main())
