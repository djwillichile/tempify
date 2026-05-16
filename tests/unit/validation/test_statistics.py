"""Tests for StatisticalReporter."""

from __future__ import annotations

import numpy as np
import xarray as xr

from tempify.validation import StatisticalReporter
from tempify.validation.statistics import STATISTIC_NAMES


def test_six_canonical_keys_present() -> None:
    rng = np.random.default_rng(0)
    da = xr.DataArray(
        rng.standard_normal((4, 3, 3)),
        dims=("time", "y", "x"),
    )
    out = StatisticalReporter().report(da)
    assert "0" in out
    for k in STATISTIC_NAMES:
        assert k in out["0"]


def test_all_nan_pixel_reports_100_pct() -> None:
    da = xr.DataArray(
        np.full((2, 2, 2), np.nan),
        dims=("time", "y", "x"),
    )
    stats = StatisticalReporter().report(da)["0"]
    assert stats["nan_pct"] == 100.0
    assert stats["count_valid"] == 0


def test_mean_matches_numpy_reference() -> None:
    rng = np.random.default_rng(123)
    arr = rng.standard_normal((3, 4, 4))
    da = xr.DataArray(arr, dims=("time", "y", "x"))
    stats = StatisticalReporter().report(da)
    for i in range(3):
        ref = float(np.mean(arr[i]))
        assert abs(stats[str(i)]["mean"] - ref) < 1e-12


def test_handles_no_band_dim() -> None:
    arr = xr.DataArray(np.array([[1.0, 2.0], [3.0, 4.0]]), dims=("y", "x"))
    stats = StatisticalReporter().report(arr)
    assert stats["0"]["min"] == 1.0
    assert stats["0"]["max"] == 4.0
