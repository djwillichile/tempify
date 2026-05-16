"""Shared fixtures for tempify.io tests."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import rioxarray  # noqa: F401 - registers the .rio accessor
import xarray as xr


@pytest.fixture
def sample_geotiff(tmp_path: Path) -> Path:
    """Create a small single-band GeoTIFF in EPSG:4326 (4x4 pixels)."""
    rng = np.random.default_rng(0)
    arr = rng.standard_normal((4, 4)).astype(np.float32)
    da = xr.DataArray(
        arr,
        dims=("y", "x"),
        coords={
            "y": [3.5, 2.5, 1.5, 0.5],
            "x": [0.5, 1.5, 2.5, 3.5],
        },
        name="data",
    ).rio.write_crs("EPSG:4326")
    path = tmp_path / "sample.tif"
    da.rio.to_raster(path)
    return path


@pytest.fixture
def sample_multiband_geotiff(tmp_path: Path) -> Path:
    """Create a 3-band GeoTIFF in EPSG:4326 (3x3x3)."""
    rng = np.random.default_rng(1)
    arr = rng.standard_normal((3, 3, 3)).astype(np.float32)
    da = xr.DataArray(
        arr,
        dims=("band", "y", "x"),
        coords={
            "band": [1, 2, 3],
            "y": [2.5, 1.5, 0.5],
            "x": [0.5, 1.5, 2.5],
        },
        name="data",
    ).rio.write_crs("EPSG:4326")
    path = tmp_path / "multiband.tif"
    da.rio.to_raster(path)
    return path


@pytest.fixture
def sample_netcdf_monthly(tmp_path: Path) -> Path:
    """Create a 12-month NetCDF with a CF time axis (12x3x3)."""
    rng = np.random.default_rng(2)
    times = pd.date_range("2023-01-15", periods=12, freq="MS")
    arr = rng.standard_normal((12, 3, 3)).astype(np.float64)
    da = xr.DataArray(
        arr,
        dims=("time", "y", "x"),
        coords={
            "time": times,
            "y": [2.5, 1.5, 0.5],
            "x": [0.5, 1.5, 2.5],
        },
        name="tavg",
    ).rio.write_crs("EPSG:4326")
    da.attrs["units"] = "degC"
    da.attrs["long_name"] = "Air temperature (monthly mean)"
    da.attrs["standard_name"] = "air_temperature"
    path = tmp_path / "monthly.nc"
    da.to_netcdf(path)
    return path


@pytest.fixture
def geotiff_collection_dir(tmp_path: Path) -> tuple[Path, list[Path]]:
    """Create a folder with 3 single-band GeoTIFFs, returned (dir, paths)."""
    rng = np.random.default_rng(3)
    out_dir = tmp_path / "collection"
    out_dir.mkdir()
    paths = []
    for i in range(1, 4):
        arr = rng.standard_normal((3, 3)).astype(np.float32)
        da = xr.DataArray(
            arr,
            dims=("y", "x"),
            coords={
                "y": [2.5, 1.5, 0.5],
                "x": [0.5, 1.5, 2.5],
            },
            name="data",
        ).rio.write_crs("EPSG:4326")
        p = out_dir / f"step_{i:02d}.tif"
        da.rio.to_raster(p)
        paths.append(p)
    return out_dir, paths
