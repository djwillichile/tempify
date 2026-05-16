"""CLI error catalog and exit codes."""

from __future__ import annotations

from typing import Final

EXIT_CODES: Final[dict[str, int]] = {
    "ok": 0,
    "validation_failure": 1,
    "user_cancellation": 2,
    "internal_error": 3,
    "sigint": 130,
}


class CliError(Exception):
    """Error raised by a CLI command with a stable code and exit status."""

    def __init__(self, message: str, exit_code: int = 3) -> None:
        super().__init__(message)
        self.exit_code = exit_code
