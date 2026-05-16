"""Tests for io-handlers writers (NetCDF, GeoTIFF single/collection, Zarr)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import rioxarray  # noqa: F401 - registers the .rio accessor
import xarray as xr

from tempify.io import (
    GeoTIFFCollectionWriter,
    MultiBandGeoTIFFWriter,
    NetCDFReader,
    NetCDFWriter,
    Provenance,
    UnsupportedBandCountError,
    ZarrWriter,
)
from tempify.io.common import MissingOptionalDependencyError


def _make_monthly(tmp_path: Path) -> xr.DataArray:
    rng = np.random.default_rng(7)
    return xr.DataArray(
        rng.standard_normal((4, 3, 3)).astype(np.float64),
        dims=("month", "y", "x"),
        coords={
            "month": [1, 2, 3, 4],
            "y": [2.5, 1.5, 0.5],
            "x": [0.5, 1.5, 2.5],
        },
        name="tavg",
    ).rio.write_crs("EPSG:4326")


class TestNetCDFWriter:
    def test_roundtrip_preserves_values(self, tmp_path: Path) -> None:
        da = _make_monthly(tmp_path)
        target = tmp_path / "out.nc"
        writer = NetCDFWriter()
        path = writer.write(da, target)
        assert path == target
        assert target.exists()
        reread = NetCDFReader().read(target)
        np.testing.assert_allclose(da.values, reread.values, atol=1e-12)

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        da = _make_monthly(tmp_path)
        target = tmp_path / "nested" / "dir" / "out.nc"
        writer = NetCDFWriter()
        writer.write(da, target)
        assert target.exists()

    def test_complevel_passed(self, tmp_path: Path) -> None:
        da = _make_monthly(tmp_path)
        target = tmp_path / "out.nc"
        NetCDFWriter(complevel=1).write(da, target)
        # If complevel option is rejected by xarray the write would fail
        assert target.exists()


class TestMultiBandGeoTIFFWriter:
    def test_writes_3band(self, tmp_path: Path) -> None:
        da = _make_monthly(tmp_path)
        target = tmp_path / "out_multi.tif"
        MultiBandGeoTIFFWriter().write(da, target)
        assert target.exists()

    def test_band_count_exceed_raises(self, tmp_path: Path) -> None:
        # Build a DataArray with too many bands by stacking
        rng = np.random.default_rng(0)
        big = xr.DataArray(
            rng.standard_normal((70000, 1, 1)).astype(np.float32),
            dims=("band", "y", "x"),
        )
        with pytest.raises(UnsupportedBandCountError):
            MultiBandGeoTIFFWriter().write(big, tmp_path / "huge.tif")


class TestGeoTIFFCollectionWriter:
    def test_writes_one_file_per_step(self, tmp_path: Path) -> None:
        da = _make_monthly(tmp_path)
        out_dir = tmp_path / "collection_out"
        writer = GeoTIFFCollectionWriter()
        files = writer.write(da, out_dir)
        assert len(files) == 4
        for f in files:
            assert f.exists()
            assert f.suffix == ".tif"
        manifest = out_dir / "_manifest.json"
        assert manifest.exists()
        listed = json.loads(manifest.read_text())
        assert sorted(listed) == sorted(f.name for f in files)

    def test_provenance_sidecar_per_file(self, tmp_path: Path) -> None:
        da = _make_monthly(tmp_path)
        out_dir = tmp_path / "collection_out_prov"
        prov = Provenance(
            tempify_version="0.1.0",
            tempify_method="linear",
            tempify_params="{}",
            tempify_md5_inputs=(),
            tempify_timestamp_utc="2026-05-16T14:00:00Z",
        )
        writer = GeoTIFFCollectionWriter(provenance=prov)
        files = writer.write(da, out_dir)
        for f in files:
            sidecar = f.with_suffix(".tif.provenance.json")
            assert sidecar.exists()
            payload = json.loads(sidecar.read_text())
            assert payload["tempify_method"] == "linear"

    def test_pure_spatial_raises_value_error(self, tmp_path: Path) -> None:
        rng = np.random.default_rng(0)
        da = xr.DataArray(
            rng.standard_normal((3, 3)).astype(np.float32),
            dims=("y", "x"),
        )
        with pytest.raises(ValueError, match="non-spatial leading"):
            GeoTIFFCollectionWriter().write(da, tmp_path / "bad")


class TestZarrWriter:
    def test_writes_zarr_when_available(self, tmp_path: Path) -> None:
        pytest.importorskip("zarr")
        da = _make_monthly(tmp_path)
        target = tmp_path / "out.zarr"
        path = ZarrWriter().write(da, target)
        assert path == target
        assert target.exists()

    def test_missing_zarr_raises_typed_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import builtins

        real_import = builtins.__import__

        def fake_import(name: str, *args: object, **kwargs: object) -> object:
            if name == "zarr":
                raise ImportError("simulated missing zarr")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        da = _make_monthly(tmp_path)
        with pytest.raises(MissingOptionalDependencyError) as excinfo:
            ZarrWriter().write(da, tmp_path / "out.zarr")
        assert excinfo.value.dependency == "zarr"
