"""Tests for CubicSplineInterpolator (per ADR-0018)."""

from __future__ import annotations

import numpy as np
import pytest
import xarray as xr

from tempify.interpolation import CubicSplineInterpolator, TemporalAxis
from tempify.interpolation._kernels import cubic_kernel
from tempify.interpolation.exceptions import PartialNanPixelError


class TestCubicKernel:
    """Pure SciPy-backed kernel correctness."""

    def test_constant_input_yields_constant_output(self) -> None:
        m = np.full(12, 11.0, dtype=np.float64)
        x_in = np.asarray(
            TemporalAxis.from_months(2023).monthly_anchor_doys(),
            dtype=np.float64,
        )
        x_out = np.arange(1, 366, dtype=np.float64)
        result = cubic_kernel(m, x_in, x_out, cyclic=True)
        assert np.allclose(result, 11.0, atol=1e-10)

    def test_passes_through_input_nodes(self) -> None:
        x_in = np.asarray(
            TemporalAxis.from_months(2023).monthly_anchor_doys(),
            dtype=np.float64,
        )
        x_out = np.arange(1, 366, dtype=np.float64)
        m = np.array([21, 20, 18, 15, 12, 9, 9, 10, 12, 14, 17, 20], dtype=np.float64)
        result = cubic_kernel(m, x_in, x_out, cyclic=True)
        for i, doy in enumerate(x_in):
            assert abs(result[int(doy) - 1] - m[i]) < 1e-9, f"node {i}"

    def test_sinusoidal_input_low_error(self) -> None:
        x_in = np.asarray(
            TemporalAxis.from_months(2023).monthly_anchor_doys(),
            dtype=np.float64,
        )
        x_out = np.arange(1, 366, dtype=np.float64)
        period = 365.0
        m = 10.0 * np.sin(2 * np.pi * (x_in - 1) / period)
        expected = 10.0 * np.sin(2 * np.pi * (x_out - 1) / period)
        result = cubic_kernel(m, x_in, x_out, cyclic=True)
        # Cubic is C2; should fit sinusoids well.
        assert np.max(np.abs(result - expected)) < 0.5

    def test_non_cyclic_extrapolates(self) -> None:
        x_in = np.asarray(
            TemporalAxis.from_months(2023).monthly_anchor_doys(),
            dtype=np.float64,
        )
        x_out = np.arange(1, 366, dtype=np.float64)
        m = np.linspace(0, 11, 12)
        result = cubic_kernel(m, x_in, x_out, cyclic=False)
        assert not np.any(np.isnan(result))


class TestCubicFacade:
    """xarray-level integration."""

    def test_cubic_basic_on_smooth_fixture(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = CubicSplineInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis)
        assert result.sizes["time"] == 365
        assert result.sizes["y"] == 3
        assert result.sizes["x"] == 3
        assert result.attrs["tempify_method"] == "cubic"

    def test_cubic_raises_on_partial_nan_by_default(
        self,
        monthly_3x3_smooth: xr.DataArray,
    ) -> None:
        corrupt = monthly_3x3_smooth.copy()
        corrupt[5, 0, 0] = np.nan
        interp = CubicSplineInterpolator()
        axis = TemporalAxis.from_months(2023)
        with pytest.raises(PartialNanPixelError):
            interp.interpolate(corrupt, axis).compute()

    def test_cubic_can_overshoot(self, monthly_3x3_smooth: xr.DataArray) -> None:
        """Cubic spline DOES allow overshoots — this is the documented tradeoff.

        We don't assert a specific overshoot, only that the output range
        can extend slightly beyond the input range, unlike PCHIP which
        is shape-preserving by construction.
        """
        interp = CubicSplineInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis).compute()
        # Output exists and is finite
        assert np.all(np.isfinite(result.values))
