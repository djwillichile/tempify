"""Tests for AkimaInterpolator (per ADR-0018)."""

from __future__ import annotations

import numpy as np
import pytest
import xarray as xr

from tempify.interpolation import AkimaInterpolator, TemporalAxis
from tempify.interpolation._kernels import akima_kernel
from tempify.interpolation.exceptions import PartialNanPixelError


class TestAkimaKernel:
    """Pure SciPy-backed kernel correctness."""

    def test_constant_input_yields_constant_output(self) -> None:
        m = np.full(12, 9.0, dtype=np.float64)
        x_in = np.asarray(
            TemporalAxis.from_months(2023).monthly_anchor_doys(),
            dtype=np.float64,
        )
        x_out = np.arange(1, 366, dtype=np.float64)
        result = akima_kernel(m, x_in, x_out, cyclic=True)
        assert np.allclose(result, 9.0, atol=1e-10)

    def test_passes_through_input_nodes(self) -> None:
        """Akima must pass exactly through the input nodes."""
        x_in = np.asarray(
            TemporalAxis.from_months(2023).monthly_anchor_doys(),
            dtype=np.float64,
        )
        x_out = np.arange(1, 366, dtype=np.float64)
        m = np.array([21, 20, 18, 15, 12, 9, 9, 10, 12, 14, 17, 20], dtype=np.float64)
        result = akima_kernel(m, x_in, x_out, cyclic=True)
        # Sample at each anchor and compare
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
        result = akima_kernel(m, x_in, x_out, cyclic=True)
        # Akima is less aggressive than PCHIP at flattening peaks;
        # tolerance can be a bit looser than the 0.5 used for PCHIP.
        assert np.max(np.abs(result - expected)) < 1.0

    def test_non_cyclic_extrapolates(self) -> None:
        x_in = np.asarray(
            TemporalAxis.from_months(2023).monthly_anchor_doys(),
            dtype=np.float64,
        )
        x_out = np.arange(1, 366, dtype=np.float64)
        m = np.linspace(0, 11, 12)
        result = akima_kernel(m, x_in, x_out, cyclic=False)
        assert not np.any(np.isnan(result)), "non-cyclic must extrapolate, not nan"


class TestAkimaFacade:
    """xarray-level integration."""

    def test_akima_basic_on_smooth_fixture(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = AkimaInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis)
        assert result.sizes["time"] == 365
        assert result.sizes["y"] == 3
        assert result.sizes["x"] == 3
        assert result.attrs["tempify_method"] == "akima"

    def test_akima_raises_on_partial_nan_by_default(
        self,
        monthly_3x3_smooth: xr.DataArray,
    ) -> None:
        corrupt = monthly_3x3_smooth.copy()
        corrupt[0, 1, 1] = np.nan
        interp = AkimaInterpolator()
        axis = TemporalAxis.from_months(2023)
        with pytest.raises(PartialNanPixelError):
            interp.interpolate(corrupt, axis).compute()

    def test_akima_propagates_all_under_policy(
        self,
        monthly_3x3_smooth: xr.DataArray,
    ) -> None:
        corrupt = monthly_3x3_smooth.copy()
        corrupt[0, 1, 1] = np.nan
        interp = AkimaInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(corrupt, axis, nan_policy="propagate_all").compute()
        # The corrupted pixel is fully NaN.
        assert np.all(np.isnan(result.isel(y=1, x=1).values))
        # Neighbors are finite.
        assert np.all(np.isfinite(result.isel(y=0, x=0).values))
