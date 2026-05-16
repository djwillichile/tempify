"""Tests for FourierInterpolator (Sub-fase 2.4)."""

from __future__ import annotations

import numpy as np
import pytest
import xarray as xr

from tempify.interpolation import FourierInterpolator, TemporalAxis
from tempify.interpolation._kernels import fourier_kernel
from tempify.interpolation.exceptions import PartialNanPixelError

# ---------------------------------------------------------------------------
# Kernel tests
# ---------------------------------------------------------------------------


class TestFourierKernel:
    """Pure NumPy FFT-based kernel correctness."""

    def test_constant_input_yields_constant_output(self) -> None:
        m = np.full(12, 7.5, dtype=np.float64)
        x_in = np.asarray(TemporalAxis.from_months(2023).monthly_anchor_doys(), dtype=np.float64)
        x_out = np.arange(1, 366, dtype=np.float64)
        result = fourier_kernel(m, x_in, x_out, n_harmonics=3)
        assert np.allclose(result, 7.5, atol=1e-10)

    def test_single_harmonic_sinusoid_recovered(self) -> None:
        """A pure cosine of period 12 is recovered nearly exactly with 1+ harmonics."""
        months = np.arange(12, dtype=np.float64)
        amp = 10.0
        m = amp * np.cos(2 * np.pi * months / 12.0)
        x_in = months + 0.5  # treat midpoint as approximate
        x_out = np.linspace(0.5, 11.5, 12)
        result = fourier_kernel(m, x_in, x_out, n_harmonics=2)
        assert np.max(np.abs(result - m)) < 1e-9


# ---------------------------------------------------------------------------
# Constructor validation
# ---------------------------------------------------------------------------


class TestFourierConstructorValidation:
    """n_harmonics must be in [1, 5]."""

    @pytest.mark.parametrize("bad", [0, -1, 6, 100])
    def test_invalid_n_harmonics_raises(self, bad: int) -> None:
        with pytest.raises(ValueError, match="n_harmonics must be in"):
            FourierInterpolator(n_harmonics=bad)

    @pytest.mark.parametrize("good", [1, 2, 3, 4, 5])
    def test_valid_n_harmonics_accepted(self, good: int) -> None:
        interp = FourierInterpolator(n_harmonics=good)
        assert interp.n_harmonics == good


# ---------------------------------------------------------------------------
# Facade
# ---------------------------------------------------------------------------


class TestFourierFacade:
    """Facade integration with xarray + Dask."""

    def test_fourier_basic_on_smooth_fixture(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = FourierInterpolator(n_harmonics=3)
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis)
        assert result.sizes["time"] == 365
        assert result.sizes["y"] == 3
        assert result.sizes["x"] == 3
        assert result.attrs["tempify_method"] == "fourier"
        assert result.attrs["tempify_wraparound"] == "fft_implicit"
        assert result.attrs["tempify_n_harmonics"] == 3

    def test_lazy_dask_evaluation_preserved(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = FourierInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis, chunk_size=2)
        assert hasattr(result.data, "dask")


# ---------------------------------------------------------------------------
# Leap year handling
# ---------------------------------------------------------------------------


class TestFourierLeapYear:
    """Output day count varies with target year."""

    def test_output_has_365_days_in_non_leap_year(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = FourierInterpolator()
        axis = TemporalAxis.from_months(2023)
        assert interp.interpolate(monthly_3x3_smooth, axis).sizes["time"] == 365

    def test_output_has_366_days_in_leap_year(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = FourierInterpolator()
        axis = TemporalAxis.from_months(2024)
        assert interp.interpolate(monthly_3x3_smooth, axis).sizes["time"] == 366


# ---------------------------------------------------------------------------
# Cyclic continuity (built-in by FFT)
# ---------------------------------------------------------------------------


class TestFourierCyclicContinuity:
    """Fourier output is periodic by construction."""

    def test_first_and_last_day_match_within_period_jitter(self) -> None:
        x_in = np.asarray(TemporalAxis.from_months(2023).monthly_anchor_doys(), dtype=np.float64)
        period = 365.0
        m = 10.0 * np.sin(2 * np.pi * (x_in - 1) / period)
        x_out = np.arange(1, 366, dtype=np.float64)
        result = fourier_kernel(m, x_in, x_out, n_harmonics=3)
        wrap_diff = abs(result[0] - result[-1])
        assert wrap_diff < 1.0


# ---------------------------------------------------------------------------
# NaN policy
# ---------------------------------------------------------------------------


class TestFourierNanPolicy:
    """NaN propagation per REQ-008."""

    def test_all_nan_pixel_propagates_nan_to_all_days(
        self, monthly_3x3_all_nan_pixel: xr.DataArray
    ) -> None:
        interp = FourierInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_all_nan_pixel, axis).compute()
        assert np.all(np.isnan(result.isel(y=1, x=1).values))
        assert not np.any(np.isnan(result.isel(y=0, x=0).values))

    def test_partial_nan_with_raise_policy_raises(
        self, monthly_3x3_partial_nan: xr.DataArray
    ) -> None:
        interp = FourierInterpolator()
        axis = TemporalAxis.from_months(2023)
        with pytest.raises(PartialNanPixelError):
            interp.interpolate(monthly_3x3_partial_nan, axis, nan_policy="raise").compute()

    def test_partial_nan_with_propagate_all_returns_nan(
        self, monthly_3x3_partial_nan: xr.DataArray
    ) -> None:
        interp = FourierInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(
            monthly_3x3_partial_nan, axis, nan_policy="propagate_all"
        ).compute()
        assert np.all(np.isnan(result.isel(y=0, x=0).values))

    def test_partial_nan_with_skip_pixel_returns_nan_for_fourier(
        self, monthly_3x3_partial_nan: xr.DataArray
    ) -> None:
        """Fourier cannot honestly skip NaN samples (FFT requires full 12)."""
        interp = FourierInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(
            monthly_3x3_partial_nan, axis, nan_policy="skip_pixel"
        ).compute()
        assert np.all(np.isnan(result.isel(y=0, x=0).values))
