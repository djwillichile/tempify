"""PCHIP with Rymes-Myers mean-preserving correction.

Stub. Real implementation in task-2.3.2/2.3.3 with the iterative
mean-preserving algorithm per REQ-006 and ADR-0010.
"""

from __future__ import annotations

from typing import Any

import xarray as xr

from tempify.interpolation.base import BaseInterpolator, TemporalAxis


class PchipMeanPreservingInterpolator(BaseInterpolator):
    """PCHIP base interpolation refined iteratively to preserve monthly means."""

    def __init__(
        self,
        convergence_tol: float = 1e-6,
        max_iterations: int = 50,
    ) -> None:
        self.convergence_tol = convergence_tol
        self.max_iterations = max_iterations

    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        **opts: Any,
    ) -> xr.DataArray:
        raise NotImplementedError(
            "PchipMeanPreservingInterpolator.interpolate is implemented in task-2.3.2"
        )
