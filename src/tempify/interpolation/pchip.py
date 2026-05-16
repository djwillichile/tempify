"""PCHIP (Fritsch-Carlson) interpolator.

Wraps the pure-NumPy/SciPy :func:`tempify.interpolation._kernels.pchip_kernel`
in an :class:`xarray.apply_ufunc` call with ``dask='parallelized'``. With
``cyclic=True`` the inputs are padded with two wrap nodes per side to
achieve C1 continuity at the December-January boundary (design section 5.2).
"""

from __future__ import annotations

from collections.abc import Hashable
from typing import ClassVar

import numpy as np
import xarray as xr

from tempify.constants import DEFAULT_CHUNK_SIZE
from tempify.interpolation._kernels import pchip_kernel
from tempify.interpolation.base import (
    BaseInterpolator,
    NanPolicy,
    TemporalAxis,
)
from tempify.interpolation.exceptions import PartialNanPixelError


class PchipInterpolator(BaseInterpolator):
    """Piecewise Cubic Hermite (Fritsch-Carlson) interpolator with cyclic option.

    Notes
    -----
    Per REQ-004 the default boundary mode is cyclic, padding with two
    wrap nodes per side to ensure C1 continuity. Per REQ-005b non-cyclic
    mode uses SciPy's natural polynomial extrapolation. NaN propagation
    follows the configurable ``nan_policy`` keyword of :meth:`interpolate`;
    in ``skip_pixel`` mode at least two valid monthly values are required.
    """

    name: ClassVar[str] = "pchip"

    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        *,
        cyclic: bool = True,
        nan_policy: NanPolicy = "raise",
        chunk_size: int | None = None,
    ) -> xr.DataArray:
        """Interpolate the monthly ``source`` onto ``target_axis`` with PCHIP."""
        self._validate_month_count(source)
        self._validate_month_contiguity(source)
        self._validate_calendar(target_axis)
        self._validate_nan_policy(nan_policy)

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
                "cyclic": cyclic,
                "nan_policy": nan_policy,
            },
            dask="parallelized",
            dask_gufunc_kwargs={"output_sizes": {"time": target_axis.n_days}},
            output_dtypes=[np.float64],
            vectorize=False,
        )
        result = result.assign_coords(time=target_axis.to_datetime_index())
        return self._postprocess(result, target_axis)

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
    cyclic: bool,
    nan_policy: NanPolicy,
) -> np.ndarray:
    """Apply :func:`pchip_kernel` per pixel along the trailing ``month`` axis."""
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
            mask = ~nan_mask
            if int(mask.sum()) < 2:
                out[i] = np.nan
                continue
            x_in_use = x_in[mask]
            values_use = values[mask]
        else:
            x_in_use = x_in
            values_use = values
        out[i] = pchip_kernel(
            values_use.astype(np.float64),
            x_in_use.astype(np.float64),
            x_out,
            cyclic=cyclic and n_nan == 0,
        )
    return out.reshape(*m_block.shape[:-1], x_out.size)
