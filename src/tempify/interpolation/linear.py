"""Linear interpolator.

Wraps the pure-NumPy :func:`tempify.interpolation._kernels.linear_kernel`
in an :class:`xarray.apply_ufunc` call with ``dask='parallelized'`` to
vectorize over the spatial dimensions.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import xarray as xr

from tempify.constants import DEFAULT_CHUNK_SIZE
from tempify.interpolation._kernels import linear_kernel
from tempify.interpolation.base import (
    BaseInterpolator,
    NanPolicy,
    TemporalAxis,
)
from tempify.interpolation.exceptions import PartialNanPixelError


class LinearInterpolator(BaseInterpolator):
    """Piecewise linear interpolator between consecutive monthly nodes.

    Parameters
    ----------
    None

    Notes
    -----
    Per REQ-004 the default boundary mode is cyclic; per REQ-005a the
    non-cyclic mode applies constant extrapolation outside the input
    range. NaN propagation follows the configurable ``nan_policy``
    keyword of :meth:`interpolate`.
    """

    name: ClassVar[str] = "linear"
    wraparound_stamp_on: ClassVar[str] = "climatological_2pt"

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
        """Interpolate the monthly ``source`` onto ``target_axis`` linearly."""
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
            kwargs={"x_in": x_in, "x_out": x_out, "cyclic": wrap, "nan_policy": nan_policy},
            dask="parallelized",
            dask_gufunc_kwargs={"output_sizes": {"time": target_axis.n_days}},
            output_dtypes=[np.float64],
            vectorize=False,
        )
        result = result.assign_coords(time=target_axis.to_datetime_index())
        return self._postprocess(result, target_axis, wraparound=wrap)

    @staticmethod
    def _prepare_chunks(source: xr.DataArray, chunk: int) -> xr.DataArray:
        """Rechunk ``source`` so spatial dims use ``chunk`` and ``month`` is whole."""
        from collections.abc import Hashable

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
    cyclic: bool,
    nan_policy: NanPolicy,
) -> np.ndarray:
    """Apply :func:`linear_kernel` per pixel along the trailing ``month`` axis.

    ``m_block`` has shape ``(..., 12)`` after apply_ufunc rearranges it.
    Returns an array with shape ``(..., len(x_out))``.
    """
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
            # skip_pixel: fall through to interpolate without NaNs by
            # filtering them out
            mask = ~nan_mask
            x_in_use = x_in[mask]
            values_use = values[mask]
        else:
            x_in_use = x_in
            values_use = values
        out[i] = linear_kernel(
            values_use.astype(np.float64),
            x_in_use.astype(np.float64),
            x_out,
            cyclic=cyclic,
        )
    return out.reshape(*m_block.shape[:-1], x_out.size)
