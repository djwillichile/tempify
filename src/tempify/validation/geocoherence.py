"""Geospatial coherence validator (pre-process, fail-fast).

Verifies that a collection of rasters share a compatible CRS, extent,
pixel resolution, nodata sentinel, and shape per ADR-0009 canonical
tolerances. The validator emits one :class:`CheckResult` per axis; if
any check has severity ``ERROR`` the pipeline raises
:class:`PreValidationError`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Final

import rioxarray  # noqa: F401 - registers the .rio accessor
import xarray as xr

from tempify.validation._codes import (
    GEO_CRS_MISMATCH,
    GEO_EXTENT_MISMATCH,
    GEO_NODATA_MISMATCH,
    GEO_RESOLUTION_MISMATCH,
    GEO_SHAPE_MISMATCH,
)
from tempify.validation.report import (
    CheckPhase,
    CheckResult,
    CheckSeverity,
    ValidationReport,
)


@dataclass(frozen=True, slots=True)
class Tolerances:
    """Canonical tolerances for the geospatial coherence checks (ADR-0009)."""

    extent_rtol: float
    extent_atol_factor: float
    resolution_rtol: float


CANONICAL_TOLERANCES: Final[Tolerances] = Tolerances(
    extent_rtol=1e-6,
    extent_atol_factor=0.01,
    resolution_rtol=1e-6,
)


def _crs_equal(a: Any, b: Any) -> bool:
    if a is None or b is None:
        return a is None and b is None
    try:
        return bool(a.equals(b, ignore_axis_order=True))
    except (AttributeError, TypeError):
        return str(a) == str(b)


def _approx_equal(a: float, b: float, rtol: float = 1e-6, atol: float = 0.0) -> bool:
    if math.isnan(a) and math.isnan(b):
        return True
    return math.isclose(a, b, rel_tol=rtol, abs_tol=atol)


class GeospatialCoherenceValidator:
    """Pre-process check that all input rasters are spatially compatible."""

    def __init__(self, tolerances: Tolerances = CANONICAL_TOLERANCES) -> None:
        self.tolerances = tolerances

    def check(self, rasters: list[xr.DataArray]) -> ValidationReport:
        """Return a :class:`ValidationReport` with one CheckResult per axis.

        ``rasters`` must be a non-empty list. Single-element inputs are
        accepted (and trivially homogeneous).
        """
        if not rasters:
            raise ValueError("rasters list must not be empty")
        checks: list[CheckResult] = []
        first = rasters[0]
        checks.append(self._check_crs(first, rasters))
        checks.append(self._check_extent(first, rasters))
        checks.append(self._check_resolution(first, rasters))
        checks.append(self._check_nodata(first, rasters))
        checks.append(self._check_shape(first, rasters))
        return ValidationReport(checks=tuple(checks))

    def _check_crs(self, ref: xr.DataArray, rasters: list[xr.DataArray]) -> CheckResult:
        ref_crs = ref.rio.crs if hasattr(ref, "rio") else None
        mismatched = [
            i
            for i, r in enumerate(rasters)
            if not _crs_equal(r.rio.crs if hasattr(r, "rio") else None, ref_crs)
        ]
        return CheckResult(
            check_id=GEO_CRS_MISMATCH,
            name="CRS coherence",
            severity=CheckSeverity.ERROR if mismatched else CheckSeverity.INFO,
            phase=CheckPhase.PRE_PROCESS,
            passed=not mismatched,
            message=(
                f"CRS no coincide en {len(mismatched)} archivo(s) respecto al primero ({ref_crs})"
                if mismatched
                else f"CRS homogéneo ({ref_crs})"
            ),
            details={"mismatched_indices": mismatched, "reference_crs": str(ref_crs)},
        )

    def _bounds(self, da: xr.DataArray) -> tuple[float, float, float, float] | None:
        try:
            return tuple(float(b) for b in da.rio.bounds())  # type: ignore[return-value]
        except (AttributeError, ValueError):
            return None

    def _pixel_size(self, da: xr.DataArray) -> tuple[float, float] | None:
        try:
            res = da.rio.resolution()
            return float(res[0]), float(res[1])
        except (AttributeError, ValueError):
            return None

    def _check_extent(self, ref: xr.DataArray, rasters: list[xr.DataArray]) -> CheckResult:
        ref_bounds = self._bounds(ref)
        ref_res = self._pixel_size(ref)
        if ref_bounds is None or ref_res is None:
            return CheckResult(
                check_id=GEO_EXTENT_MISMATCH,
                name="Extent coherence",
                severity=CheckSeverity.WARN,
                phase=CheckPhase.PRE_PROCESS,
                passed=True,
                message="No se pudo determinar el extent del raster de referencia",
            )
        atol = self.tolerances.extent_atol_factor * abs(ref_res[0])
        mismatched = []
        for i, r in enumerate(rasters):
            b = self._bounds(r)
            if b is None or not all(
                _approx_equal(a, ref_a, rtol=self.tolerances.extent_rtol, atol=atol)
                for a, ref_a in zip(b, ref_bounds, strict=True)
            ):
                mismatched.append(i)
        return CheckResult(
            check_id=GEO_EXTENT_MISMATCH,
            name="Extent coherence",
            severity=CheckSeverity.ERROR if mismatched else CheckSeverity.INFO,
            phase=CheckPhase.PRE_PROCESS,
            passed=not mismatched,
            message=(
                f"Extent no coincide en {len(mismatched)} archivo(s)"
                if mismatched
                else "Extent homogéneo"
            ),
            details={"mismatched_indices": mismatched, "reference_bounds": ref_bounds},
        )

    def _check_resolution(self, ref: xr.DataArray, rasters: list[xr.DataArray]) -> CheckResult:
        ref_res = self._pixel_size(ref)
        if ref_res is None:
            return CheckResult(
                check_id=GEO_RESOLUTION_MISMATCH,
                name="Resolution coherence",
                severity=CheckSeverity.WARN,
                phase=CheckPhase.PRE_PROCESS,
                passed=True,
                message="No se pudo determinar la resolución del raster de referencia",
            )
        mismatched = []
        for i, r in enumerate(rasters):
            res = self._pixel_size(r)
            if res is None or not (
                _approx_equal(res[0], ref_res[0], rtol=self.tolerances.resolution_rtol)
                and _approx_equal(res[1], ref_res[1], rtol=self.tolerances.resolution_rtol)
            ):
                mismatched.append(i)
        return CheckResult(
            check_id=GEO_RESOLUTION_MISMATCH,
            name="Resolution coherence",
            severity=CheckSeverity.ERROR if mismatched else CheckSeverity.INFO,
            phase=CheckPhase.PRE_PROCESS,
            passed=not mismatched,
            message=(
                f"Resolución no coincide en {len(mismatched)} archivo(s)"
                if mismatched
                else "Resolución homogénea"
            ),
            details={"mismatched_indices": mismatched, "reference_resolution": ref_res},
        )

    def _check_nodata(self, ref: xr.DataArray, rasters: list[xr.DataArray]) -> CheckResult:
        ref_nd = getattr(ref.rio, "nodata", None) if hasattr(ref, "rio") else None
        mismatched = []
        for i, r in enumerate(rasters):
            nd = getattr(r.rio, "nodata", None) if hasattr(r, "rio") else None
            same = (ref_nd is None and nd is None) or (
                ref_nd is not None
                and nd is not None
                and ((math.isnan(ref_nd) and math.isnan(nd)) or ref_nd == nd)
            )
            if not same:
                mismatched.append(i)
        return CheckResult(
            check_id=GEO_NODATA_MISMATCH,
            name="Nodata coherence",
            severity=CheckSeverity.ERROR if mismatched else CheckSeverity.INFO,
            phase=CheckPhase.PRE_PROCESS,
            passed=not mismatched,
            message=(
                f"Nodata no coincide en {len(mismatched)} archivo(s)"
                if mismatched
                else "Nodata homogéneo"
            ),
            details={"mismatched_indices": mismatched, "reference_nodata": ref_nd},
        )

    def _check_shape(self, ref: xr.DataArray, rasters: list[xr.DataArray]) -> CheckResult:
        def spatial_shape(r: xr.DataArray) -> tuple[int, int] | None:
            try:
                return int(r.sizes["y"]), int(r.sizes["x"])
            except KeyError:
                return None

        ref_shape = spatial_shape(ref)
        mismatched = [i for i, r in enumerate(rasters) if spatial_shape(r) != ref_shape]
        return CheckResult(
            check_id=GEO_SHAPE_MISMATCH,
            name="Shape coherence",
            severity=CheckSeverity.ERROR if mismatched else CheckSeverity.INFO,
            phase=CheckPhase.PRE_PROCESS,
            passed=not mismatched,
            message=(
                f"Forma espacial no coincide en {len(mismatched)} archivo(s)"
                if mismatched
                else "Forma espacial homogénea"
            ),
            details={"mismatched_indices": mismatched, "reference_shape": ref_shape},
        )
