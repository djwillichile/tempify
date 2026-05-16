"""Core abstractions for the temporal interpolation layer.

This module defines:

- :func:`monthly_midpoint`: the canonical midpoint helper per ADR-0015
  (CF Conventions 7.4).
- :class:`TemporalAxis`: the destination temporal coordinate with
  configurable anchor mode (``midpoint``, ``start``, ``end``, ``custom``).
- :class:`BaseInterpolator`: the abstract base class implemented by the
  four concrete interpolators (Linear, PCHIP, PCHIP+RM, Fourier).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from calendar import monthrange
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import ClassVar, Literal

import xarray as xr

from tempify.interpolation.exceptions import (
    InvalidMonthlyStackError,
    UnsupportedCalendarError,
)

SUPPORTED_CALENDARS: frozenset[str] = frozenset({"gregorian", "standard", "proleptic_gregorian"})
"""CF calendars accepted by v0.1.0 (per REQ-011)."""

NanPolicy = Literal["raise", "propagate_all", "skip_pixel"]
"""Behavior for pixels with partial NaN values."""

MonthlyAnchor = Literal["midpoint", "start", "end", "custom"]
"""Where on the month the input monthly value is placed on the X axis."""


def monthly_midpoint(year: int, month: int) -> datetime:
    """Return the canonical midpoint date of a calendar month.

    Per ADR-0015 / CF Conventions 7.4, an aggregated monthly value is
    placed at the centroid of its averaging period. The formula
    ``(days_in_month + 1) // 2`` reproduces the canonical table exactly:
    16 for 31-day months, 15 for 30-day months and 29-day February,
    14 for 28-day February.

    Parameters
    ----------
    year : int
        Gregorian year used for leap-year correction in February.
    month : int
        Calendar month, 1..12.

    Returns
    -------
    datetime
        Midnight on the canonical midpoint day.

    Raises
    ------
    ValueError
        If ``month`` is outside [1, 12].
    """
    if not 1 <= month <= 12:
        raise ValueError(f"month must be in [1, 12], got {month}")
    _, days_in_month = monthrange(year, month)
    midpoint_day = (days_in_month + 1) // 2
    return datetime(year, month, midpoint_day)


def _validate_custom_dates(dates: list[datetime]) -> None:
    """Validate a user-provided ``custom_dates`` list.

    Raises
    ------
    ValueError
        If the list does not have length 12 or is not strictly
        increasing.
    """
    if len(dates) != 12:
        raise ValueError(f"custom_dates must have length 12, got {len(dates)}")
    for i in range(1, len(dates)):
        if dates[i] <= dates[i - 1]:
            raise ValueError(
                "custom_dates must be strictly increasing; "
                f"dates[{i - 1}]={dates[i - 1]} not < dates[{i}]={dates[i]}"
            )


@dataclass(frozen=True, slots=True)
class TemporalAxis:
    """Target temporal coordinate for an interpolation.

    Parameters
    ----------
    start, end : datetime
        Inclusive bounds of the target axis.
    freq : Literal['daily']
        Target frequency. v0.1.0 only supports ``'daily'``.
    calendar : str
        CF calendar name. v0.1.0 only supports Gregorian variants.
    monthly_anchor : MonthlyAnchor
        Where to place each input monthly value on the X axis. Default
        ``'midpoint'`` (ADR-0015 / CF 7.4).
    custom_dates : list[datetime] | None
        Required when ``monthly_anchor='custom'``. Strictly increasing
        list of length 12.

    Raises
    ------
    ValueError
        If ``start > end``, or ``custom_dates`` invariants are violated.
    UnsupportedCalendarError
        If ``calendar`` is not one of the supported gregorian variants.
    """

    start: datetime
    end: datetime
    freq: Literal["daily"] = "daily"
    calendar: str = "gregorian"
    monthly_anchor: MonthlyAnchor = "midpoint"
    custom_dates: list[datetime] | None = None

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError(f"start ({self.start}) must be <= end ({self.end})")
        if self.calendar not in SUPPORTED_CALENDARS:
            raise UnsupportedCalendarError(self.calendar)
        if self.monthly_anchor == "custom":
            if self.custom_dates is None:
                raise ValueError("monthly_anchor='custom' requires custom_dates to be provided")
            _validate_custom_dates(self.custom_dates)
        elif self.custom_dates is not None:
            raise ValueError(
                "custom_dates can only be provided when monthly_anchor='custom', "
                f"got monthly_anchor={self.monthly_anchor!r}"
            )

    @classmethod
    def from_months(
        cls,
        year: int,
        anchor: MonthlyAnchor = "midpoint",
        custom_dates: list[datetime] | None = None,
    ) -> TemporalAxis:
        """Build a daily target axis for one calendar year (ADR-0015 defaults)."""
        return cls(
            start=datetime(year, 1, 1),
            end=datetime(year, 12, 31),
            freq="daily",
            calendar="gregorian",
            monthly_anchor=anchor,
            custom_dates=custom_dates,
        )

    @property
    def n_days(self) -> int:
        """Number of daily steps from ``start`` to ``end`` inclusive."""
        return (self.end.date() - self.start.date()).days + 1

    def monthly_anchor_doys(self) -> list[int]:
        """Day-of-year for each of the 12 monthly anchor positions."""
        year = self.start.year
        anchors: list[datetime]
        if self.monthly_anchor == "midpoint":
            anchors = [monthly_midpoint(year, m) for m in range(1, 13)]
        elif self.monthly_anchor == "start":
            anchors = [datetime(year, m, 1) for m in range(1, 13)]
        elif self.monthly_anchor == "end":
            anchors = [datetime(year, m, monthrange(year, m)[1]) for m in range(1, 13)]
        else:  # custom
            assert self.custom_dates is not None  # validated in __post_init__
            anchors = self.custom_dates
        return [d.timetuple().tm_yday for d in anchors]

    def to_datetime_index(self) -> list[datetime]:
        """Return a list of daily datetimes from ``start`` to ``end`` inclusive."""
        return [self.start + timedelta(days=i) for i in range(self.n_days)]


class BaseInterpolator(ABC):
    """Common interface and shared validations for all temporal interpolators."""

    name: ClassVar[str] = "base"
    wraparound_stamp_on: ClassVar[str] = "climatological_2pt"
    """Value of ``attrs['tempify_wraparound']`` when wraparound is active.

    Subclasses override this to declare how much padding they use:
    ``climatological_2pt`` for Linear (1 node per side, 14 effective),
    ``climatological_4pt`` for PCHIP family (2 nodes per side, 16 effective),
    ``fft_implicit`` for Fourier (no explicit padding, FFT-periodic).
    """

    @abstractmethod
    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        *,
        cyclic: bool = True,
        wraparound: bool | None = None,
        nan_policy: NanPolicy = "raise",
        chunk_size: int | None = None,
    ) -> xr.DataArray:
        """Interpolate ``source`` onto ``target_axis``.

        Parameters
        ----------
        source : xarray.DataArray
            Input array with a monthly temporal dimension named ``month``
            with coordinate values ``1..12``.
        target_axis : TemporalAxis
            Destination temporal coordinate.
        cyclic : bool, default True
            Retro-compatible synonym of ``wraparound`` (per REQ-017 and
            ADR-0016). Will be deprecated in v0.2.0 in favor of
            ``wraparound``. If True, treat December and January as
            adjacent in the interpolation (per REQ-004). If False, apply
            method-specific extrapolation (per REQ-005a/b/c).
        wraparound : bool | None, default None
            When not ``None``, must equal ``cyclic`` (per REQ-017) else
            raises ``ValueError``. When ``None`` (default), the value of
            ``cyclic`` is used. Controls whether climatological wraparound
            is active (per REQ-015 / ADR-0016).
        nan_policy : Literal['raise', 'propagate_all', 'skip_pixel']
            Behavior for pixels with partial NaN values (per REQ-008).
        chunk_size : int | None
            Override default Dask chunk size for spatial dims.
        """

    def _validate_month_count(self, source: xr.DataArray) -> None:
        """Raise InvalidMonthlyStackError if ``source`` lacks 12 months."""
        if "month" not in source.dims:
            raise InvalidMonthlyStackError(
                n_months=0,
                reason="el DataArray no tiene dimensión 'month'",
            )
        n_months = int(source.sizes["month"])
        if n_months != 12:
            raise InvalidMonthlyStackError(n_months=n_months)

    def _validate_month_contiguity(self, source: xr.DataArray) -> None:
        """Raise InvalidMonthlyStackError if the month coord is not 1..12 in order."""
        if "month" not in source.coords:
            return
        values = [int(v) for v in source.coords["month"].values]
        expected = list(range(1, 13))
        if values != expected:
            raise InvalidMonthlyStackError(
                n_months=len(values),
                reason=f"coord 'month' = {values}, se esperaba {expected}",
            )

    def _validate_calendar(self, target_axis: TemporalAxis) -> None:
        """Raise UnsupportedCalendarError if the target calendar is not Gregorian."""
        if target_axis.calendar not in SUPPORTED_CALENDARS:
            raise UnsupportedCalendarError(target_axis.calendar)

    def _validate_nan_policy(self, nan_policy: NanPolicy) -> None:
        """Raise ValueError if ``nan_policy`` is not one of the accepted literals."""
        allowed: tuple[NanPolicy, ...] = ("raise", "propagate_all", "skip_pixel")
        if nan_policy not in allowed:
            raise ValueError(f"nan_policy must be one of {allowed}, got {nan_policy!r}")

    def _resolve_wraparound(self, cyclic: bool, wraparound: bool | None) -> bool:
        """Resolve cyclic/wraparound consistency per REQ-017 and ADR-0016."""
        if wraparound is None:
            return cyclic
        if wraparound != cyclic:
            raise ValueError(
                "cyclic and wraparound must agree; in v0.2.0 cyclic will be "
                f"deprecated in favor of wraparound. Got cyclic={cyclic}, "
                f"wraparound={wraparound}."
            )
        return wraparound

    def _postprocess(
        self,
        result: xr.DataArray,
        target_axis: TemporalAxis,
        wraparound: bool = True,
    ) -> xr.DataArray:
        """Attach standard provenance attributes to the interpolated DataArray.

        Adds ``tempify_method`` (the interpolator class name),
        ``tempify_monthly_anchor`` (the anchor convention used), and
        ``tempify_wraparound`` (climatological wraparound mode per ADR-0016).
        Concrete interpolators may attach additional attributes specific
        to their method (e.g., ``rymes_myers_iterations`` per REQ-007).
        """
        out = result.copy()
        out.attrs["tempify_method"] = self.name
        out.attrs["tempify_monthly_anchor"] = target_axis.monthly_anchor
        out.attrs["tempify_wraparound"] = self.wraparound_stamp_on if wraparound else "off"
        return out
