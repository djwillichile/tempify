"""Tests for PchipMeanPreservingInterpolator (Sub-fase 2.3, REQ-006, REQ-007)."""

from __future__ import annotations

import numpy as np
import pytest
import xarray as xr

from tempify.constants import DEFAULT_RM_CONVERGENCE_TOL
from tempify.interpolation import (
    PchipMeanPreservingInterpolator,
    TemporalAxis,
)
from tempify.interpolation._kernels import pchip_mp_kernel
from tempify.interpolation.exceptions import PartialNanPixelError

# ---------------------------------------------------------------------------
# Kernel tests
# ---------------------------------------------------------------------------


class TestPchipMpKernel:
    """Pure NumPy/SciPy mean-preserving kernel."""

    def _build_inputs(
        self, year: int = 2023
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        axis = TemporalAxis.from_months(year)
        x_in = np.asarray(axis.monthly_anchor_doys(), dtype=np.float64)
        x_out = np.arange(1, axis.n_days + 1, dtype=np.float64)
        day_to_month = np.asarray([d.month - 1 for d in axis.to_datetime_index()], dtype=np.int64)
        return x_in, x_out, day_to_month, x_in  # last is placeholder

    def test_constant_input_yields_constant_output(self) -> None:
        x_in, x_out, day_to_month, _ = self._build_inputs()
        m = np.full(12, 5.0, dtype=np.float64)
        daily, iters = pchip_mp_kernel(
            m,
            x_in,
            x_out,
            day_to_month,
            cyclic=True,
            convergence_tol=1e-12,
            max_iterations=50,
        )
        assert np.allclose(daily, 5.0, atol=1e-10)
        assert iters == 0  # baseline already constant

    def test_monthly_mean_preserved_after_iteration(self) -> None:
        """REQ-006: reconstructed monthly mean must match original within tol."""
        x_in, x_out, day_to_month, _ = self._build_inputs()
        m = np.array(
            [5.0, 6.0, 8.0, 12.0, 16.0, 20.0, 22.0, 21.0, 17.0, 13.0, 9.0, 6.0],
            dtype=np.float64,
        )
        daily, iters = pchip_mp_kernel(
            m,
            x_in,
            x_out,
            day_to_month,
            cyclic=True,
            convergence_tol=1e-9,
            max_iterations=50,
        )
        reconstructed = np.zeros(12)
        counts = np.zeros(12, dtype=np.int64)
        for i, mo in enumerate(day_to_month):
            reconstructed[mo] += daily[i]
            counts[mo] += 1
        reconstructed = reconstructed / counts
        assert np.max(np.abs(reconstructed - m)) < 1e-9
        assert iters >= 1

    def test_convergence_count_records_iterations(self) -> None:
        """REQ-007: number of iterations is tracked and returned."""
        x_in, x_out, day_to_month, _ = self._build_inputs()
        rng = np.random.default_rng(0)
        m = 15.0 + 5.0 * rng.standard_normal(12)
        _, iters = pchip_mp_kernel(
            m,
            x_in,
            x_out,
            day_to_month,
            cyclic=True,
            convergence_tol=DEFAULT_RM_CONVERGENCE_TOL,
            max_iterations=50,
        )
        assert iters >= 0
        assert iters <= 50


# ---------------------------------------------------------------------------
# Constructor validation
# ---------------------------------------------------------------------------


class TestPchipMpConstructor:
    """Defensive constructor validation."""

    def test_invalid_convergence_tol_raises(self) -> None:
        with pytest.raises(ValueError, match="convergence_tol must be positive"):
            PchipMeanPreservingInterpolator(convergence_tol=0.0)
        with pytest.raises(ValueError, match="convergence_tol must be positive"):
            PchipMeanPreservingInterpolator(convergence_tol=-1e-6)

    def test_invalid_max_iterations_raises(self) -> None:
        with pytest.raises(ValueError, match="max_iterations must be >= 1"):
            PchipMeanPreservingInterpolator(max_iterations=0)


# ---------------------------------------------------------------------------
# Facade
# ---------------------------------------------------------------------------


class TestPchipMpFacade:
    """Facade integration with xarray + Dask."""

    def test_pchip_mp_basic_on_smooth_fixture(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = PchipMeanPreservingInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis).compute()
        assert result.sizes["time"] == 365
        assert result.attrs["tempify_method"] == "pchip_mp"
        assert result.attrs["tempify_wraparound"] == "climatological_4pt"
        assert "rymes_myers_iterations_max" in result.attrs
        assert result.attrs["rymes_myers_convergence_tol"] == DEFAULT_RM_CONVERGENCE_TOL

    def test_lazy_dask_evaluation_preserved(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = PchipMeanPreservingInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis, chunk_size=2)
        assert hasattr(result.data, "dask")


# ---------------------------------------------------------------------------
# Mean preservation property (NFR-002)
# ---------------------------------------------------------------------------


class TestPchipMpMeanPreservation:
    """Monthly mean conservation via the facade (NFR-002)."""

    def test_monthly_mean_recovered_on_smooth_fixture(
        self, monthly_3x3_smooth: xr.DataArray
    ) -> None:
        interp = PchipMeanPreservingInterpolator(convergence_tol=1e-9)
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis).compute()
        # Build day-to-month for aggregation
        d2m = np.asarray([d.month for d in axis.to_datetime_index()], dtype=np.int64)
        for mo in range(1, 13):
            mask = d2m == mo
            recovered = result.isel(time=mask).mean(dim="time")
            original = monthly_3x3_smooth.isel(month=mo - 1)
            diff = float(np.max(np.abs(recovered.values - original.values)))
            assert diff < 1e-7


# ---------------------------------------------------------------------------
# Leap year
# ---------------------------------------------------------------------------


class TestPchipMpLeapYear:
    """Output day count varies with target year."""

    def test_output_has_365_days_in_non_leap_year(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = PchipMeanPreservingInterpolator()
        axis = TemporalAxis.from_months(2023)
        assert interp.interpolate(monthly_3x3_smooth, axis).sizes["time"] == 365

    def test_output_has_366_days_in_leap_year(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = PchipMeanPreservingInterpolator()
        axis = TemporalAxis.from_months(2024)
        assert interp.interpolate(monthly_3x3_smooth, axis).sizes["time"] == 366


# ---------------------------------------------------------------------------
# NaN policy
# ---------------------------------------------------------------------------


class TestPchipMpNanPolicy:
    """NaN propagation per REQ-008."""

    def test_all_nan_pixel_propagates_nan(self, monthly_3x3_all_nan_pixel: xr.DataArray) -> None:
        interp = PchipMeanPreservingInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_all_nan_pixel, axis).compute()
        assert np.all(np.isnan(result.isel(y=1, x=1).values))
        assert not np.any(np.isnan(result.isel(y=0, x=0).values))

    def test_partial_nan_with_raise_policy_raises(
        self, monthly_3x3_partial_nan: xr.DataArray
    ) -> None:
        interp = PchipMeanPreservingInterpolator()
        axis = TemporalAxis.from_months(2023)
        with pytest.raises(PartialNanPixelError):
            interp.interpolate(monthly_3x3_partial_nan, axis, nan_policy="raise").compute()

    def test_partial_nan_with_propagate_all_returns_nan(
        self, monthly_3x3_partial_nan: xr.DataArray
    ) -> None:
        interp = PchipMeanPreservingInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(
            monthly_3x3_partial_nan, axis, nan_policy="propagate_all"
        ).compute()
        assert np.all(np.isnan(result.isel(y=0, x=0).values))

    def test_partial_nan_with_skip_pixel_returns_nan(
        self, monthly_3x3_partial_nan: xr.DataArray
    ) -> None:
        """RM needs all 12 monthly anchors; skip_pixel propagates NaN per design."""
        interp = PchipMeanPreservingInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(
            monthly_3x3_partial_nan, axis, nan_policy="skip_pixel"
        ).compute()
        assert np.all(np.isnan(result.isel(y=0, x=0).values))
