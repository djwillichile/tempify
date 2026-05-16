"""Tests for PchipInterpolator (tasks 2.2.1-2.2.5)."""

from __future__ import annotations

import numpy as np
import pytest
import xarray as xr

from tempify.interpolation import PchipInterpolator, TemporalAxis
from tempify.interpolation._kernels import pchip_kernel
from tempify.interpolation.exceptions import PartialNanPixelError

# ---------------------------------------------------------------------------
# task-2.2.1 - kernel tests
# ---------------------------------------------------------------------------


class TestPchipKernel:
    """Pure SciPy-backed kernel correctness."""

    def test_constant_input_yields_constant_output(self) -> None:
        m = np.full(12, 7.5, dtype=np.float64)
        x_in = np.asarray(
            TemporalAxis.from_months(2023).monthly_anchor_doys(),
            dtype=np.float64,
        )
        x_out = np.arange(1, 366, dtype=np.float64)
        result = pchip_kernel(m, x_in, x_out, cyclic=True)
        assert np.allclose(result, 7.5, atol=1e-10)

    def test_sinusoidal_input_low_error(self) -> None:
        """Sinusoidal annual cycle interpolates with low L-infinity error."""
        x_in = np.asarray(
            TemporalAxis.from_months(2023).monthly_anchor_doys(),
            dtype=np.float64,
        )
        x_out = np.arange(1, 366, dtype=np.float64)
        period = 365.0
        m = 10.0 * np.sin(2 * np.pi * (x_in - 1) / period)
        expected = 10.0 * np.sin(2 * np.pi * (x_out - 1) / period)
        result = pchip_kernel(m, x_in, x_out, cyclic=True)
        assert np.max(np.abs(result - expected)) < 0.5


# ---------------------------------------------------------------------------
# task-2.2.2 - facade
# ---------------------------------------------------------------------------


class TestPchipFacade:
    """Facade integration with xarray."""

    def test_pchip_basic_on_smooth_fixture(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = PchipInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis)
        assert result.sizes["time"] == 365
        assert result.sizes["y"] == 3
        assert result.sizes["x"] == 3
        assert result.attrs["tempify_method"] == "pchip"
        assert result.attrs["tempify_monthly_anchor"] == "midpoint"

    def test_lazy_dask_evaluation_preserved(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = PchipInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis, chunk_size=2)
        assert hasattr(result.data, "dask"), "expected dask-backed result"


# ---------------------------------------------------------------------------
# task-2.2.3 - leap year handling
# ---------------------------------------------------------------------------


class TestPchipLeapYearOutputSize:
    """Output day count varies with target year."""

    def test_output_has_365_days_in_non_leap_year(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = PchipInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis)
        assert result.sizes["time"] == 365

    def test_output_has_366_days_in_leap_year(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = PchipInterpolator()
        axis = TemporalAxis.from_months(2024)
        result = interp.interpolate(monthly_3x3_smooth, axis)
        assert result.sizes["time"] == 366


# ---------------------------------------------------------------------------
# task-2.2.4 - cyclic continuity at year boundary (REQ-004)
# ---------------------------------------------------------------------------


class TestPchipCyclicContinuity:
    """C1 continuity at December-January boundary for smooth inputs."""

    def test_cyclic_boundary_continuity_kernel(self) -> None:
        x_in = np.asarray(
            TemporalAxis.from_months(2023).monthly_anchor_doys(),
            dtype=np.float64,
        )
        period = 365.0
        m = 10.0 * np.sin(2 * np.pi * (x_in - 1) / period)
        x_out = np.arange(1, 366, dtype=np.float64)
        result = pchip_kernel(m, x_in, x_out, cyclic=True)
        wrap_diff = abs(result[0] - result[-1])
        assert wrap_diff < 0.5

    def test_cyclic_boundary_continuity_facade(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = PchipInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis).compute()
        wrap = np.abs(result.isel(time=0).values - result.isel(time=-1).values)
        assert float(wrap.max()) < 5.0


# ---------------------------------------------------------------------------
# task-2.2.5 - non-cyclic extrapolation
# ---------------------------------------------------------------------------


class TestPchipNonCyclicExtrapolation:
    """Non-cyclic mode uses SciPy's natural polynomial extrapolation."""

    def test_non_cyclic_returns_finite_outside_range(self) -> None:
        x_in = np.asarray(
            TemporalAxis.from_months(2023).monthly_anchor_doys(),
            dtype=np.float64,
        )
        m = np.linspace(0.0, 11.0, 12, dtype=np.float64)
        x_out = np.array([1.0, 5.0, 365.0], dtype=np.float64)
        result = pchip_kernel(m, x_in, x_out, cyclic=False)
        assert np.all(np.isfinite(result))


# ---------------------------------------------------------------------------
# NaN policy
# ---------------------------------------------------------------------------


class TestPchipNanPolicy:
    """NaN propagation per REQ-008."""

    def test_all_nan_pixel_propagates_nan_to_all_days(
        self, monthly_3x3_all_nan_pixel: xr.DataArray
    ) -> None:
        interp = PchipInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_all_nan_pixel, axis).compute()
        nan_pixel = result.isel(y=1, x=1).values
        assert np.all(np.isnan(nan_pixel))
        valid_pixel = result.isel(y=0, x=0).values
        assert not np.any(np.isnan(valid_pixel))

    def test_partial_nan_with_raise_policy_raises(
        self, monthly_3x3_partial_nan: xr.DataArray
    ) -> None:
        interp = PchipInterpolator()
        axis = TemporalAxis.from_months(2023)
        with pytest.raises(PartialNanPixelError):
            interp.interpolate(monthly_3x3_partial_nan, axis, nan_policy="raise").compute()

    def test_partial_nan_with_propagate_all_returns_nan(
        self, monthly_3x3_partial_nan: xr.DataArray
    ) -> None:
        interp = PchipInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(
            monthly_3x3_partial_nan, axis, nan_policy="propagate_all"
        ).compute()
        partial_pixel = result.isel(y=0, x=0).values
        assert np.all(np.isnan(partial_pixel))

    def test_partial_nan_with_skip_pixel_interpolates_remaining(
        self, monthly_3x3_partial_nan: xr.DataArray
    ) -> None:
        interp = PchipInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(
            monthly_3x3_partial_nan, axis, nan_policy="skip_pixel"
        ).compute()
        partial_pixel = result.isel(y=0, x=0).values
        assert not np.any(np.isnan(partial_pixel))
