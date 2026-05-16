"""Canonical catalog of validation error codes.

Each entry is referenced from the validators in this layer and surfaced
to users via :class:`~tempify.validation.report.CheckResult`. The full
table is defined in ``docs/schemas/validation-report.schema.md``.
"""

from __future__ import annotations

from typing import Final

# Geospatial coherence (pre-process)
GEO_CRS_MISMATCH: Final[str] = "GEO-001"
GEO_EXTENT_MISMATCH: Final[str] = "GEO-002"
GEO_RESOLUTION_MISMATCH: Final[str] = "GEO-003"
GEO_NODATA_MISMATCH: Final[str] = "GEO-004"
GEO_SHAPE_MISMATCH: Final[str] = "GEO-005"

# Method / variable compatibility (pre-process)
COMPAT_METHOD_NOT_ALLOWED: Final[str] = "COMPAT-001"
COMPAT_PRECIPITATION_SMOOTH: Final[str] = "COMPAT-002"
COMPAT_FORCE_OVERRIDE_USED: Final[str] = "COMPAT-003"

# Post-interpolation
POST_MEAN_NOT_PRESERVED: Final[str] = "POST-001"
POST_CYCLIC_DISCONTINUITY: Final[str] = "POST-002"
POST_PHYSICAL_RANGE_VIOLATION: Final[str] = "POST-003"
POST_NAN_INTEGRITY_VIOLATION: Final[str] = "POST-004"

ALL_CODES: Final[tuple[str, ...]] = (
    GEO_CRS_MISMATCH,
    GEO_EXTENT_MISMATCH,
    GEO_RESOLUTION_MISMATCH,
    GEO_NODATA_MISMATCH,
    GEO_SHAPE_MISMATCH,
    COMPAT_METHOD_NOT_ALLOWED,
    COMPAT_PRECIPITATION_SMOOTH,
    COMPAT_FORCE_OVERRIDE_USED,
    POST_MEAN_NOT_PRESERVED,
    POST_CYCLIC_DISCONTINUITY,
    POST_PHYSICAL_RANGE_VIOLATION,
    POST_NAN_INTEGRITY_VIOLATION,
)
