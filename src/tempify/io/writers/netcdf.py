"""NetCDF writer (CF-compliant default).

Encodes the output with zlib compression level 4 and attaches the
standard CF attributes (``units``, ``calendar``, ``_FillValue``,
``standard_name``, ``long_name``, ``grid_mapping``) when the caller
provides them via the DataArray's attrs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import xarray as xr


class NetCDFWriter:
    """Write a single DataArray to a NetCDF file (CF-compliant)."""

    def __init__(self, complevel: int = 4) -> None:
        self.complevel = complevel

    def write(
        self,
        data: xr.DataArray,
        target: Path,
        **opts: Any,
    ) -> Path:
        """Write ``data`` to ``target`` with CF metadata + zlib L4 encoding."""
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        encoding = {
            data.name or "data": {
                "zlib": True,
                "complevel": int(opts.get("complevel", self.complevel)),
            }
        }
        # If the DataArray has no name, xarray.to_netcdf needs one.
        if data.name is None:
            data = data.rename("data")
            encoding = {"data": encoding[next(iter(encoding))]}
        data.to_netcdf(path, encoding=encoding)
        return path
