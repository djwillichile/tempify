"""Tests for PostInterpolationValidator."""

from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr

from tempify.validation import PostInterpolationValidator
from tempify.validation._codes import (
    POST_CYCLIC_DISCONTINUITY,
    POST_MEAN_NOT_PRESERVED,
    POST_NAN_INTEGRITY_VIOLATION,
    POST_PHYSICAL_RANGE_VIOLATION,
)
from tempify.validation.profiles import VariableProfile
from tempify.validation.report import CheckSeverity


def test_mean_preservation_passes_for_step_replication(
    monthly_input_smooth: xr.DataArray,
    daily_output_from_monthly: xr.DataArray,
    temperature_profile: VariableProfile,
) -> None:
    validator = PostInterpolationValidator()
    report = validator.check(monthly_input_smooth, daily_output_from_monthly, temperature_profile)
    mean_check = next(c for c in report.checks if c.check_id == POST_MEAN_NOT_PRESERVED)
    assert mean_check.passed is True


def test_mean_preservation_warns_on_perturbation(
    monthly_input_smooth: xr.DataArray,
    daily_output_from_monthly: xr.DataArray,
    temperature_profile: VariableProfile,
) -> None:
    # Add a constant 10 to daily output: monthly aggregates diverge by 10
    perturbed = daily_output_from_monthly + 10.0
    perturbed.attrs.update(daily_output_from_monthly.attrs)
    # Force temperature_profile.acceptable_mean_error to be tighter than 10
    validator = PostInterpolationValidator(atol=1e-4)
    report = validator.check(monthly_input_smooth, perturbed, temperature_profile)
    mean_check = next(c for c in report.checks if c.check_id == POST_MEAN_NOT_PRESERVED)
    assert mean_check.passed is False
    assert mean_check.severity == CheckSeverity.WARN


def test_physical_range_violation_flagged(
    monthly_input_smooth: xr.DataArray,
    temperature_profile: VariableProfile,
) -> None:
    times = pd.date_range("2023-01-01", "2023-12-31", freq="D")
    bad = xr.DataArray(
        np.full((len(times), 3, 3), 999.0),  # outside [-90, 60]
        dims=("time", "y", "x"),
        coords={"time": times},
        name="tavg",
    )
    report = PostInterpolationValidator().check(monthly_input_smooth, bad, temperature_profile)
    range_check = next(c for c in report.checks if c.check_id == POST_PHYSICAL_RANGE_VIOLATION)
    assert range_check.passed is False


def test_cyclic_continuity_check_present(
    monthly_input_smooth: xr.DataArray,
    daily_output_from_monthly: xr.DataArray,
    temperature_profile: VariableProfile,
) -> None:
    report = PostInterpolationValidator().check(
        monthly_input_smooth, daily_output_from_monthly, temperature_profile
    )
    cyc = next(c for c in report.checks if c.check_id == POST_CYCLIC_DISCONTINUITY)
    assert cyc.severity in (CheckSeverity.INFO, CheckSeverity.WARN)


def test_nan_integrity_flagged_when_mismatch(
    monthly_input_smooth: xr.DataArray,
    daily_output_from_monthly: xr.DataArray,
    temperature_profile: VariableProfile,
) -> None:
    # Create a NaN pixel in input but not in output
    monthly_with_nan = monthly_input_smooth.copy()
    monthly_with_nan.loc[{"y": monthly_with_nan.y[0]}] = np.nan
    report = PostInterpolationValidator().check(
        monthly_with_nan, daily_output_from_monthly, temperature_profile
    )
    nan_check = next(c for c in report.checks if c.check_id == POST_NAN_INTEGRITY_VIOLATION)
    assert nan_check.passed is False
    assert nan_check.severity == CheckSeverity.ERROR
