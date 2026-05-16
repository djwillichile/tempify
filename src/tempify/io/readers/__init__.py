"""Reader implementations for tempify."""

from tempify.io.readers.geotiff import GeoTIFFReader
from tempify.io.readers.multi import MultiFileCollectionReader
from tempify.io.readers.netcdf import NetCDFReader

__all__ = [
    "GeoTIFFReader",
    "MultiFileCollectionReader",
    "NetCDFReader",
]
