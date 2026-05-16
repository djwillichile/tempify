"""Common I/O abstractions: Protocols and typed exceptions.

Per the architectural rule of separation between layers, this module
defines only structural Protocols and typed exception classes; it does
NOT depend on any other tempify layer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar, Protocol, runtime_checkable

import xarray as xr

# ---------------------------------------------------------------------------
# Typed exceptions (REQ-009 / NFR-004): every error carries a stable code
# and Spanish-language message.
# ---------------------------------------------------------------------------


class IOTempifyError(Exception):
    """Base class for all I/O layer errors."""

    code: ClassVar[str] = "TEMPIFY-IO-000"


class UnsupportedFormatError(IOTempifyError):
    """Raised when the file extension or driver is not supported by tempify."""

    code: ClassVar[str] = "TEMPIFY-IO-001"

    def __init__(self, fmt: str) -> None:
        self.fmt = fmt
        super().__init__(
            f"Formato '{fmt}' no soportado por tempify. Formatos soportados: "
            "GeoTIFF (.tif, .tiff), NetCDF (.nc, .nc4) y Zarr (extra opcional)."
        )


class MissingOptionalDependencyError(IOTempifyError):
    """Raised when an optional dependency is needed but not installed."""

    code: ClassVar[str] = "TEMPIFY-IO-002"

    def __init__(self, dependency: str, extra: str) -> None:
        self.dependency = dependency
        self.extra = extra
        super().__init__(
            f"Dependencia opcional '{dependency}' no está instalada. "
            f"Instálela con `pip install tempify[{extra}]`."
        )


class UnsupportedBandCountError(IOTempifyError):
    """Raised when a multi-band format limit is exceeded."""

    code: ClassVar[str] = "TEMPIFY-IO-003"

    def __init__(self, count: int, max_allowed: int) -> None:
        self.count = count
        self.max_allowed = max_allowed
        super().__init__(
            f"Número de bandas {count} excede el máximo {max_allowed} para "
            "este formato. Considere usar NetCDF o Zarr para series temporales "
            "más largas."
        )


class CRSPreservationError(IOTempifyError):
    """Raised when CRS information cannot be preserved across a read/write cycle."""

    code: ClassVar[str] = "TEMPIFY-IO-004"

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(
            f"No se pudo preservar el CRS durante la operación: {reason}. "
            "Verifique que el archivo tenga metadata espacial válida."
        )


# ---------------------------------------------------------------------------
# Protocols (REQ-001 / REQ-002)
# ---------------------------------------------------------------------------


@runtime_checkable
class BaseReader(Protocol):
    """Structural Protocol for tempify readers.

    A reader takes a single file path (or list of paths for multi-file
    readers) and returns an ``xr.DataArray`` with CRS preserved via the
    ``rio`` accessor.
    """

    def read(self, source: Path | list[Path]) -> xr.DataArray:
        """Read the raster from ``source`` into a DataArray with CRS attached."""
        ...

    def metadata(self) -> dict[str, Any]:
        """Return a dict of human-readable metadata about the last read."""
        ...


@runtime_checkable
class BaseWriter(Protocol):
    """Structural Protocol for tempify writers.

    A writer takes a DataArray and a target path and persists the data
    to disk. Returns the path written (which may differ from the input
    for collection writers that templated the filename).
    """

    def write(self, data: xr.DataArray, target: Path, **opts: Any) -> Path | list[Path]:
        """Write ``data`` to ``target`` and return the path(s) actually written."""
        ...
