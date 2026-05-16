"""I/O layer for tempify.

Reads and writes ``xr.DataArray`` to/from disk in GeoTIFF, NetCDF and
optionally Zarr formats. CRS is preserved via the ``rio`` accessor
(ADR-0001) and provenance metadata is attached to every output per
the canonical schema defined in :mod:`tempify.io.provenance`.

The layer exposes two Protocols (:class:`BaseReader`, :class:`BaseWriter`)
and concrete implementations per format. Per the architectural rule
this layer does NOT import from the interpolation, detection,
validation, pipeline, cli or gui layers.
"""

from tempify.io.common import (
    BaseReader,
    BaseWriter,
    CRSPreservationError,
    IOTempifyError,
    MissingOptionalDependencyError,
    UnsupportedBandCountError,
    UnsupportedFormatError,
)
from tempify.io.provenance import (
    Provenance,
    attach_provenance_attrs,
    compute_provenance_md5,
    write_provenance_sidecar,
)
from tempify.io.readers import (
    GeoTIFFReader,
    MultiFileCollectionReader,
    NetCDFReader,
)
from tempify.io.writers import (
    GeoTIFFCollectionWriter,
    MultiBandGeoTIFFWriter,
    NetCDFWriter,
    ZarrWriter,
)

__all__ = [
    "BaseReader",
    "BaseWriter",
    "CRSPreservationError",
    "GeoTIFFCollectionWriter",
    "GeoTIFFReader",
    "IOTempifyError",
    "MissingOptionalDependencyError",
    "MultiBandGeoTIFFWriter",
    "MultiFileCollectionReader",
    "NetCDFReader",
    "NetCDFWriter",
    "Provenance",
    "UnsupportedBandCountError",
    "UnsupportedFormatError",
    "ZarrWriter",
    "attach_provenance_attrs",
    "compute_provenance_md5",
    "write_provenance_sidecar",
]
