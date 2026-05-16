"""Tests for GeospatialCoherenceValidator."""

from __future__ import annotations

import numpy as np
import pytest
import rioxarray  # noqa: F401
import xarray as xr

from tempify.validation import (
    CANONICAL_TOLERANCES,
    GeospatialCoherenceValidator,
    Tolerances,
)
from tempify.validation._codes import (
    GEO_CRS_MISMATCH,
    GEO_EXTENT_MISMATCH,
    GEO_RESOLUTION_MISMATCH,
    GEO_SHAPE_MISMATCH,
)


def _raster(crs: str = "EPSG:4326", shape: tuple[int, int] = (3, 3)) -> xr.DataArray:
    rng = np.random.default_rng(0)
    arr = rng.standard_normal(shape).astype(np.float32)
    y = list(range(shape[0] - 1, -1, -1))
    x = list(range(shape[1]))
    return xr.DataArray(
        arr,
        dims=("y", "x"),
        coords={"y": [v + 0.5 for v in y], "x": [v + 0.5 for v in x]},
        name="data",
    ).rio.write_crs(crs)


def test_homogeneous_passes(homogeneous_rasters: list[xr.DataArray]) -> None:
    validator = GeospatialCoherenceValidator()
    report = validator.check(homogeneous_rasters)
    assert report.pre_passed is True
    assert not report.errors


def test_crs_mismatch_detected() -> None:
    a = _raster("EPSG:4326")
    b = _raster("EPSG:3857")
    report = GeospatialCoherenceValidator().check([a, b])
    crs_check = next(c for c in report.checks if c.check_id == GEO_CRS_MISMATCH)
    assert crs_check.passed is False
    assert report.pre_passed is False


def test_shape_mismatch_detected() -> None:
    a = _raster(shape=(3, 3))
    b = _raster(shape=(4, 4))
    report = GeospatialCoherenceValidator().check([a, b])
    shape_check = next(c for c in report.checks if c.check_id == GEO_SHAPE_MISMATCH)
    assert shape_check.passed is False


def test_resolution_mismatch_detected() -> None:
    a = _raster(shape=(3, 3))
    b_arr = xr.DataArray(
        np.zeros((3, 3), dtype=np.float32),
        dims=("y", "x"),
        coords={"y": [10.0, 5.0, 0.0], "x": [0.0, 5.0, 10.0]},  # 5-unit res
        name="data",
    ).rio.write_crs("EPSG:4326")
    report = GeospatialCoherenceValidator().check([a, b_arr])
    res_check = next(c for c in report.checks if c.check_id == GEO_RESOLUTION_MISMATCH)
    assert res_check.passed is False


def test_extent_mismatch_detected() -> None:
    a = _raster(shape=(3, 3))
    b_arr = xr.DataArray(
        np.zeros((3, 3), dtype=np.float32),
        dims=("y", "x"),
        coords={"y": [102.5, 101.5, 100.5], "x": [0.5, 1.5, 2.5]},
        name="data",
    ).rio.write_crs("EPSG:4326")
    report = GeospatialCoherenceValidator().check([a, b_arr])
    ext_check = next(c for c in report.checks if c.check_id == GEO_EXTENT_MISMATCH)
    assert ext_check.passed is False


def test_empty_list_raises() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        GeospatialCoherenceValidator().check([])


def test_canonical_tolerances_have_expected_defaults() -> None:
    assert CANONICAL_TOLERANCES.extent_rtol == 1e-6
    assert CANONICAL_TOLERANCES.resolution_rtol == 1e-6


def test_custom_tolerances_accepted() -> None:
    t = Tolerances(extent_rtol=1e-3, extent_atol_factor=0.05, resolution_rtol=1e-3)
    validator = GeospatialCoherenceValidator(tolerances=t)
    assert validator.tolerances.extent_rtol == 1e-3
