"""Typed exceptions for the interpolation layer.

Each exception carries a stable error code (per NFR-005) accessible
via the class-level ``code`` attribute, and emits a Spanish-language
message that includes the relevant context payload. Per ADR-0004 the
precipitation rejection policy is enforced in :mod:`tempify.validation`,
not here.
"""

from __future__ import annotations

from typing import ClassVar


class InterpolationError(Exception):
    """Base class for all interpolation-layer errors."""

    code: ClassVar[str] = "TEMPIFY-INT-000"


class InvalidMonthlyStackError(InterpolationError):
    """Raised when the input stack does not have exactly 12 contiguous months."""

    code: ClassVar[str] = "TEMPIFY-INT-001"

    def __init__(self, n_months: int, reason: str | None = None) -> None:
        self.n_months = n_months
        self.reason = reason
        detail = f": {reason}" if reason else ""
        super().__init__(
            "El stack mensual debe tener exactamente 12 meses contiguos; "
            f"se encontraron {n_months}{detail}."
        )


class UnsupportedCalendarError(InterpolationError):
    """Raised when the input uses a non-Gregorian CF calendar."""

    code: ClassVar[str] = "TEMPIFY-INT-002"

    def __init__(self, calendar: str) -> None:
        self.calendar = calendar
        super().__init__(
            f"El calendario CF '{calendar}' no es soportado en v0.1.0; solo se "
            "aceptan calendarios 'gregorian', 'standard' o 'proleptic_gregorian'."
        )


class PartialNanPixelError(InterpolationError):
    """Raised when some (not all) months of a pixel are NaN under ``nan_policy='raise'``."""

    code: ClassVar[str] = "TEMPIFY-INT-003"

    def __init__(self, pixel_index: tuple[int, ...], n_nan: int) -> None:
        self.pixel_index = pixel_index
        self.n_nan = n_nan
        super().__init__(
            f"El píxel en posición {pixel_index} tiene {n_nan}/12 meses con NaN. "
            "Con nan_policy='raise' (por defecto) solo se permiten píxeles "
            "totalmente válidos o totalmente NaN. Use nan_policy='propagate_all' "
            "o 'skip_pixel' para tolerar NaN parcial."
        )
