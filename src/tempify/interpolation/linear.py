"""Linear interpolator.

Stub. Real implementation in task-2.1.2 with cyclic and non-cyclic
boundary handling per REQ-004 and REQ-005a.
"""

from __future__ import annotations

from typing import Any

import xarray as xr

from tempify.interpolation.base import BaseInterpolator, TemporalAxis


class LinearInterpolator(BaseInterpolator):
    """Piecewise linear interpolator between consecutive monthly nodes."""

    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        **opts: Any,
    ) -> xr.DataArray:
        raise NotImplementedError("LinearInterpolator.interpolate is implemented in task-2.1.2")
