"""Package-wide constants for tempify.

Per ADR-0010 these constants define the canonical Level 1 tolerance
(Rymes-Myers iterator convergence) and related defaults. Other levels
(contractual post-validator tolerance, per-variable acceptable error)
live in :mod:`tempify.validation` per their respective scopes.

Per ADR-0007 the default Dask scheduler for production interpolation
is ``threaded``; strict reproducibility mode uses ``synchronous``.
"""

from __future__ import annotations

from typing import Final

DEFAULT_CHUNK_SIZE: Final[int] = 512
"""Default Dask chunk size for spatial dimensions (pixels per side)."""

DEFAULT_RM_CONVERGENCE_TOL: Final[float] = 1e-6
"""Rymes-Myers iterator convergence tolerance (ADR-0010 Level 1).

Internal stopping criterion of the iterative algorithm in the variable's
units. NOT the contractual post-validation tolerance: that lives in
:mod:`tempify.validation` per ADR-0010 Level 2.
"""

DEFAULT_RM_MAX_ITER: Final[int] = 50
"""Maximum iterations for the Rymes-Myers algorithm before bailing out."""

FOURIER_MIN_HARMONICS: Final[int] = 1
"""Minimum number of Fourier harmonics accepted by FourierInterpolator."""

FOURIER_MAX_HARMONICS: Final[int] = 5
"""Maximum number of Fourier harmonics (Nyquist for 12 samples is 6)."""
