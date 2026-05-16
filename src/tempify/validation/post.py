"""Post-interpolation validator.

Verifies monthly mean preservation, cyclic continuity at the Dec-Jan
boundary, physical range conformance, and NaN integrity. Per the
policy "fail-fast pre, warn-and-continue post", failures here emit
``WARN`` severity but do not abort the pipeline.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import xarray as xr

from tempify.validation._codes import (
    POST_CYCLIC_DISCONTINUITY,
    POST_MEAN_NOT_PRESERVED,
    POST_NAN_INTEGRITY_VIOLATION,
    POST_PHYSICAL_RANGE_VIOLATION,
)
from tempify.validation.profiles import VariableProfile
from tempify.validation.report import (
    CheckPhase,
    CheckResult,
    CheckSeverity,
    ValidationReport,
)

DEFAULT_POST_ATOL: Final[float] = 1e-4
"""Contractual post-validator atol per ADR-0010 nivel 2."""

DEFAULT_POST_RTOL: Final[float] = 1e-6
"""Contractual post-validator rtol per ADR-0010 nivel 2."""

CYCLIC_DISCONTINUITY_FACTOR: Final[float] = 3.0
"""Multiplier of the monthly std used as discontinuity threshold."""


class PostInterpolationValidator:
    """Run post-process checks on the interpolated daily output."""

    def __init__(
        self,
        atol: float | None = None,
        rtol: float | None = None,
    ) -> None:
        self.atol = atol if atol is not None else DEFAULT_POST_ATOL
        self.rtol = rtol if rtol is not None else DEFAULT_POST_RTOL

    def check(
        self,
        monthly_input: xr.DataArray,
        daily_output: xr.DataArray,
        profile: VariableProfile,
    ) -> ValidationReport:
        """Run all post-interpolation checks on ``daily_output``."""
        checks: list[CheckResult] = [
            self._check_mean_preservation(monthly_input, daily_output, profile),
            self._check_cyclic_continuity(daily_output),
            self._check_physical_range(daily_output, profile),
            self._check_nan_integrity(monthly_input, daily_output),
        ]
        return ValidationReport(checks=tuple(checks))

    def _aggregate_to_monthly(self, daily: xr.DataArray) -> xr.DataArray:
        if "time" not in daily.dims:
            raise ValueError("daily output must have a 'time' dimension")
        # Build a month index per day from the time coord
        if not hasattr(daily.coords["time"], "dt"):
            raise ValueError("time coordinate must be datetime-like")
        return daily.groupby(daily["time"].dt.month).mean(dim="time")

    def _check_mean_preservation(
        self,
        monthly_input: xr.DataArray,
        daily_output: xr.DataArray,
        profile: VariableProfile,
    ) -> CheckResult:
        atol = float(min(self.atol, profile.acceptable_mean_error))
        agg = self._aggregate_to_monthly(daily_output)
        diff = float(np.nanmax(np.abs(agg.values - monthly_input.values)))
        ok = bool(np.isfinite(diff)) and (
            diff <= atol + self.rtol * float(np.nanmax(np.abs(monthly_input.values)))
        )
        return CheckResult(
            check_id=POST_MEAN_NOT_PRESERVED,
            name="Monthly mean preservation",
            severity=CheckSeverity.INFO if ok else CheckSeverity.WARN,
            phase=CheckPhase.POST_PROCESS,
            passed=ok,
            message=(
                f"Diferencia máxima entre media reconstruida y original: {diff:.3e} "
                f"(tolerancia efectiva: {atol:.3e})"
            ),
            details={
                "max_abs_diff": diff,
                "atol_used": atol,
                "rtol_used": self.rtol,
            },
        )

    def _check_cyclic_continuity(self, daily: xr.DataArray) -> CheckResult:
        if "time" not in daily.dims:
            return CheckResult(
                check_id=POST_CYCLIC_DISCONTINUITY,
                name="Cyclic continuity (Dec-Jan)",
                severity=CheckSeverity.INFO,
                phase=CheckPhase.POST_PROCESS,
                passed=True,
                message="No aplica: output sin dimensión 'time'.",
            )
        first = float(np.nanmean(daily.isel(time=0).values))
        last = float(np.nanmean(daily.isel(time=-1).values))
        wrap_diff = abs(last - first)
        # Use the daily series std as a scale
        std = float(np.nanstd(daily.values))
        threshold = CYCLIC_DISCONTINUITY_FACTOR * std if std > 0 else float("inf")
        ok = wrap_diff <= threshold
        return CheckResult(
            check_id=POST_CYCLIC_DISCONTINUITY,
            name="Cyclic continuity (Dec-Jan)",
            severity=CheckSeverity.INFO if ok else CheckSeverity.WARN,
            phase=CheckPhase.POST_PROCESS,
            passed=ok,
            message=(
                f"Diferencia entre el primer y último día: {wrap_diff:.3e} "
                f"(umbral: {threshold:.3e})"
            ),
            details={
                "wrap_diff": wrap_diff,
                "series_std": std,
                "threshold": threshold,
            },
        )

    def _check_physical_range(self, daily: xr.DataArray, profile: VariableProfile) -> CheckResult:
        finite = np.isfinite(daily.values)
        if not finite.any():
            return CheckResult(
                check_id=POST_PHYSICAL_RANGE_VIOLATION,
                name="Physical range",
                severity=CheckSeverity.INFO,
                phase=CheckPhase.POST_PROCESS,
                passed=True,
                message="No aplica: output es todo NaN.",
            )
        finite_vals = daily.values[finite]
        min_v = float(np.min(finite_vals))
        max_v = float(np.max(finite_vals))
        below = int((finite_vals < profile.physical_min).sum())
        above = int((finite_vals > profile.physical_max).sum())
        ok = below == 0 and above == 0
        return CheckResult(
            check_id=POST_PHYSICAL_RANGE_VIOLATION,
            name="Physical range",
            severity=CheckSeverity.INFO if ok else CheckSeverity.WARN,
            phase=CheckPhase.POST_PROCESS,
            passed=ok,
            message=(
                f"Rango observado [{min_v:.3f}, {max_v:.3f}] vs físico "
                f"[{profile.physical_min}, {profile.physical_max}]; "
                f"{int(below + above)} píxeles-día fuera de rango."
            ),
            details={
                "observed_min": min_v,
                "observed_max": max_v,
                "below_count": int(below),
                "above_count": int(above),
                "physical_min": profile.physical_min,
                "physical_max": profile.physical_max,
            },
        )

    def _check_nan_integrity(
        self, monthly_input: xr.DataArray, daily_output: xr.DataArray
    ) -> CheckResult:
        """A pixel that was all-NaN in input must be all-NaN in output (and vice versa)."""
        # Identify spatial mask of fully-NaN input pixels (month dim is collapsed)
        if "month" not in monthly_input.dims or "time" not in daily_output.dims:
            return CheckResult(
                check_id=POST_NAN_INTEGRITY_VIOLATION,
                name="NaN integrity",
                severity=CheckSeverity.INFO,
                phase=CheckPhase.POST_PROCESS,
                passed=True,
                message="No aplica: dimensiones inesperadas.",
            )
        nan_input_pixels = monthly_input.isnull().all(dim="month")
        # In output: a pixel is "all-NaN" if every time step is NaN
        nan_output_pixels = daily_output.isnull().all(dim="time")
        try:
            mismatch = (nan_input_pixels != nan_output_pixels).sum()
            n_mismatch = int(mismatch.values)
        except (ValueError, TypeError):
            n_mismatch = -1
        ok = n_mismatch == 0
        return CheckResult(
            check_id=POST_NAN_INTEGRITY_VIOLATION,
            name="NaN integrity",
            severity=CheckSeverity.INFO if ok else CheckSeverity.ERROR,
            phase=CheckPhase.POST_PROCESS,
            passed=ok,
            message=(
                f"{n_mismatch} píxel(es) divergen entre input y output en presencia de NaN."
                if n_mismatch != 0
                else "Integridad de NaN preservada."
            ),
            details={"mismatch_count": n_mismatch},
        )
