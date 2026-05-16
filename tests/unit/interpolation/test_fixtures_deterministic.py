"""Determinism check for shared fixtures (task-1.8)."""

from __future__ import annotations

import numpy as np
import xarray as xr

from tests.unit.interpolation.conftest import SEED, digest_arrays


def test_seeded_random_is_deterministic() -> None:
    """Two seeded RNGs must produce identical bytes (NFR-003 strict mode)."""
    rng_a = np.random.default_rng(SEED)
    rng_b = np.random.default_rng(SEED)
    a_vals = rng_a.normal(scale=0.1, size=(12, 3, 3))
    b_vals = rng_b.normal(scale=0.1, size=(12, 3, 3))

    a = xr.DataArray(a_vals, dims=("month", "y", "x"), coords={"month": list(range(1, 13))})
    b = xr.DataArray(b_vals, dims=("month", "y", "x"), coords={"month": list(range(1, 13))})
    assert digest_arrays([a]) == digest_arrays([b])


def test_fixture_smooth_is_deterministic(monthly_3x3_smooth: xr.DataArray) -> None:
    """Module-scoped fixture: same MD5 across invocations within a session."""
    d1 = digest_arrays([monthly_3x3_smooth])
    d2 = digest_arrays([monthly_3x3_smooth])
    assert d1 == d2
