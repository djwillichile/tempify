"""Tests for tempify.constants (task-1.2)."""

from __future__ import annotations

import typing

import tempify.constants as constants


def test_constants_are_final_and_have_expected_values() -> None:
    """All 5 constants are typed Final with the documented default values."""
    annotations = typing.get_type_hints(constants, include_extras=True)

    assert constants.DEFAULT_CHUNK_SIZE == 512
    assert constants.DEFAULT_RM_CONVERGENCE_TOL == 1e-6
    assert constants.DEFAULT_RM_MAX_ITER == 50
    assert constants.FOURIER_MIN_HARMONICS == 1
    assert constants.FOURIER_MAX_HARMONICS == 5

    for name in (
        "DEFAULT_CHUNK_SIZE",
        "DEFAULT_RM_CONVERGENCE_TOL",
        "DEFAULT_RM_MAX_ITER",
        "FOURIER_MIN_HARMONICS",
        "FOURIER_MAX_HARMONICS",
    ):
        assert name in annotations, f"{name} must be present in module annotations"
        hint_repr = repr(annotations[name])
        assert "Final" in hint_repr, f"{name} must be annotated Final, got {hint_repr}"


def test_fourier_harmonics_range_respects_nyquist() -> None:
    """Max harmonics must stay strictly below Nyquist limit (12/2=6) for monthly data."""
    assert constants.FOURIER_MIN_HARMONICS >= 1
    assert constants.FOURIER_MAX_HARMONICS <= 5
    assert constants.FOURIER_MIN_HARMONICS < constants.FOURIER_MAX_HARMONICS
