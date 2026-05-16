"""Tests for io-handlers provenance utilities."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rioxarray  # noqa: F401 - registers the .rio accessor
import xarray as xr

from tempify.io.provenance import (
    Provenance,
    attach_provenance_attrs,
    compute_provenance_md5,
    write_provenance_sidecar,
)


def _provenance_sample() -> Provenance:
    return Provenance(
        tempify_version="0.1.0",
        tempify_method="pchip_mp",
        tempify_params='{"convergence_tol": 1e-6}',
        tempify_md5_inputs=(("input.tif", "abc123"),),
        tempify_timestamp_utc="2026-05-16T14:00:00Z",
    )


def test_compute_md5_matches_hashlib(tmp_path: Path) -> None:
    path = tmp_path / "data.bin"
    payload = b"abcdef" * 10_000
    path.write_bytes(payload)
    expected = hashlib.md5(payload).hexdigest()
    assert compute_provenance_md5(path) == expected


def test_compute_md5_streaming_handles_large_files(tmp_path: Path) -> None:
    """MD5 should be chunked, not load the whole file into memory."""
    path = tmp_path / "big.bin"
    block = b"x" * (64 * 1024)
    with path.open("wb") as f:
        for _ in range(8):  # 512 KiB total
            f.write(block)
    h_expected = hashlib.md5(block * 8).hexdigest()
    assert compute_provenance_md5(path, chunk_size=64 * 1024) == h_expected


def test_attach_provenance_attrs_does_not_mutate_input() -> None:
    da = xr.DataArray(np.arange(4).reshape(2, 2), dims=("y", "x"), name="data")
    original = da.copy()
    p = _provenance_sample()
    out = attach_provenance_attrs(da, p)
    assert "tempify_version" in out.attrs
    assert "tempify_version" not in original.attrs
    assert out.attrs["tempify_version"] == "0.1.0"
    assert out.attrs["tempify_method"] == "pchip_mp"
    md5_roundtrip = json.loads(out.attrs["tempify_md5_inputs"])
    assert md5_roundtrip == [["input.tif", "abc123"]]


def test_write_provenance_sidecar_creates_json_next_to_target(tmp_path: Path) -> None:
    target = tmp_path / "out.tif"
    target.write_bytes(b"")
    p = _provenance_sample()
    sidecar = write_provenance_sidecar(target, p)
    assert sidecar.exists()
    assert sidecar.name == "out.tif.provenance.json"
    payload = json.loads(sidecar.read_text())
    assert payload["tempify_version"] == "0.1.0"
    assert payload["tempify_md5_inputs"] == [["input.tif", "abc123"]]
