"""Shared synthetic fixtures for tempify.interpolation tests (task-1.8).

All fixtures are deterministic (seeded RNG) and module-scoped to keep
per-test overhead low. Each fixture returns an ``xr.DataArray`` shaped
``(month=12, y=3, x=3)`` with a coord ``month`` taking values 1..12.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable

import numpy as np
import pytest
import xarray as xr

from tempify.interpolation.base import TemporalAxis

SEED = 42


def _wrap(values: np.ndarray) -> xr.DataArray:
    """Wrap a (12, 3, 3) numpy array as a tempify-compatible DataArray."""
    return xr.DataArray(
        values,
        dims=("month", "y", "x"),
        coords={"month": list(range(1, 13))},
    )


@pytest.fixture(scope="session")
def monthly_3x3_smooth() -> xr.DataArray:
    """Sinusoidal annual cycle, no NaN. Shape (12, 3, 3)."""
    rng = np.random.default_rng(SEED)
    months = np.arange(1, 13).reshape(12, 1, 1)
    base = 15.0 + 10.0 * np.sin(2 * np.pi * (months - 1) / 12)
    noise = rng.normal(loc=0.0, scale=0.1, size=(12, 3, 3))
    return _wrap(base + noise)


@pytest.fixture(scope="session")
def monthly_3x3_partial_nan() -> xr.DataArray:
    """Pixel (0, 0) has 3 NaNs in months 2, 6, 11. Rest is smooth."""
    rng = np.random.default_rng(SEED)
    months = np.arange(1, 13).reshape(12, 1, 1)
    base = 15.0 + 10.0 * np.sin(2 * np.pi * (months - 1) / 12)
    arr = (base + rng.normal(scale=0.1, size=(12, 3, 3))).copy()
    arr[1, 0, 0] = np.nan
    arr[5, 0, 0] = np.nan
    arr[10, 0, 0] = np.nan
    return _wrap(arr)


@pytest.fixture(scope="session")
def monthly_3x3_all_nan_pixel() -> xr.DataArray:
    """Pixel (1, 1) has all 12 months NaN. Rest is smooth."""
    rng = np.random.default_rng(SEED)
    months = np.arange(1, 13).reshape(12, 1, 1)
    base = 15.0 + 10.0 * np.sin(2 * np.pi * (months - 1) / 12)
    arr = (base + rng.normal(scale=0.1, size=(12, 3, 3))).copy()
    arr[:, 1, 1] = np.nan
    return _wrap(arr)


@pytest.fixture(scope="session")
def monthly_3x3_constant() -> xr.DataArray:
    """Constant value 20.0 everywhere. Useful for invariance tests."""
    return _wrap(np.full((12, 3, 3), 20.0))


@pytest.fixture(scope="session")
def temporal_axis_2023() -> TemporalAxis:
    """Non-leap-year daily target axis."""
    return TemporalAxis.from_months(2023)


@pytest.fixture(scope="session")
def temporal_axis_2024() -> TemporalAxis:
    """Leap-year daily target axis."""
    return TemporalAxis.from_months(2024)


def digest_arrays(arrays: Iterable[xr.DataArray]) -> str:
    """MD5 over concatenated raw bytes of a sequence of arrays. Used by tests."""
    h = hashlib.md5()
    for a in arrays:
        h.update(np.ascontiguousarray(a.values.astype(np.float64)).tobytes())
    return h.hexdigest()
