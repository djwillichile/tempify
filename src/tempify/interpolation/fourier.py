"""Fourier multi-harmonic interpolator.

Stub. Real implementation in task-2.4.2 with harmonics validation
in [1, 5] per REQ-001 and Nyquist constraints.
"""

from __future__ import annotations

from typing import Any

import xarray as xr

from tempify.interpolation.base import BaseInterpolator, TemporalAxis


class FourierInterpolator(BaseInterpolator):
    """Truncated Fourier series interpolator with configurable harmonics."""

    def __init__(self, n_harmonics: int = 3) -> None:
        self.n_harmonics = n_harmonics

    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        **opts: Any,
    ) -> xr.DataArray:
        raise NotImplementedError("FourierInterpolator.interpolate is implemented in task-2.4.2")
