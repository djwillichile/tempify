"""Shared fixtures for the validation tests."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import rioxarray  # noqa: F401 - registers the .rio accessor
import xarray as xr

from tempify.validation.profiles import VariableProfile


@pytest.fixture
def homogeneous_rasters() -> list[xr.DataArray]:
    """List of 3 small rasters in EPSG:4326 sharing CRS, extent, resolution."""
    rng = np.random.default_rng(0)
    rasters = []
    for _ in range(3):
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
        rasters.append(da)
    return rasters


@pytest.fixture
def temperature_profile() -> VariableProfile:
    return VariableProfile(
        name="temperature",
        canonical_name="air_temperature",
        units="degC",
        allowed_methods=("linear", "pchip", "pchip_mp", "fourier"),
        physical_min=-90.0,
        physical_max=60.0,
        acceptable_mean_error=1e-4,
        aliases=("tavg", "tmean", "tas"),
    )


@pytest.fixture
def precipitation_profile() -> VariableProfile:
    return VariableProfile(
        name="precipitation",
        canonical_name="precipitation_flux",
        units="mm",
        allowed_methods=(),
        physical_min=0.0,
        physical_max=2000.0,
        acceptable_mean_error=0.1,
        aliases=("pr", "ppt"),
    )


@pytest.fixture
def monthly_input_smooth() -> xr.DataArray:
    """Monthly DataArray (12, 3, 3) with a smooth sinusoidal cycle."""
    rng = np.random.default_rng(7)
    months = np.arange(1, 13).reshape(12, 1, 1)
    base = 15.0 + 10.0 * np.sin(2 * np.pi * (months - 1) / 12)
    arr = base + rng.normal(scale=0.1, size=(12, 3, 3))
    return xr.DataArray(
        arr,
        dims=("month", "y", "x"),
        coords={"month": list(range(1, 13))},
        name="tavg",
    )


@pytest.fixture
def daily_output_from_monthly(monthly_input_smooth: xr.DataArray) -> xr.DataArray:
    """Trivial 'interpolation' that returns a constant daily output per month."""
    times = pd.date_range("2023-01-01", "2023-12-31", freq="D")
    arr = np.zeros((len(times), 3, 3))
    for i, t in enumerate(times):
        arr[i] = monthly_input_smooth.isel(month=t.month - 1).values
    return xr.DataArray(
        arr,
        dims=("time", "y", "x"),
        coords={"time": times},
        name="tavg",
    )
