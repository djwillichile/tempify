"""Provenance utilities for tempify outputs.

Implements the canonical provenance dataclass (per ``docs/schemas/
processing-report.schema.md``) and helpers to compute, attach and
persist it. Hashes are MD5 (streaming, 64 KiB chunks) per ADR-0007.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import xarray as xr

DEFAULT_HASH_CHUNK_BYTES: Final[int] = 64 * 1024
"""Block size used by :func:`compute_provenance_md5` (per ADR-0007)."""


@dataclass(frozen=True, slots=True)
class Provenance:
    """Provenance record attached to every tempify output.

    Attributes
    ----------
    tempify_version : str
        Version of the tempify package that produced the output.
    tempify_method : str
        Interpolation method short name (e.g. ``'pchip_mp'``).
    tempify_params : str
        JSON-serialized dict with the method's parameters and runtime
        options (chunk size, tolerances, etc.).
    tempify_md5_inputs : tuple[tuple[str, str], ...]
        Tuple of ``(input_path, md5_hex)`` pairs for every input file.
    tempify_timestamp_utc : str
        ISO 8601 UTC timestamp of the run start.
    """

    tempify_version: str
    tempify_method: str
    tempify_params: str
    tempify_md5_inputs: tuple[tuple[str, str], ...]
    tempify_timestamp_utc: str


def compute_provenance_md5(path: Path, chunk_size: int = DEFAULT_HASH_CHUNK_BYTES) -> str:
    """Streaming MD5 hash of a file on disk.

    Parameters
    ----------
    path : pathlib.Path
        File to hash. Must exist and be readable.
    chunk_size : int
        Block size in bytes. Default ``64 KiB`` (``DEFAULT_HASH_CHUNK_BYTES``).

    Returns
    -------
    str
        Lowercase hexadecimal MD5 digest.
    """
    h = hashlib.md5()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def attach_provenance_attrs(da: xr.DataArray, provenance: Provenance) -> xr.DataArray:
    """Return a copy of ``da`` with the provenance fields attached as attrs.

    The five fields are added with the canonical names. ``tempify_md5_inputs``
    is serialized as a JSON string of a list of ``[path, md5]`` pairs so it
    can round-trip through NetCDF and Zarr (which require scalar/string-typed
    attribute values).
    """
    out = da.copy()
    out.attrs["tempify_version"] = provenance.tempify_version
    out.attrs["tempify_method"] = provenance.tempify_method
    out.attrs["tempify_params"] = provenance.tempify_params
    out.attrs["tempify_md5_inputs"] = json.dumps(
        [list(pair) for pair in provenance.tempify_md5_inputs]
    )
    out.attrs["tempify_timestamp_utc"] = provenance.tempify_timestamp_utc
    return out


def write_provenance_sidecar(target: Path, provenance: Provenance) -> Path:
    """Write the provenance as a ``<target>.provenance.json`` sidecar.

    Used by GeoTIFF outputs where the format does not natively support
    arbitrary attribute serialization. The sidecar mirrors the same
    schema used in NetCDF/Zarr attrs.

    Returns
    -------
    pathlib.Path
        Path of the sidecar file written.
    """
    sidecar = target.with_suffix(target.suffix + ".provenance.json")
    payload = {
        "tempify_version": provenance.tempify_version,
        "tempify_method": provenance.tempify_method,
        "tempify_params": provenance.tempify_params,
        "tempify_md5_inputs": [list(pair) for pair in provenance.tempify_md5_inputs],
        "tempify_timestamp_utc": provenance.tempify_timestamp_utc,
    }
    sidecar.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return sidecar
