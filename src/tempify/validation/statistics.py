"""Statistical reporter for tempify outputs.

Computes per-band ``min``, ``max``, ``mean``, ``std``, ``nan_pct`` and
``count_valid`` over the leading temporal dimension. The output dict
matches the schema documented in
``docs/schemas/validation-report.schema.md``.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import xarray as xr

STATISTIC_NAMES: Final[tuple[str, ...]] = (
    "min",
    "max",
    "mean",
    "std",
    "nan_pct",
    "count_valid",
)


class StatisticalReporter:
    """Compute per-band statistics over a DataArray with a leading temporal axis."""

    def report(self, da: xr.DataArray) -> dict[str, dict[str, float]]:
        """Return ``{step_index: {stat_name: value, ...}, ...}``.

        The leading dimension is detected as the first dim that is not
        ``x`` or ``y``. If no such dim exists the whole array is treated
        as a single band.
        """
        band_dim = None
        for d in da.dims:
            if d not in ("x", "y"):
                band_dim = d
                break
        if band_dim is None:
            return {"0": self._stats_of(da)}
        out: dict[str, dict[str, float]] = {}
        for i in range(int(da.sizes[band_dim])):
            slice_da = da.isel({band_dim: i})
            out[str(i)] = self._stats_of(slice_da)
        return out

    @staticmethod
    def _stats_of(arr: xr.DataArray) -> dict[str, float]:
        values = arr.values
        total = int(values.size)
        nan_mask = ~np.isfinite(values)
        n_valid = int(total - nan_mask.sum())
        if n_valid == 0:
            return {
                "min": float("nan"),
                "max": float("nan"),
                "mean": float("nan"),
                "std": float("nan"),
                "nan_pct": 100.0,
                "count_valid": 0.0,
            }
        finite = values[~nan_mask]
        return {
            "min": float(np.min(finite)),
            "max": float(np.max(finite)),
            "mean": float(np.mean(finite)),
            "std": float(np.std(finite)),
            "nan_pct": float(100.0 * nan_mask.sum() / total),
            "count_valid": float(n_valid),
        }
