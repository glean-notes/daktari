import re
from typing import Dict, Optional

from colors import green, red, underline

from daktari.check import CheckResult, CheckStatus
from daktari.os import OS, detect_os


def check_status_symbol(status: CheckStatus) -> str:
    return "✅" if status == CheckStatus.PASS else "❌"


def get_most_specific_suggestion(this_os: str, suggestions: Dict[str, str]) -> Optional[str]:
    def get_suggestion(os_to_match: str) -> Optional[str]:
        return next((message for os, message in suggestions.items() if os == os_to_match), None)

    return get_suggestion(this_os) or get_suggestion(OS.GENERIC)


def print_suggestion_text(text: str):
    pattern = re.compile("<cmd>(.+)</cmd>")

    def add_ansi_underline(match):
        return underline(match.group(1))

    replaced = pattern.sub(add_ansi_underline, text)
    lines = [line.lstrip() for line in replaced.splitlines()]

    raw_lines = [line.lstrip() for line in re.compile("</?cmd>").sub("", text).splitlines()]

    max_width = max([len(line) for line in raw_lines])
    title = "💡 Suggestion "
    print("┌─" + title + "─" * (max_width - len(title)) + "┐")
    for i, line in enumerate(lines):
        raw_line = raw_lines[i]
        padding = " " * (max_width - len(raw_line))
        print(f"│ {line}{padding} │")
    print("└" + "─" * (max_width + 2) + "┘")


def print_check_result(result: CheckResult):
    this_os = detect_os()
    status_symbol = check_status_symbol(result.status)
    colour = green if result.status == CheckStatus.PASS else red
    print(f"{status_symbol} [{colour(result.name)}] {result.summary}")
    if result.status == CheckStatus.FAIL:
        suggestion = get_most_specific_suggestion(this_os, result.suggestions)
        if suggestion:
            print_suggestion_text(suggestion)
