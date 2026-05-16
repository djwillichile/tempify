"""PCHIP (Fritsch-Carlson) interpolator.

Stub. Real implementation in task-2.2.2 with cyclic nodes and
extrapolation per REQ-004 and REQ-005b.
"""

from __future__ import annotations

from typing import Any

import xarray as xr

from tempify.interpolation.base import BaseInterpolator, TemporalAxis


class PchipInterpolator(BaseInterpolator):
    """Piecewise cubic Hermite interpolating polynomial (Fritsch-Carlson)."""

    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        **opts: Any,
    ) -> xr.DataArray:
        raise NotImplementedError("PchipInterpolator.interpolate is implemented in task-2.2.2")
