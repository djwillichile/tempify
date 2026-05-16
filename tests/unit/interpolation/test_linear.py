"""Tests for LinearInterpolator (tasks 2.1.1, 2.1.2, 2.1.3, 2.1.4)."""

from __future__ import annotations

from datetime import datetime

import numpy as np
import pytest
import xarray as xr

from tempify.interpolation import LinearInterpolator, TemporalAxis
from tempify.interpolation._kernels import linear_kernel
from tempify.interpolation.exceptions import PartialNanPixelError

# ---------------------------------------------------------------------------
# task-2.1.1 - kernel tests
# ---------------------------------------------------------------------------


class TestLinearKernel:
    """Pure NumPy kernel correctness (task-2.1.1)."""

    def test_constant_input_yields_constant_output(self) -> None:
        m = np.full(12, 7.5, dtype=np.float64)
        x_in = np.asarray(TemporalAxis.from_months(2023).monthly_anchor_doys(), dtype=np.float64)
        x_out = np.arange(1, 366, dtype=np.float64)
        result = linear_kernel(m, x_in, x_out, cyclic=True)
        assert np.allclose(result, 7.5, atol=1e-12)

    def test_linear_in_x_in_yields_linear_in_x_out(self) -> None:
        """If input is linear in x_in (non-cyclic), output is linear in x_out."""
        x_in = np.asarray(TemporalAxis.from_months(2023).monthly_anchor_doys(), dtype=np.float64)
        slope = 0.5
        intercept = 1.0
        m = slope * x_in + intercept
        x_out = np.arange(int(x_in[0]), int(x_in[-1]) + 1, dtype=np.float64)
        result = linear_kernel(m, x_in, x_out, cyclic=False)
        expected = slope * x_out + intercept
        assert np.max(np.abs(result - expected)) < 1e-12


# ---------------------------------------------------------------------------
# task-2.1.2 - facade integration
# ---------------------------------------------------------------------------


class TestLinearInterpolatorFacade:
    """Facade integration with xarray (task-2.1.2)."""

    def test_linear_basic_on_smooth_fixture(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = LinearInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis)
        assert result.sizes["time"] == 365
        assert result.sizes["y"] == 3
        assert result.sizes["x"] == 3
        assert result.attrs["tempify_method"] == "linear"
        assert result.attrs["tempify_monthly_anchor"] == "midpoint"

    def test_lazy_dask_evaluation_preserved(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = LinearInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis, chunk_size=2)
        # Dask-backed before .compute
        assert hasattr(result.data, "dask"), "expected dask-backed result"

    def test_time_coordinate_matches_target_axis(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = LinearInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis)
        times = list(result.coords["time"].values)
        assert times[0] == np.datetime64(datetime(2023, 1, 1))
        assert times[-1] == np.datetime64(datetime(2023, 12, 31))


# ---------------------------------------------------------------------------
# task-2.1.3 - leap year handling
# ---------------------------------------------------------------------------


class TestLinearLeapYearOutputSize:
    """Output day count varies with target year (task-2.1.3)."""

    def test_output_has_365_days_in_non_leap_year(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = LinearInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis)
        assert result.sizes["time"] == 365

    def test_output_has_366_days_in_leap_year(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = LinearInterpolator()
        axis = TemporalAxis.from_months(2024)
        result = interp.interpolate(monthly_3x3_smooth, axis)
        assert result.sizes["time"] == 366


# ---------------------------------------------------------------------------
# task-2.1.4 - non-cyclic extrapolation (REQ-005a)
# ---------------------------------------------------------------------------


class TestLinearNonCyclicExtrapolation:
    """Non-cyclic constant extrapolation at boundaries (task-2.1.4, REQ-005a)."""

    def test_non_cyclic_linear_constant_before_first_anchor(self) -> None:
        """For t < x_in[0] (first midpoint), output equals m[0]."""
        m = np.array([10.0] + [20.0] * 11, dtype=np.float64)
        x_in = np.asarray(TemporalAxis.from_months(2023).monthly_anchor_doys(), dtype=np.float64)
        x_out = np.array([1.0, 5.0, 10.0, 15.0], dtype=np.float64)
        result = linear_kernel(m, x_in, x_out, cyclic=False)
        assert np.allclose(result[:3], 10.0)

    def test_non_cyclic_linear_constant_after_last_anchor(self) -> None:
        """For t > x_in[-1] (last midpoint), output equals m[-1]."""
        m = np.array([10.0] * 11 + [99.0], dtype=np.float64)
        x_in = np.asarray(TemporalAxis.from_months(2023).monthly_anchor_doys(), dtype=np.float64)
        x_out = np.array([360.0, 361.0, 365.0], dtype=np.float64)
        result = linear_kernel(m, x_in, x_out, cyclic=False)
        assert np.allclose(result, 99.0)


# ---------------------------------------------------------------------------
# NaN policy behavior (REQ-008)
# ---------------------------------------------------------------------------


class TestLinearNanPolicy:
    """NaN propagation per REQ-008."""

    def test_all_nan_pixel_propagates_nan_to_all_days(
        self, monthly_3x3_all_nan_pixel: xr.DataArray
    ) -> None:
        interp = LinearInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_all_nan_pixel, axis).compute()
        nan_pixel = result.isel(y=1, x=1).values
        assert np.all(np.isnan(nan_pixel))
        valid_pixel = result.isel(y=0, x=0).values
        assert not np.any(np.isnan(valid_pixel))

    def test_partial_nan_with_raise_policy_raises(
        self, monthly_3x3_partial_nan: xr.DataArray
    ) -> None:
        interp = LinearInterpolator()
        axis = TemporalAxis.from_months(2023)
        with pytest.raises(PartialNanPixelError):
            interp.interpolate(monthly_3x3_partial_nan, axis, nan_policy="raise").compute()

    def test_partial_nan_with_propagate_all_returns_nan(
        self, monthly_3x3_partial_nan: xr.DataArray
    ) -> None:
        interp = LinearInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(
            monthly_3x3_partial_nan, axis, nan_policy="propagate_all"
        ).compute()
        partial_pixel = result.isel(y=0, x=0).values
        assert np.all(np.isnan(partial_pixel))

    def test_partial_nan_with_skip_pixel_interpolates_remaining(
        self, monthly_3x3_partial_nan: xr.DataArray
    ) -> None:
        interp = LinearInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(
            monthly_3x3_partial_nan, axis, nan_policy="skip_pixel"
        ).compute()
        partial_pixel = result.isel(y=0, x=0).values
        assert not np.any(np.isnan(partial_pixel))
