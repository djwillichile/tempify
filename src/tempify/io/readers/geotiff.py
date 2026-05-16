"""GeoTIFF reader.

Wraps :func:`rioxarray.open_rasterio` to load a GeoTIFF (single or
multi-band) into an ``xr.DataArray`` with CRS preserved via the ``rio``
accessor. Multi-band GeoTIFFs are returned with a ``band`` dimension
that the caller can rename to ``month`` or ``time`` according to its
semantics (the reader does NOT infer temporal meaning).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import rioxarray  # noqa: F401 - registers the .rio accessor
import xarray as xr


class GeoTIFFReader:
    """Reader for single GeoTIFF files (any number of bands)."""

    def __init__(self) -> None:
        self._last_metadata: dict[str, Any] = {}

    def read(self, source: Path | list[Path]) -> xr.DataArray:
        """Read ``source`` as an ``xr.DataArray`` preserving CRS."""
        if isinstance(source, list):
            raise TypeError(
                "GeoTIFFReader expects a single Path; use MultiFileCollectionReader "
                "for a list of files."
            )
        path = Path(source)
        da = xr.open_dataarray(path, engine="rasterio", mask_and_scale=True)
        # rioxarray attaches CRS automatically; verify it survived.
        crs = da.rio.crs if hasattr(da, "rio") else None
        self._last_metadata = {
            "path": str(path),
            "crs": str(crs) if crs is not None else None,
            "shape": tuple(da.shape),
            "dtype": str(da.dtype),
            "dims": tuple(da.dims),
        }
        return da

    def metadata(self) -> dict[str, Any]:
        """Return the metadata recorded during the last :meth:`read`."""
        return dict(self._last_metadata)
