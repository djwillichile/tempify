"""Temporal interpolation methods for monthly to daily densification.

This package implements six interpolation methods: Linear, PCHIP,
PCHIP with Rymes-Myers mean-preserving correction, Fourier multi
harmonic, Akima (1970), and natural cubic spline. Each operates on
an ``xr.DataArray`` with dims ``(month, y, x)`` and returns a daily
``DataArray`` with dims ``(time, y, x)``.

Per ADR-0004, the precipitation rejection policy is enforced by the
validation layer (``tempify.validation``), NOT here. The interpolators
themselves operate on any variable; the variable-method compatibility
check lives in Capa 3.

Akima and CubicSpline added in v0.1.4 per ADR-0018.
"""

from tempify.interpolation.akima import AkimaInterpolator
from tempify.interpolation.base import BaseInterpolator, TemporalAxis
from tempify.interpolation.cubic import CubicSplineInterpolator
from tempify.interpolation.fourier import FourierInterpolator
from tempify.interpolation.linear import LinearInterpolator
from tempify.interpolation.pchip import PchipInterpolator
from tempify.interpolation.pchip_mp import PchipMeanPreservingInterpolator

__all__ = [
    "AkimaInterpolator",
    "BaseInterpolator",
    "CubicSplineInterpolator",
    "FourierInterpolator",
    "LinearInterpolator",
    "PchipInterpolator",
    "PchipMeanPreservingInterpolator",
    "TemporalAxis",
]
