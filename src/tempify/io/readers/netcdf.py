"""NetCDF reader.

Wraps :func:`xarray.open_dataset` with ``decode_cf=True`` and extracts
the first data variable as a DataArray. CRS is reconstructed via the
``rio`` accessor when present in the file's ``grid_mapping`` attribute.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import rioxarray  # noqa: F401 - registers the .rio accessor
import xarray as xr


class NetCDFReader:
    """Reader for NetCDF (.nc, .nc4) files."""

    def __init__(self, variable: str | None = None) -> None:
        """Construct the reader.

        Parameters
        ----------
        variable : str | None
            Name of the variable to extract. When ``None``, the first
            data variable in the dataset is returned.
        """
        self.variable = variable
        self._last_metadata: dict[str, Any] = {}

    def read(self, source: Path | list[Path]) -> xr.DataArray:
        """Read ``source`` and return the selected DataArray."""
        if isinstance(source, list):
            raise TypeError(
                "NetCDFReader expects a single Path; use MultiFileCollectionReader "
                "for a list of files."
            )
        path = Path(source)
        ds = xr.open_dataset(path, decode_cf=True)
        try:
            if self.variable is not None:
                if self.variable not in ds.data_vars:
                    raise KeyError(
                        f"Variable '{self.variable}' no encontrada en {path}. "
                        f"Disponibles: {sorted([str(v) for v in ds.data_vars])}"
                    )
                da = ds[self.variable].load()
            else:
                # Pick the variable with the most spatial-temporal dimensions,
                # skipping CRS / grid_mapping scalars that rioxarray writes.
                data_vars = [(str(name), int(ds[name].ndim)) for name in ds.data_vars]
                # Largest ndim wins; among ties keep insertion order.
                data_vars.sort(key=lambda pair: pair[1], reverse=True)
                if not data_vars or data_vars[0][1] == 0:
                    raise KeyError(
                        f"No se encontró ninguna variable de datos con dimensiones en {path}."
                    )
                da = ds[data_vars[0][0]].load()
        finally:
            ds.close()
        crs = da.rio.crs if hasattr(da, "rio") else None
        self._last_metadata = {
            "path": str(path),
            "variable": str(da.name),
            "crs": str(crs) if crs is not None else None,
            "shape": tuple(da.shape),
            "dtype": str(da.dtype),
            "dims": tuple(da.dims),
        }
        return da

    def metadata(self) -> dict[str, Any]:
        return dict(self._last_metadata)
