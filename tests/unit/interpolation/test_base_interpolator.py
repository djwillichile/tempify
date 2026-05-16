"""Tests for BaseInterpolator ABC and shared validations (tasks 1.6, 1.7)."""

from __future__ import annotations

from datetime import datetime
from typing import override

import numpy as np
import pytest
import xarray as xr

from tempify.interpolation.base import (
    BaseInterpolator,
    NanPolicy,
    TemporalAxis,
)
from tempify.interpolation.exceptions import (
    InvalidMonthlyStackError,
    UnsupportedCalendarError,
)


class _Dummy(BaseInterpolator):
    """Concrete dummy that always returns the input unchanged."""

    name = "dummy"

    @override
    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        *,
        cyclic: bool = True,
        nan_policy: NanPolicy = "raise",
        chunk_size: int | None = None,
    ) -> xr.DataArray:
        self._validate_month_count(source)
        self._validate_month_contiguity(source)
        self._validate_calendar(target_axis)
        self._validate_nan_policy(nan_policy)
        return self._postprocess(source, target_axis)


def _make_monthly(values: np.ndarray, months: list[int] | None = None) -> xr.DataArray:
    months = months if months is not None else list(range(1, 13))
    return xr.DataArray(values, dims=("month",), coords={"month": months})


def test_base_interpolator_is_abstract() -> None:
    with pytest.raises(TypeError, match="abstract"):
        BaseInterpolator()  # type: ignore[abstract]


def test_subclass_without_interpolate_raises() -> None:
    with pytest.raises(TypeError, match="abstract"):

        class Incomplete(BaseInterpolator):
            pass

        Incomplete()  # type: ignore[abstract]


def test_dummy_subclass_is_instantiable() -> None:
    assert isinstance(_Dummy(), BaseInterpolator)


def test_validate_month_count_rejects_non_12() -> None:
    interp = _Dummy()
    bad = _make_monthly(np.arange(11, dtype=float), months=list(range(1, 12)))
    with pytest.raises(InvalidMonthlyStackError):
        interp.interpolate(bad, TemporalAxis.from_months(2023))


def test_validate_month_count_rejects_missing_month_dim() -> None:
    interp = _Dummy()
    bad = xr.DataArray(np.arange(12, dtype=float), dims=("time",))
    with pytest.raises(InvalidMonthlyStackError):
        interp.interpolate(bad, TemporalAxis.from_months(2023))


def test_validate_month_contiguity_rejects_gaps() -> None:
    interp = _Dummy()
    bad = _make_monthly(
        np.arange(12, dtype=float),
        months=[1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    )
    with pytest.raises(InvalidMonthlyStackError, match="coord 'month'"):
        interp.interpolate(bad, TemporalAxis.from_months(2023))


def test_validate_calendar_rejects_non_gregorian() -> None:
    with pytest.raises(UnsupportedCalendarError):
        TemporalAxis(
            start=datetime(2023, 1, 1),
            end=datetime(2023, 12, 31),
            calendar="noleap",
        )


def test_validate_nan_policy_rejects_invalid_value() -> None:
    interp = _Dummy()
    good = _make_monthly(np.arange(12, dtype=float))
    with pytest.raises(ValueError, match="nan_policy"):
        interp.interpolate(good, TemporalAxis.from_months(2023), nan_policy="invalid")  # type: ignore[arg-type]


def test_postprocess_stamps_method_attr() -> None:
    interp = _Dummy()
    src = _make_monthly(np.arange(12, dtype=float))
    out = interp.interpolate(src, TemporalAxis.from_months(2023))
    assert out.attrs["tempify_method"] == "dummy"
    assert out.attrs["tempify_monthly_anchor"] == "midpoint"


def test_signature_has_keyword_only_options() -> None:
    """REQ-002: interpolate accepts cyclic, nan_policy, chunk_size as keyword-only."""
    interp = _Dummy()
    src = _make_monthly(np.arange(12, dtype=float))
    axis = TemporalAxis.from_months(2023)
    # These should work as keyword arguments
    interp.interpolate(src, axis, cyclic=False, nan_policy="propagate_all", chunk_size=256)
    # And not as positional after target_axis
    with pytest.raises(TypeError):
        interp.interpolate(src, axis, False)  # type: ignore[misc]
