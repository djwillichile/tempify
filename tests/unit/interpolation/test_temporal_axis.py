"""Tests for TemporalAxis and monthly_midpoint helper (tasks 1.3, 1.4, 1.4b)."""

from __future__ import annotations

from datetime import datetime

import pytest

from tempify.interpolation.base import TemporalAxis, monthly_midpoint
from tempify.interpolation.exceptions import UnsupportedCalendarError


class TestTemporalAxisConstruction:
    """task-1.3: basic construction and n_days."""

    def test_minimal_construction(self) -> None:
        axis = TemporalAxis(start=datetime(2023, 1, 1), end=datetime(2023, 12, 31))
        assert axis.freq == "daily"
        assert axis.calendar == "gregorian"
        assert axis.monthly_anchor == "midpoint"

    @pytest.mark.parametrize(
        ("year", "expected_days"),
        [(2023, 365), (2024, 366), (2100, 365), (2000, 366)],
    )
    def test_n_days_for_year(self, year: int, expected_days: int) -> None:
        axis = TemporalAxis(start=datetime(year, 1, 1), end=datetime(year, 12, 31))
        assert axis.n_days == expected_days

    def test_dataclass_is_frozen(self) -> None:
        axis = TemporalAxis(start=datetime(2023, 1, 1), end=datetime(2023, 12, 31))
        with pytest.raises((AttributeError, TypeError)):
            axis.start = datetime(2024, 1, 1)  # type: ignore[misc]

    def test_start_greater_than_end_raises(self) -> None:
        with pytest.raises(ValueError, match=r"start .* must be <= end"):
            TemporalAxis(start=datetime(2024, 1, 1), end=datetime(2023, 12, 31))

    def test_unsupported_calendar_raises(self) -> None:
        with pytest.raises(UnsupportedCalendarError):
            TemporalAxis(
                start=datetime(2023, 1, 1),
                end=datetime(2023, 12, 31),
                calendar="360_day",
            )


class TestMonthlyMidpointTable:
    """task-1.4: ADR-0015 canonical table verification."""

    @pytest.mark.parametrize(
        ("month", "expected_day"),
        [
            (1, 16),  # January 31d
            (2, 14),  # February common 28d
            (3, 16),  # March 31d
            (4, 15),  # April 30d
            (5, 16),
            (6, 15),
            (7, 16),
            (8, 16),
            (9, 15),
            (10, 16),
            (11, 15),
            (12, 16),
        ],
    )
    def test_monthly_midpoint_canonical_table_2023(self, month: int, expected_day: int) -> None:
        """Non-leap year (2023) matches ADR-0015 table exactly."""
        result = monthly_midpoint(2023, month)
        assert result == datetime(2023, month, expected_day)

    def test_february_midpoint_2024_is_day_15(self) -> None:
        """Leap year February has 29 days, midpoint = day 15 per ADR-0015."""
        assert monthly_midpoint(2024, 2) == datetime(2024, 2, 15)

    @pytest.mark.parametrize("month", [0, 13, -1, 100])
    def test_invalid_month_raises(self, month: int) -> None:
        with pytest.raises(ValueError, match="month must be in"):
            monthly_midpoint(2023, month)


class TestTemporalAxisFromMonths:
    """task-1.4: from_months factory."""

    def test_from_months_default_midpoint_anchor(self) -> None:
        axis = TemporalAxis.from_months(2023)
        assert axis.monthly_anchor == "midpoint"
        assert axis.start == datetime(2023, 1, 1)
        assert axis.end == datetime(2023, 12, 31)

    def test_to_datetime_index_has_n_days_entries(self) -> None:
        axis = TemporalAxis.from_months(2024)
        dts = axis.to_datetime_index()
        assert len(dts) == 366
        assert dts[0] == datetime(2024, 1, 1)
        assert dts[-1] == datetime(2024, 12, 31)


class TestMonthlyAnchorVariants:
    """task-1.4b: anchor start / end / custom variants (REQ-014)."""

    def test_anchor_start_returns_day_1(self) -> None:
        axis = TemporalAxis.from_months(2023, anchor="start")
        doys = axis.monthly_anchor_doys()
        assert doys[0] == 1  # 1 January
        assert doys[2] == 60  # 1 March (Jan 31 + Feb 28 + 1)

    def test_anchor_end_returns_last_day_of_month(self) -> None:
        axis = TemporalAxis.from_months(2023, anchor="end")
        doys = axis.monthly_anchor_doys()
        # 2023 is non-leap: Jan 31 -> doy 31, Dec 31 -> doy 365
        assert doys[0] == 31
        assert doys[-1] == 365

    def test_anchor_midpoint_uses_canonical_table(self) -> None:
        axis = TemporalAxis.from_months(2023, anchor="midpoint")
        doys = axis.monthly_anchor_doys()
        # January midpoint day 16 = DOY 16
        assert doys[0] == 16
        # February (28d) midpoint day 14 = DOY 31 + 14 = 45
        assert doys[1] == 45

    def test_custom_without_dates_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="requires custom_dates"):
            TemporalAxis.from_months(2023, anchor="custom")

    def test_custom_wrong_length_raises(self) -> None:
        with pytest.raises(ValueError, match="must have length 12"):
            TemporalAxis.from_months(
                2023,
                anchor="custom",
                custom_dates=[datetime(2023, m, 1) for m in range(1, 6)],
            )

    def test_custom_non_increasing_raises(self) -> None:
        bad = [datetime(2023, m, 1) for m in range(1, 13)]
        bad[5], bad[6] = bad[6], bad[5]  # swap to break order
        with pytest.raises(ValueError, match="strictly increasing"):
            TemporalAxis.from_months(2023, anchor="custom", custom_dates=bad)

    def test_custom_dates_without_custom_anchor_raises(self) -> None:
        good = [datetime(2023, m, 15) for m in range(1, 13)]
        with pytest.raises(ValueError, match="custom_dates can only be provided"):
            TemporalAxis(
                start=datetime(2023, 1, 1),
                end=datetime(2023, 12, 31),
                monthly_anchor="midpoint",
                custom_dates=good,
            )
