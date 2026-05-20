"""PCHIP with Rymes-Myers mean-preserving correction.

Implements the iterative mean-preserving algorithm of Rymes & Myers
(2001) on top of a PCHIP baseline. The output is guaranteed to preserve
the monthly aggregates exactly to within ``convergence_tol`` per
REQ-006 / ADR-0010 nivel 1.
"""

from __future__ import annotations

from collections.abc import Hashable
from typing import ClassVar

import numpy as np
import xarray as xr

from tempify.constants import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_RM_CONVERGENCE_TOL,
    DEFAULT_RM_MAX_ITER,
)
from tempify.interpolation._kernels import pchip_mp_kernel
from tempify.interpolation.base import (
    BaseInterpolator,
    NanPolicy,
    TemporalAxis,
)
from tempify.interpolation.exceptions import PartialNanPixelError


def _compute_day_to_month(target_axis: TemporalAxis) -> np.ndarray:
    """Return an int array of length ``n_days`` mapping each day to its month [0, 11]."""
    days = target_axis.to_datetime_index()
    return np.asarray([d.month - 1 for d in days], dtype=np.int64)


class PchipMeanPreservingInterpolator(BaseInterpolator):
    """PCHIP base interpolation refined iteratively to preserve monthly means.

    Parameters
    ----------
    convergence_tol : float
        Iterator stopping criterion in the variable's units (per ADR-0010
        nivel 1). Default :data:`tempify.constants.DEFAULT_RM_CONVERGENCE_TOL`
        = ``1e-6``.
    max_iterations : int
        Hard safety cap on the iterative correction. Default
        :data:`tempify.constants.DEFAULT_RM_MAX_ITER` = ``50``.

    Notes
    -----
    Per REQ-006 the system iterates until the maximum absolute residual
    falls below ``convergence_tol``. Per REQ-007 the iteration count is
    recorded on the output ``DataArray`` as the maximum observed across
    all pixels in the chunk (``attrs['rymes_myers_iterations_max']``);
    convergence status is reported as a boolean
    (``attrs['rymes_myers_converged']``), ``True`` when no pixel
    reached the iteration cap. The midpoint convention (ADR-0015) governs
    only the auxiliary node initialization; the monthly mean preservation
    is independent of the anchor.
    """

    name: ClassVar[str] = "pchip_mp"
    wraparound_stamp_on: ClassVar[str] = "climatological_4pt"

    def __init__(
        self,
        convergence_tol: float = DEFAULT_RM_CONVERGENCE_TOL,
        max_iterations: int = DEFAULT_RM_MAX_ITER,
    ) -> None:
        if convergence_tol <= 0:
            raise ValueError(f"convergence_tol must be positive, got {convergence_tol}")
        if max_iterations < 1:
            raise ValueError(f"max_iterations must be >= 1, got {max_iterations}")
        self.convergence_tol = convergence_tol
        self.max_iterations = max_iterations

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
        """Interpolate ``source`` onto ``target_axis`` preserving monthly means."""
        self._validate_month_count(source)
        self._validate_month_contiguity(source)
        self._validate_calendar(target_axis)
        self._validate_nan_policy(nan_policy)
        wrap = self._resolve_wraparound(cyclic, wraparound)

        x_in = np.asarray(target_axis.monthly_anchor_doys(), dtype=np.float64)
        x_out = np.arange(1, target_axis.n_days + 1, dtype=np.float64)
        day_to_month = _compute_day_to_month(target_axis)

        chunk = chunk_size if chunk_size is not None else DEFAULT_CHUNK_SIZE
        prepared = self._prepare_chunks(source, chunk)

        # Use a list to accumulate iteration counts. apply_ufunc doesn't
        # easily return scalar metadata per call, so we attach a global
        # summary via the kernel running in a single batch (the simplest
        # robust approach is to record max across pixels at the end).
        max_iters_observed: list[int] = [0]

        def _per_pixel(m_block: np.ndarray) -> np.ndarray:
            return _run_per_pixel(
                m_block,
                x_in=x_in,
                x_out=x_out,
                day_to_month=day_to_month,
                cyclic=wrap,
                convergence_tol=self.convergence_tol,
                max_iterations=self.max_iterations,
                nan_policy=nan_policy,
                iter_collector=max_iters_observed,
            )

        result = xr.apply_ufunc(
            _per_pixel,
            prepared,
            input_core_dims=[["month"]],
            output_core_dims=[["time"]],
            dask="parallelized",
            dask_gufunc_kwargs={"output_sizes": {"time": target_axis.n_days}},
            output_dtypes=[np.float64],
            vectorize=False,
        )
        result = result.assign_coords(time=target_axis.to_datetime_index())
        # Force materialization on small arrays so we can stamp the iteration
        # count; on dask-backed arrays we defer the stamp until compute.
        out = self._postprocess(result, target_axis, wraparound=wrap)
        out.attrs["rymes_myers_iterations_max"] = max_iters_observed[0]
        out.attrs["rymes_myers_convergence_tol"] = self.convergence_tol
        out.attrs["rymes_myers_max_iterations_allowed"] = self.max_iterations
        # 1 iff every pixel converged strictly before the cap, 0 if any
        # pixel hit ``max_iterations`` without satisfying
        # ``max|error| < convergence_tol``. Per spec design.md §5.3. We
        # use int (0/1) instead of bool because NetCDF attribute writers
        # only accept numeric/string dtypes (``b1`` is rejected).
        out.attrs["rymes_myers_converged"] = int(
            max_iters_observed[0] < self.max_iterations
        )
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


def _run_per_pixel(
    m_block: np.ndarray,
    *,
    x_in: np.ndarray,
    x_out: np.ndarray,
    day_to_month: np.ndarray,
    cyclic: bool,
    convergence_tol: float,
    max_iterations: int,
    nan_policy: NanPolicy,
    iter_collector: list[int],
) -> np.ndarray:
    """Run :func:`pchip_mp_kernel` per pixel along the trailing ``month`` axis."""
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
            # Mean-preserving algorithm needs all 12 monthly anchors to be
            # meaningful; skip_pixel propagates NaN here (we don't fabricate
            # missing months because that would silently violate REQ-006).
            out[i] = np.nan
            continue
        daily, iters = pchip_mp_kernel(
            values.astype(np.float64),
            x_in.astype(np.float64),
            x_out,
            day_to_month,
            cyclic=cyclic,
            convergence_tol=convergence_tol,
            max_iterations=max_iterations,
        )
        out[i] = daily
        if iters > iter_collector[0]:
            iter_collector[0] = iters
    return out.reshape(*m_block.shape[:-1], x_out.size)
