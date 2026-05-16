"""Tests for MethodVariableCompatibilityChecker."""

from __future__ import annotations

import pytest

from tempify.validation import (
    MethodVariableCompatibilityChecker,
    MethodVariableIncompatibilityError,
)
from tempify.validation._codes import (
    COMPAT_FORCE_OVERRIDE_USED,
    COMPAT_METHOD_NOT_ALLOWED,
    COMPAT_PRECIPITATION_SMOOTH,
)
from tempify.validation.profiles import VariableProfile
from tempify.validation.report import CheckSeverity


def test_allowed_method_passes(temperature_profile: VariableProfile) -> None:
    result = MethodVariableCompatibilityChecker().check("pchip_mp", temperature_profile)
    assert result.passed is True
    assert result.severity == CheckSeverity.INFO
    assert result.check_id == COMPAT_METHOD_NOT_ALLOWED


def test_disallowed_method_raises(precipitation_profile: VariableProfile) -> None:
    checker = MethodVariableCompatibilityChecker()
    with pytest.raises(MethodVariableIncompatibilityError) as excinfo:
        checker.check("linear", precipitation_profile)
    assert excinfo.value.method == "linear"
    assert excinfo.value.variable == "precipitation"


def test_force_override_returns_warn_for_precipitation(
    precipitation_profile: VariableProfile,
) -> None:
    result = MethodVariableCompatibilityChecker().check(
        "pchip_mp", precipitation_profile, force=True
    )
    assert result.severity == CheckSeverity.WARN
    assert result.check_id == COMPAT_PRECIPITATION_SMOOTH
    assert result.details["force_method_used"] is True


def test_force_override_for_non_precipitation_uses_compat003(
    temperature_profile: VariableProfile,
) -> None:
    # Use an unsupported method (e.g., 'spline' is not in temperature.allowed)
    profile = VariableProfile(
        name=temperature_profile.name,
        canonical_name=temperature_profile.canonical_name,
        units=temperature_profile.units,
        allowed_methods=("linear",),  # restrict
        physical_min=temperature_profile.physical_min,
        physical_max=temperature_profile.physical_max,
        acceptable_mean_error=temperature_profile.acceptable_mean_error,
        aliases=temperature_profile.aliases,
    )
    result = MethodVariableCompatibilityChecker().check("fourier", profile, force=True)
    assert result.severity == CheckSeverity.WARN
    assert result.check_id == COMPAT_FORCE_OVERRIDE_USED
