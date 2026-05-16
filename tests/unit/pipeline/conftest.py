"""Shared fixtures for pipeline tests."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import rioxarray  # noqa: F401 - registers the .rio accessor
import xarray as xr


@pytest.fixture
def worldclim_like_dir(tmp_path: Path) -> Path:
    """Folder with 12 monthly GeoTIFFs named like WorldClim."""
    rng = np.random.default_rng(0)
    out = tmp_path / "worldclim_like"
    out.mkdir()
    for month in range(1, 13):
        arr = (
            15.0 + 10.0 * np.sin(2 * np.pi * (month - 1) / 12) + rng.normal(scale=0.1, size=(3, 3))
        ).astype(np.float32)
        da = xr.DataArray(
            arr,
            dims=("y", "x"),
            coords={"y": [2.5, 1.5, 0.5], "x": [0.5, 1.5, 2.5]},
            name="data",
        ).rio.write_crs("EPSG:4326")
        da.rio.to_raster(out / f"wc2.1_2.5m_tavg_{month:02d}.tif")
    return out
