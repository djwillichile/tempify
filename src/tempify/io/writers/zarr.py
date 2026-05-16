"""Zarr writer (optional dependency).

Zarr is an optional extra. The :class:`ZarrWriter` performs the import
lazily inside :meth:`write` so the rest of the I/O layer can be used
without installing zarr. If the package is missing, a typed
:class:`MissingOptionalDependencyError` is raised at the point of use,
not at import time.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import xarray as xr

from tempify.io.common import MissingOptionalDependencyError


class ZarrWriter:
    """Write a DataArray to a Zarr store (extra ``tempify[zarr]``)."""

    def write(
        self,
        data: xr.DataArray,
        target: Path,
        **opts: Any,
    ) -> Path:
        """Write ``data`` to the Zarr store at ``target``."""
        try:
            import zarr  # type: ignore[import-not-found]  # noqa: F401
        except ImportError as exc:
            raise MissingOptionalDependencyError(
                dependency="zarr",
                extra="zarr",
            ) from exc
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = opts.get("mode", "w")
        data.to_zarr(path, mode=mode)
        return path
