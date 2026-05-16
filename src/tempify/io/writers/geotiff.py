"""GeoTIFF writers (single multi-band and collection).

:class:`MultiBandGeoTIFFWriter` writes one GeoTIFF with N bands.
:class:`GeoTIFFCollectionWriter` writes N GeoTIFF files (one per band)
with a configurable filename template, accompanied by a ``.provenance.json``
sidecar that mirrors the NetCDF attrs.

GeoTIFF's TIFF container imposes a hard limit on the number of bands
that fits in the 16-bit SamplesPerPixel field; the writer enforces this
explicitly per REQ-006 of io-handlers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar, Final

import rioxarray  # noqa: F401 - registers the .rio accessor
import xarray as xr

from tempify.io.common import UnsupportedBandCountError
from tempify.io.provenance import Provenance, write_provenance_sidecar

MAX_GEOTIFF_BANDS: Final[int] = 65535


class MultiBandGeoTIFFWriter:
    """Write a multi-band GeoTIFF (one file, N bands)."""

    def write(
        self,
        data: xr.DataArray,
        target: Path,
        **opts: Any,
    ) -> Path:
        """Write ``data`` to a single multi-band GeoTIFF.

        ``data`` must have a band-like leading dimension (``band``,
        ``time`` or ``month``); it is collapsed to TIFF bands in order.
        """
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Determine the band-like dim (first non-spatial)
        band_dim = None
        for d in data.dims:
            if d not in ("x", "y"):
                band_dim = d
                break
        if band_dim is not None:
            n_bands = int(data.sizes[band_dim])
            if n_bands > MAX_GEOTIFF_BANDS:
                raise UnsupportedBandCountError(n_bands, MAX_GEOTIFF_BANDS)
        data.rio.to_raster(path, **{k: v for k, v in opts.items() if k != "complevel"})
        return path


class GeoTIFFCollectionWriter:
    """Write a band collection as N single-band GeoTIFFs with provenance sidecar."""

    DEFAULT_TEMPLATE: ClassVar[str] = "{name}_{index:03d}.tif"

    def __init__(
        self,
        filename_template: str = "{name}_{index:03d}.tif",
        provenance: Provenance | None = None,
    ) -> None:
        self.filename_template = filename_template
        self.provenance = provenance

    def write(
        self,
        data: xr.DataArray,
        target: Path,
        **opts: Any,
    ) -> list[Path]:
        """Write ``data`` as N GeoTIFFs under directory ``target``.

        Each step along the leading non-spatial dimension becomes one
        single-band GeoTIFF. A ``.provenance.json`` sidecar is written
        per file when :attr:`provenance` is set.
        """
        out_dir = Path(target)
        out_dir.mkdir(parents=True, exist_ok=True)
        # Detect the band-like dim
        band_dim = None
        for d in data.dims:
            if d not in ("x", "y"):
                band_dim = d
                break
        if band_dim is None:
            raise ValueError(
                "GeoTIFFCollectionWriter requires a non-spatial leading "
                "dimension (e.g. 'band', 'time' or 'month')."
            )
        written: list[Path] = []
        name = data.name or "data"
        for idx in range(int(data.sizes[band_dim])):
            slice_da = data.isel({band_dim: idx})
            filename = self.filename_template.format(name=name, index=idx, band_dim=band_dim)
            file_path = out_dir / filename
            slice_da.rio.to_raster(
                file_path,
                **{k: v for k, v in opts.items() if k != "complevel"},
            )
            written.append(file_path)
            if self.provenance is not None:
                write_provenance_sidecar(file_path, self.provenance)
        # Always drop a top-level manifest of files written
        manifest = out_dir / "_manifest.json"
        manifest.write_text(json.dumps([p.name for p in written], indent=2), encoding="utf-8")
        return written
