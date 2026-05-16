"""Tests for typed exceptions in tempify.interpolation (task-1.5)."""

from __future__ import annotations

import pytest

from tempify.interpolation.exceptions import (
    InterpolationError,
    InvalidMonthlyStackError,
    PartialNanPixelError,
    UnsupportedCalendarError,
)


def test_inheritance_chain() -> None:
    assert issubclass(InvalidMonthlyStackError, InterpolationError)
    assert issubclass(UnsupportedCalendarError, InterpolationError)
    assert issubclass(PartialNanPixelError, InterpolationError)


@pytest.mark.parametrize(
    ("exc_factory", "expected_code"),
    [
        (lambda: InvalidMonthlyStackError(n_months=11), "TEMPIFY-INT-001"),
        (lambda: UnsupportedCalendarError("360_day"), "TEMPIFY-INT-002"),
        (lambda: PartialNanPixelError(pixel_index=(0, 1), n_nan=3), "TEMPIFY-INT-003"),
    ],
)
def test_each_exception_has_referenceable_code(exc_factory: object, expected_code: str) -> None:
    """NFR-005: each exception class exposes a stable referenceable code."""
    assert exc_factory.__call__().__class__.code == expected_code  # type: ignore[attr-defined]


def test_invalid_monthly_message_in_spanish() -> None:
    err = InvalidMonthlyStackError(n_months=11)
    assert "12 meses" in str(err)
    assert "11" in str(err)


def test_invalid_monthly_with_reason() -> None:
    err = InvalidMonthlyStackError(n_months=12, reason="coord no contigua")
    assert "coord no contigua" in str(err)


def test_unsupported_calendar_message_in_spanish() -> None:
    err = UnsupportedCalendarError("360_day")
    assert "360_day" in str(err)
    assert "no es soportado" in str(err)
    assert "gregorian" in str(err)


def test_partial_nan_message_in_spanish_with_payload() -> None:
    err = PartialNanPixelError(pixel_index=(42, 17), n_nan=3)
    assert "(42, 17)" in str(err)
    assert "3/12" in str(err)
    assert "nan_policy" in str(err)
    assert err.pixel_index == (42, 17)
    assert err.n_nan == 3
