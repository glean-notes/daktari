import logging
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class SuccessfulCommandResult:
    stdout: str
    stderr: str


class CommandNotFoundException(Exception):
    pass


class CommandErrorException(Exception):
    def __init__(self, message, return_code, stdout, stderr):
        super().__init__(message)

        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr


def run_command(command_parts):
    if isinstance(command_parts, str):
        command_parts = command_parts.split()
    combined_command = " ".join(command_parts)
    logging.debug(f"Running command '{combined_command}'")
    try:
        result = subprocess.run(
            command_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input="", universal_newlines=True
        )
    except FileNotFoundError:
        logging.debug(f"Command not found for '{combined_command}'.")
        raise CommandNotFoundException(f"Command not found: {combined_command}")
    if result.returncode != 0:
        logging.debug(
            f"Non-zero exit code for '{combined_command}'\n"
            f"Exit code = {result.returncode}\n"
            f"Stdout = {result.stdout}\n"
            f"Stderr = {result.stderr}\n"
        )
        raise CommandErrorException(
            f"Command returned exit code {result.returncode}: {combined_command}",
            result.returncode,
            result.stdout,
            result.stderr,
        )
    logging.debug(f"Result of '{combined_command}'. Stdout = {result.stdout}. Stderr = {result.stderr}.")

    return SuccessfulCommandResult(result.stdout, result.stderr)


def can_run_command(command) -> bool:
    try:
        run_command(command)
        return True
    except Exception:
        logging.debug("Exception running command", exc_info=True)
        return False


def get_stdout(command) -> Optional[str]:
    try:
        return run_command(command).stdout
    except Exception:
        logging.debug("Exception running command", exc_info=True)
        return None


def get_stderr(command) -> Optional[str]:
    try:
        return run_command(command).stderr
    except Exception:
        logging.debug("Exception running command", exc_info=True)
        return None
