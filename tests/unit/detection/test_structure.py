"""Tests for StructureDetector."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import rioxarray  # noqa: F401 - registers the .rio accessor
import xarray as xr

from tempify.detection import (
    SIDECAR_EXTENSIONS,
    EmptyInputError,
    HeterogeneousFilesError,
    StructureDetector,
    StructureMode,
)


def _make_tif(path: Path, shape: tuple[int, int] = (3, 3)) -> Path:
    rng = np.random.default_rng(0)
    da = xr.DataArray(
        rng.standard_normal(shape).astype(np.float32),
        dims=("y", "x"),
        coords={
            "y": [shape[0] - 0.5 - i for i in range(shape[0])],
            "x": [0.5 + i for i in range(shape[1])],
        },
        name="data",
    ).rio.write_crs("EPSG:4326")
    da.rio.to_raster(path)
    return path


def _make_multiband_tif(path: Path, n_bands: int = 3) -> Path:
    rng = np.random.default_rng(0)
    da = xr.DataArray(
        rng.standard_normal((n_bands, 3, 3)).astype(np.float32),
        dims=("band", "y", "x"),
        coords={
            "band": list(range(1, n_bands + 1)),
            "y": [2.5, 1.5, 0.5],
            "x": [0.5, 1.5, 2.5],
        },
        name="data",
    ).rio.write_crs("EPSG:4326")
    da.rio.to_raster(path)
    return path


class TestModeASingleFile:
    def test_single_file_is_mode_a(self, tmp_path: Path) -> None:
        p = _make_tif(tmp_path / "single.tif")
        result = StructureDetector().detect(p)
        assert result.structure_mode == StructureMode.SINGLE_STACK
        assert result.files == (p,)
        assert result.confidence["structure_mode"] == 1.0

    def test_multiband_returns_band_descriptions_when_present(self, tmp_path: Path) -> None:
        p = _make_multiband_tif(tmp_path / "multi.tif", n_bands=3)
        result = StructureDetector().detect(p)
        assert result.structure_mode == StructureMode.SINGLE_STACK
        # band_descriptions is either None (rasterio returned empty descriptions)
        # or a tuple of length 3 (descriptions present).
        if result.band_descriptions is not None:
            assert len(result.band_descriptions) == 3


class TestModeBDirectory:
    def test_folder_with_multiple_tifs_is_mode_b(self, tmp_path: Path) -> None:
        for i in range(3):
            _make_tif(tmp_path / f"step_{i:02d}.tif")
        result = StructureDetector().detect(tmp_path)
        assert result.structure_mode == StructureMode.MONOLAYER_COLLECTION
        assert len(result.files) == 3
        # Files are NFC-sorted
        names = [p.name for p in result.files]
        assert names == sorted(names)

    def test_folder_with_one_tif_degrades_to_mode_a(self, tmp_path: Path) -> None:
        _make_tif(tmp_path / "only.tif")
        result = StructureDetector().detect(tmp_path)
        assert result.structure_mode == StructureMode.SINGLE_STACK
        assert result.confidence["structure_mode"] < 1.0

    def test_sidecar_files_are_ignored(self, tmp_path: Path) -> None:
        _make_tif(tmp_path / "step_01.tif")
        _make_tif(tmp_path / "step_02.tif")
        # Create sidecar files that should be skipped
        (tmp_path / "step_01.tif.aux.xml").write_text("<sidecar/>")
        (tmp_path / "step_01.tif.ovr").write_text("")
        (tmp_path / "step_02.tif.provenance.json").write_text("{}")
        result = StructureDetector().detect(tmp_path)
        assert result.structure_mode == StructureMode.MONOLAYER_COLLECTION
        assert len(result.files) == 2

    def test_heterogeneous_extensions_raise(self, tmp_path: Path) -> None:
        _make_tif(tmp_path / "step_01.tif")
        # Build a fake .nc by writing an actual NetCDF
        rng = np.random.default_rng(0)
        da = xr.DataArray(
            rng.standard_normal((3, 3)).astype(np.float32),
            dims=("y", "x"),
            name="data",
        )
        da.to_netcdf(tmp_path / "step_02.nc")
        with pytest.raises(HeterogeneousFilesError):
            StructureDetector().detect(tmp_path)

    def test_empty_directory_raises(self, tmp_path: Path) -> None:
        with pytest.raises(EmptyInputError):
            StructureDetector().detect(tmp_path)


class TestModeCExplicitList:
    def test_explicit_list_is_mode_c(self, tmp_path: Path) -> None:
        paths = [_make_tif(tmp_path / f"a_{i}.tif") for i in range(3)]
        result = StructureDetector().detect(paths)
        assert result.structure_mode == StructureMode.EXPLICIT_LIST
        assert len(result.files) == 3
        assert result.confidence["structure_mode"] == 1.0

    def test_explicit_list_is_sorted_nfc(self, tmp_path: Path) -> None:
        paths = [_make_tif(tmp_path / f"a_{i}.tif") for i in range(3)]
        # Pass in reverse order; detector should sort
        result = StructureDetector().detect(list(reversed(paths)))
        names = [p.name for p in result.files]
        assert names == sorted(names)

    def test_empty_list_raises(self) -> None:
        with pytest.raises(EmptyInputError):
            StructureDetector().detect([])


class TestSidecarExtensionsCatalog:
    def test_canonical_extensions_present(self) -> None:
        for ext in (".aux.xml", ".ovr", ".tfw", ".prj", ".cpg"):
            assert ext in SIDECAR_EXTENSIONS
