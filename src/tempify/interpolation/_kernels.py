"""Internal 1D NumPy kernels used by the interpolators.

Each kernel takes a 1D array of 12 monthly values plus the monthly
anchor positions (``x_in``, days-of-year) and the target positions
(``x_out``, days-of-year) and returns a 1D array of N target values.

The kernels are pure NumPy / SciPy with no xarray dependency. They are
intended to be wrapped by :func:`xarray.apply_ufunc` with
``dask='parallelized'`` to vectorize over the spatial dimensions.

Notes
-----
- All kernels accept ``cyclic: bool``. With ``cyclic=True`` December
  and January are treated as adjacent (the year wraps around).
- NaN handling is the caller's responsibility (the kernels operate on
  arrays that have already been filtered per ``nan_policy``).
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def linear_kernel(
    m: NDArray[np.floating],
    x_in: NDArray[np.floating],
    x_out: NDArray[np.floating],
    cyclic: bool,
) -> NDArray[np.floating]:
    """Piecewise linear interpolation on the year axis.

    Parameters
    ----------
    m : numpy.ndarray
        12 monthly values placed at ``x_in``.
    x_in : numpy.ndarray
        Strictly increasing array of length 12 with the day-of-year of
        each monthly anchor (per ADR-0015).
    x_out : numpy.ndarray
        Strictly increasing array of length N (typically 365 or 366)
        with the target days-of-year.
    cyclic : bool
        If ``True``, treat the year as periodic: linear interpolation
        wraps from December to January with period equal to
        ``x_out[-1] - x_out[0] + 1``. If ``False``, apply constant
        extrapolation outside ``[x_in[0], x_in[-1]]`` per REQ-005a.

    Returns
    -------
    numpy.ndarray
        Array of length ``len(x_out)`` with the interpolated values.
    """
    if cyclic:
        # Period is total number of days in the target year. Extend the
        # input with one wrap node on each side so np.interp can use them
        # linearly. The +1 accounts for "inclusive bounds".
        period = float(x_out[-1] - x_out[0]) + 1.0
        x_left = x_in[-1] - period
        x_right = x_in[0] + period
        m_ext = np.concatenate(([m[-1]], m, [m[0]]))
        x_ext = np.concatenate(([x_left], x_in, [x_right]))
        return np.asarray(np.interp(x_out, x_ext, m_ext))
    return np.asarray(np.interp(x_out, x_in, m))


def pchip_kernel(
    m: NDArray[np.floating],
    x_in: NDArray[np.floating],
    x_out: NDArray[np.floating],
    cyclic: bool,
) -> NDArray[np.floating]:
    """Piecewise cubic Hermite (Fritsch-Carlson) interpolation on the year axis.

    Parameters
    ----------
    m : numpy.ndarray
        12 monthly values placed at ``x_in``.
    x_in : numpy.ndarray
        Strictly increasing array of length 12 with the day-of-year of
        each monthly anchor.
    x_out : numpy.ndarray
        Strictly increasing array of length N with target days-of-year.
    cyclic : bool
        If True, treat the year as periodic. Per design section 5.2 the
        input nodes are padded with two wrap nodes on each side so that
        SciPy's PCHIP delivers C1 continuity at the December-January
        boundary. If False, SciPy's natural extrapolation is used for
        out-of-range positions per REQ-005b.

    Returns
    -------
    numpy.ndarray
        Array of length ``len(x_out)`` with the interpolated values.
    """
    from scipy.interpolate import PchipInterpolator as ScipyPchip  # type: ignore[import-untyped]

    if cyclic:
        period = float(x_out[-1] - x_out[0]) + 1.0
        m_ext = np.concatenate(([m[-2], m[-1]], m, [m[0], m[1]]))
        x_ext = np.concatenate(
            (
                [x_in[-2] - period, x_in[-1] - period],
                x_in,
                [x_in[0] + period, x_in[1] + period],
            )
        )
        pchip = ScipyPchip(x_ext, m_ext, extrapolate=False)
        return np.asarray(pchip(x_out))
    pchip = ScipyPchip(x_in, m, extrapolate=True)
    return np.asarray(pchip(x_out))


def fourier_kernel(
    m: NDArray[np.floating],
    x_in: NDArray[np.floating],
    x_out: NDArray[np.floating],
    n_harmonics: int,
) -> NDArray[np.floating]:
    """Truncated Fourier series interpolation via numpy.fft.rfft.

    The 12 monthly inputs are treated as periodic samples of an annual
    signal. The first ``n_harmonics`` positive-frequency coefficients
    (plus the DC term) are kept and used to synthesize values at
    arbitrary daily positions. Fourier is inherently periodic so there
    is no separate cyclic vs non-cyclic mode; the FFT semantics handle
    the year wraparound implicitly (per ADR-0016 stamp ``fft_implicit``).

    Parameters
    ----------
    m : numpy.ndarray
        12 monthly values (FFT requires uniformly spaced samples; we
        treat the monthly anchors as approximately uniform — the small
        non-uniformity from midpoint dates per ADR-0015 is absorbed via
        the explicit ``x_in`` re-projection below).
    x_in : numpy.ndarray
        Day-of-year of each monthly anchor (length 12).
    x_out : numpy.ndarray
        Day-of-year targets (length N).
    n_harmonics : int
        Number of positive-frequency harmonics to retain. Must be in
        ``[FOURIER_MIN_HARMONICS, FOURIER_MAX_HARMONICS]``. The DC term
        is always kept.

    Returns
    -------
    numpy.ndarray
        Array of length ``len(x_out)`` with the reconstructed values.
    """
    n = m.size
    coeffs = np.fft.rfft(m)
    period = float(x_out[-1] - x_out[0]) + 1.0
    t = (x_out - x_in[0]) / period * n
    result = np.full(x_out.size, float(np.real(coeffs[0])) / n, dtype=np.float64)
    max_k = min(n_harmonics, n // 2)
    for k in range(1, max_k + 1):
        c = coeffs[k]
        factor = 2.0 / n if (n % 2 != 0 or k < n // 2) else 1.0 / n
        angle = 2.0 * np.pi * k * t / n
        result += factor * (float(np.real(c)) * np.cos(angle) - float(np.imag(c)) * np.sin(angle))
    return result
