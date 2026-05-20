"""Fourier multi-harmonic interpolator.

Treats the 12 monthly inputs as samples of a periodic annual signal.
Uses ``numpy.fft.rfft`` to extract Fourier coefficients, truncates to
``n_harmonics`` positive frequencies (plus DC), and synthesizes daily
values at the target axis positions. Per ADR-0016 the wraparound is
``fft_implicit``: the FFT itself enforces periodicity, so no explicit
padding is required.
"""

from __future__ import annotations

from collections.abc import Hashable
from typing import ClassVar

import numpy as np
import xarray as xr

from tempify.constants import (
    DEFAULT_CHUNK_SIZE,
    FOURIER_MAX_HARMONICS,
    FOURIER_MIN_HARMONICS,
)
from tempify.interpolation._kernels import fourier_kernel
from tempify.interpolation.base import (
    BaseInterpolator,
    NanPolicy,
    TemporalAxis,
)
from tempify.interpolation.exceptions import PartialNanPixelError


class FourierInterpolator(BaseInterpolator):
    """Truncated Fourier series interpolator with configurable harmonics.

    Parameters
    ----------
    n_harmonics : int
        Number of positive-frequency harmonics retained beyond the DC
        term. Must lie in ``[FOURIER_MIN_HARMONICS, FOURIER_MAX_HARMONICS]``
        (= ``[1, 5]`` for 12 monthly samples; the Nyquist limit is 6).

    Notes
    -----
    Per REQ-005c Fourier has no special non-cyclic mode: the FFT-based
    reconstruction is inherently periodic regardless of the ``cyclic``
    flag. The output is stamped with ``attrs['tempify_wraparound'] =
    'fft_implicit'`` when wraparound is True, and ``'fft_implicit_off'``
    when the user explicitly requested ``wraparound=False`` (the
    numerical behavior is unchanged but the stamp records the user's
    intent for traceability per ADR-0016).
    """

    name: ClassVar[str] = "fourier"
    wraparound_stamp_on: ClassVar[str] = "fft_implicit"

    def __init__(self, n_harmonics: int = 3) -> None:
        if not (FOURIER_MIN_HARMONICS <= n_harmonics <= FOURIER_MAX_HARMONICS):
            raise ValueError(
                f"n_harmonics must be in [{FOURIER_MIN_HARMONICS}, "
                f"{FOURIER_MAX_HARMONICS}]; got {n_harmonics}"
            )
        self.n_harmonics = n_harmonics

    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        *,
        cyclic: bool = True,
        wraparound: bool | None = None,
        nan_policy: NanPolicy = "raise",
        chunk_size: int | None = None,
    ) -> xr.DataArray:
        """Interpolate ``source`` onto ``target_axis`` via truncated Fourier series."""
        self._validate_month_count(source)
        self._validate_month_contiguity(source)
        self._validate_calendar(target_axis)
        self._validate_nan_policy(nan_policy)
        wrap = self._resolve_wraparound(cyclic, wraparound)

        x_in = np.asarray(target_axis.monthly_anchor_doys(), dtype=np.float64)
        x_out = np.arange(1, target_axis.n_days + 1, dtype=np.float64)

        chunk = chunk_size if chunk_size is not None else DEFAULT_CHUNK_SIZE
        prepared = self._prepare_chunks(source, chunk)

        result = xr.apply_ufunc(
            _per_pixel,
            prepared,
            input_core_dims=[["month"]],
            output_core_dims=[["time"]],
            kwargs={
                "x_in": x_in,
                "x_out": x_out,
                "n_harmonics": self.n_harmonics,
                "nan_policy": nan_policy,
            },
            dask="parallelized",
            dask_gufunc_kwargs={"output_sizes": {"time": target_axis.n_days}},
            output_dtypes=[np.float64],
            vectorize=False,
        )
        result = result.assign_coords(time=target_axis.to_datetime_index())
        out = self._postprocess(result, target_axis, wraparound=wrap)
        out.attrs["tempify_n_harmonics"] = self.n_harmonics
        return out

    @staticmethod
    def _prepare_chunks(source: xr.DataArray, chunk: int) -> xr.DataArray:
        """Rechunk ``source`` so spatial dims use ``chunk`` and ``month`` is whole."""
        chunks: dict[Hashable, int] = {"month": -1}
        for d in source.dims:
            if d == "month":
                continue
            chunks[d] = chunk
        return source.chunk(chunks)


def _per_pixel(
    m_block: np.ndarray,
    *,
    x_in: np.ndarray,
    x_out: np.ndarray,
    n_harmonics: int,
    nan_policy: NanPolicy,
) -> np.ndarray:
    """Apply :func:`fourier_kernel` per pixel along the trailing ``month`` axis."""
    flat = m_block.reshape(-1, m_block.shape[-1])
    out = np.empty((flat.shape[0], x_out.size), dtype=np.float64)
    for i in range(flat.shape[0]):
        values = flat[i]
        nan_mask = np.isnan(values)
        n_nan = int(nan_mask.sum())
        if n_nan == values.size:
            out[i] = np.nan
            continue
        if n_nan > 0:
            if nan_policy == "raise":
                raise PartialNanPixelError(pixel_index=(i,), n_nan=n_nan)
            if nan_policy == "propagate_all":
                out[i] = np.nan
                continue
            # skip_pixel: FFT requires the full 12-sample input. With NaNs
            # we cannot run an honest FFT, so we propagate NaN for this
            # pixel rather than fabricate values.
            out[i] = np.nan
            continue
        out[i] = fourier_kernel(
            values.astype(np.float64),
            x_in.astype(np.float64),
            x_out,
            n_harmonics=n_harmonics,
        )
    return out.reshape(*m_block.shape[:-1], x_out.size)
