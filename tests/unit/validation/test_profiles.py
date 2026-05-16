"""Tests for VariableProfile loading and matching."""

from __future__ import annotations

import pytest

from tempify.validation.errors import UnknownVariableProfileError
from tempify.validation.profiles import (
    VariableProfile,
    VariableProfileMatcher,
    iter_builtin_profiles,
)


def test_iter_builtin_profiles_yields_all_four() -> None:
    names = sorted(p.name for p in iter_builtin_profiles())
    assert "temperature" in names
    assert "precipitation" in names
    assert "relative_humidity" in names
    assert "solar_radiation" in names


def test_temperature_profile_has_expected_fields() -> None:
    matcher = VariableProfileMatcher()
    p = matcher.match("temperature")
    assert p.units == "degC"
    assert "linear" in p.allowed_methods
    assert "pchip_mp" in p.allowed_methods
    assert p.physical_min < 0 < p.physical_max


def test_precipitation_has_no_allowed_methods() -> None:
    matcher = VariableProfileMatcher()
    p = matcher.match("precipitation")
    assert p.allowed_methods == ()


def test_match_by_alias_case_insensitive() -> None:
    matcher = VariableProfileMatcher()
    assert matcher.match("Tavg").name == "temperature"
    assert matcher.match("PR").name == "precipitation"


def test_unknown_profile_raises() -> None:
    matcher = VariableProfileMatcher()
    with pytest.raises(UnknownVariableProfileError) as excinfo:
        matcher.match("does_not_exist")
    assert excinfo.value.name == "does_not_exist"
    assert "temperature" in excinfo.value.available


def test_from_dict_round_trip() -> None:
    payload = {
        "name": "foo",
        "canonical_name": "foo_canonical",
        "units": "m",
        "allowed_methods": ["linear", "pchip"],
        "physical_range": {"min": 0.0, "max": 10.0},
        "acceptable_mean_error": 1e-3,
        "aliases": ["f"],
        "description": "demo",
    }
    p = VariableProfile.from_dict(payload)
    assert p.name == "foo"
    assert p.allowed_methods == ("linear", "pchip")
    assert p.physical_min == 0.0
