"""Tests for climatological wraparound feature (REQ-015, REQ-016, REQ-017, ADR-0016)."""

from __future__ import annotations

import numpy as np
import pytest
import xarray as xr

from tempify.interpolation import (
    LinearInterpolator,
    PchipInterpolator,
    TemporalAxis,
)

# ---------------------------------------------------------------------------
# REQ-015: wraparound stamp on output
# ---------------------------------------------------------------------------


class TestWraparoundStampOnOutput:
    """The output attrs include the canonical wraparound mode."""

    def test_linear_default_stamps_climatological_2pt(
        self, monthly_3x3_smooth: xr.DataArray
    ) -> None:
        interp = LinearInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis)
        assert result.attrs["tempify_wraparound"] == "climatological_2pt"

    def test_pchip_default_stamps_climatological_4pt(
        self, monthly_3x3_smooth: xr.DataArray
    ) -> None:
        interp = PchipInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis)
        assert result.attrs["tempify_wraparound"] == "climatological_4pt"


# ---------------------------------------------------------------------------
# REQ-015: wraparound adds artificial nodes (numerically demonstrable)
# ---------------------------------------------------------------------------


class TestWraparoundAddsArtificialNodes:
    """Wraparound makes Dec-Jan transition smooth (low wrap diff)."""

    @pytest.fixture
    def step_input(self) -> xr.DataArray:
        """Step monthly input: m[0..5]=0, m[6..11]=10. Wraparound should smooth Dec-Jan."""
        values = np.array(
            [
                [[0.0]] * 6 + [[10.0]] * 6,
            ],
            dtype=np.float64,
        ).reshape(12, 1, 1)
        return xr.DataArray(
            values,
            dims=("month", "y", "x"),
            coords={"month": list(range(1, 13))},
        )

    def test_linear_wraparound_on_smooths_dec_jan(self, step_input: xr.DataArray) -> None:
        interp = LinearInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(step_input, axis, wraparound=True).compute()
        wrap_diff_on = abs(
            float(result.isel(time=0, y=0, x=0).values - result.isel(time=-1, y=0, x=0).values)
        )
        # With wraparound, the linear path between m[11]=10 and m[0]=0 crossing
        # Dec-Jan boundary creates a continuous slope: wrap diff is small.
        assert wrap_diff_on < 2.0

    def test_linear_wraparound_off_keeps_step_at_boundary(self, step_input: xr.DataArray) -> None:
        interp = LinearInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(step_input, axis, cyclic=False, wraparound=False).compute()
        # Without wraparound, output[0] = m[0] = 0 (constant extrap)
        # and output[-1] = m[11] = 10. So wrap diff is large.
        wrap_diff_off = abs(
            float(result.isel(time=0, y=0, x=0).values - result.isel(time=-1, y=0, x=0).values)
        )
        assert wrap_diff_off > 5.0


# ---------------------------------------------------------------------------
# REQ-016: wraparound=False disables extension
# ---------------------------------------------------------------------------


class TestWraparoundFalseDisablesExtension:
    """wraparound=False reverts to bare 12-point behavior."""

    def test_linear_wraparound_false_stamps_off(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = LinearInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis, cyclic=False, wraparound=False)
        assert result.attrs["tempify_wraparound"] == "off"

    def test_pchip_wraparound_false_stamps_off(self, monthly_3x3_smooth: xr.DataArray) -> None:
        interp = PchipInterpolator()
        axis = TemporalAxis.from_months(2023)
        result = interp.interpolate(monthly_3x3_smooth, axis, cyclic=False, wraparound=False)
        assert result.attrs["tempify_wraparound"] == "off"


# ---------------------------------------------------------------------------
# REQ-017: contradictory cyclic/wraparound raises
# ---------------------------------------------------------------------------


class TestContradictoryCyclicWraparoundRaises:
    """Mismatched cyclic / wraparound must raise ValueError."""

    @pytest.mark.parametrize(
        ("cyclic", "wraparound"),
        [(True, False), (False, True)],
    )
    def test_contradictory_values_raise(
        self,
        monthly_3x3_smooth: xr.DataArray,
        cyclic: bool,
        wraparound: bool,
    ) -> None:
        interp = LinearInterpolator()
        axis = TemporalAxis.from_months(2023)
        with pytest.raises(ValueError, match="cyclic and wraparound must agree"):
            interp.interpolate(monthly_3x3_smooth, axis, cyclic=cyclic, wraparound=wraparound)

    def test_wraparound_none_uses_cyclic(self, monthly_3x3_smooth: xr.DataArray) -> None:
        """wraparound=None (default) inherits cyclic value."""
        interp = LinearInterpolator()
        axis = TemporalAxis.from_months(2023)
        result_default = interp.interpolate(monthly_3x3_smooth, axis)
        result_explicit = interp.interpolate(monthly_3x3_smooth, axis, cyclic=True, wraparound=True)
        np.testing.assert_array_equal(
            result_default.compute().values, result_explicit.compute().values
        )
