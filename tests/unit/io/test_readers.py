"""Tests for io-handlers readers (GeoTIFF, NetCDF, MultiFileCollection)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from tempify.io import (
    CRSPreservationError,
    GeoTIFFReader,
    MultiFileCollectionReader,
    NetCDFReader,
    UnsupportedFormatError,
)


class TestGeoTIFFReader:
    def test_reads_single_band(self, sample_geotiff: Path) -> None:
        reader = GeoTIFFReader()
        da = reader.read(sample_geotiff)
        assert "y" in da.dims and "x" in da.dims
        meta = reader.metadata()
        assert meta["path"] == str(sample_geotiff)
        assert meta["crs"] is not None
        assert "4326" in meta["crs"]

    def test_reads_multiband(self, sample_multiband_geotiff: Path) -> None:
        reader = GeoTIFFReader()
        da = reader.read(sample_multiband_geotiff)
        assert "band" in da.dims
        assert da.sizes["band"] == 3

    def test_list_input_raises_type_error(self, sample_geotiff: Path) -> None:
        reader = GeoTIFFReader()
        with pytest.raises(TypeError, match="single Path"):
            reader.read([sample_geotiff])

    def test_preserves_crs(self, sample_geotiff: Path) -> None:
        reader = GeoTIFFReader()
        da = reader.read(sample_geotiff)
        crs = da.rio.crs
        assert crs is not None
        assert "4326" in str(crs)


class TestNetCDFReader:
    def test_reads_monthly_dataset(self, sample_netcdf_monthly: Path) -> None:
        reader = NetCDFReader()
        da = reader.read(sample_netcdf_monthly)
        assert "time" in da.dims
        assert da.sizes["time"] == 12
        assert da.attrs.get("units") == "degC"

    def test_explicit_variable(self, sample_netcdf_monthly: Path) -> None:
        reader = NetCDFReader(variable="tavg")
        da = reader.read(sample_netcdf_monthly)
        assert da.name == "tavg"

    def test_missing_variable_raises(self, sample_netcdf_monthly: Path) -> None:
        reader = NetCDFReader(variable="does_not_exist")
        with pytest.raises(KeyError, match="Disponibles"):
            reader.read(sample_netcdf_monthly)

    def test_list_input_raises_type_error(self, sample_netcdf_monthly: Path) -> None:
        reader = NetCDFReader()
        with pytest.raises(TypeError):
            reader.read([sample_netcdf_monthly])


class TestMultiFileCollectionReader:
    def test_concat_three_geotiffs(self, geotiff_collection_dir: tuple[Path, list[Path]]) -> None:
        _, paths = geotiff_collection_dir
        reader = MultiFileCollectionReader(concat_dim="month")
        da = reader.read(paths)
        assert "month" in da.dims
        assert da.sizes["month"] == 3
        assert da.rio.crs is not None

    def test_order_is_nfc_deterministic(
        self, geotiff_collection_dir: tuple[Path, list[Path]]
    ) -> None:
        """Files are sorted by NFC-normalized path string regardless of input order."""
        _, paths = geotiff_collection_dir
        reader = MultiFileCollectionReader()
        # Reverse the input order; the reader should still sort internally.
        reader.read(list(reversed(paths)))
        meta = reader.metadata()
        # Returned paths in metadata are in sorted order
        assert meta["paths"] == sorted(meta["paths"])

    def test_empty_list_raises(self) -> None:
        reader = MultiFileCollectionReader()
        with pytest.raises(ValueError, match="empty"):
            reader.read([])

    def test_single_path_raises_type_error(self, sample_geotiff: Path) -> None:
        reader = MultiFileCollectionReader()
        with pytest.raises(TypeError, match="list"):
            reader.read(sample_geotiff)

    def test_unsupported_extension_raises(self, tmp_path: Path) -> None:
        bad = tmp_path / "data.xyz"
        bad.write_bytes(b"")
        reader = MultiFileCollectionReader()
        with pytest.raises(UnsupportedFormatError):
            reader.read([bad])

    def test_mismatched_crs_raises(self, tmp_path: Path, sample_geotiff: Path) -> None:
        """Two files with different CRS values must trigger CRSPreservationError."""
        import rioxarray  # noqa: F401
        import xarray as xr

        other_path = tmp_path / "other_crs.tif"
        rng = np.random.default_rng(99)
        da = xr.DataArray(
            rng.standard_normal((4, 4)).astype(np.float32),
            dims=("y", "x"),
            coords={
                "y": [3.5, 2.5, 1.5, 0.5],
                "x": [0.5, 1.5, 2.5, 3.5],
            },
            name="data",
        ).rio.write_crs("EPSG:3857")
        da.rio.to_raster(other_path)

        reader = MultiFileCollectionReader()
        with pytest.raises(CRSPreservationError):
            reader.read([sample_geotiff, other_path])
