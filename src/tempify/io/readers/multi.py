"""Multi-file collection reader.

Concatenates a list of single-file rasters into a single DataArray
along a new ``band`` (or user-specified) dimension. Files are sorted
lexicographically with Unicode NFC normalization to guarantee a
cross-platform deterministic order (Windows is case-insensitive on
filesystem listing, NFC fixes that).
"""

from __future__ import annotations

import unicodedata
from pathlib import Path
from typing import Any

import xarray as xr

from tempify.io.common import CRSPreservationError, UnsupportedFormatError
from tempify.io.readers.geotiff import GeoTIFFReader
from tempify.io.readers.netcdf import NetCDFReader


def _normalize_for_sort(p: Path) -> str:
    """Unicode NFC normalization of the path string for deterministic sort."""
    return unicodedata.normalize("NFC", str(p))


def _pick_reader(path: Path) -> GeoTIFFReader | NetCDFReader:
    """Choose a single-file reader based on the file extension."""
    suffix = path.suffix.lower()
    if suffix in {".tif", ".tiff"}:
        return GeoTIFFReader()
    if suffix in {".nc", ".nc4", ".cdf"}:
        return NetCDFReader()
    raise UnsupportedFormatError(suffix)


class MultiFileCollectionReader:
    """Read a list of files and concat them along a new dimension."""

    def __init__(self, concat_dim: str = "band") -> None:
        """Construct the reader.

        Parameters
        ----------
        concat_dim : str
            Name of the new dimension along which files are concatenated.
            Default ``'band'``; pipeline code may rename it to ``'month'``
            or ``'time'`` based on detection results.
        """
        self.concat_dim = concat_dim
        self._last_metadata: dict[str, Any] = {}

    def read(self, source: Path | list[Path]) -> xr.DataArray:
        """Read and concat the files in ``source``."""
        if not isinstance(source, list):
            raise TypeError(
                "MultiFileCollectionReader expects a list of Paths; use "
                "GeoTIFFReader or NetCDFReader for single files."
            )
        if len(source) == 0:
            raise ValueError("source list is empty")
        paths = sorted([Path(p) for p in source], key=_normalize_for_sort)
        arrays = []
        crs_set: set[str] = set()
        for p in paths:
            reader = _pick_reader(p)
            arr = reader.read(p)
            # If the per-file array has a single-step trailing dimension
            # (e.g., a band axis of size 1), squeeze it so the concat is
            # along a clean new axis.
            if "band" in arr.dims and arr.sizes.get("band", 0) == 1:
                arr = arr.squeeze("band", drop=True)
            arrays.append(arr)
            crs = getattr(arr.rio, "crs", None)
            if crs is not None:
                crs_set.add(str(crs))
        if len(crs_set) > 1:
            raise CRSPreservationError(
                f"Múltiples CRS distintos en la colección: {sorted(crs_set)}"
            )
        result = xr.concat(arrays, dim=self.concat_dim)
        # Re-stamp CRS after concat (xarray.concat may drop it)
        if crs_set:
            result = result.rio.write_crs(next(iter(crs_set)))
        self._last_metadata = {
            "paths": [str(p) for p in paths],
            "n_files": len(paths),
            "concat_dim": self.concat_dim,
            "crs": next(iter(crs_set)) if crs_set else None,
            "shape": tuple(result.shape),
            "dims": tuple(result.dims),
        }
        return result

    def metadata(self) -> dict[str, Any]:
        return dict(self._last_metadata)
