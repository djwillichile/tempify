"""Tests for the tempify CLI entry point."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import rioxarray  # noqa: F401 - registers the .rio accessor
import xarray as xr
from typer.testing import CliRunner

from tempify.cli import app
from tempify.cli.errors import EXIT_CODES

runner = CliRunner()


@pytest.fixture
def worldclim_like(tmp_path: Path) -> Path:
    rng = np.random.default_rng(0)
    out = tmp_path / "wc"
    out.mkdir()
    for month in range(1, 13):
        arr = (
            15.0 + 10.0 * np.sin(2 * np.pi * (month - 1) / 12) + rng.normal(scale=0.1, size=(3, 3))
        ).astype(np.float32)
        da = xr.DataArray(
            arr,
            dims=("y", "x"),
            coords={"y": [2.5, 1.5, 0.5], "x": [0.5, 1.5, 2.5]},
            name="data",
        ).rio.write_crs("EPSG:4326")
        da.rio.to_raster(out / f"wc2.1_2.5m_tavg_{month:02d}.tif")
    return out


class TestVersion:
    def test_version_outputs(self) -> None:
        result = runner.invoke(app, ["version"])
        assert result.exit_code == EXIT_CODES["ok"]
        assert "tempify" in result.stdout
        assert "numpy" in result.stdout


class TestProfilesList:
    def test_profiles_list_outputs_four_profiles(self) -> None:
        result = runner.invoke(app, ["profiles", "list"])
        assert result.exit_code == EXIT_CODES["ok"]
        assert "temperature" in result.stdout
        assert "precipitation" in result.stdout
        assert "relative_humidity" in result.stdout
        assert "solar_radiation" in result.stdout


class TestInspect:
    def test_inspect_runs_only_detection(self, worldclim_like: Path) -> None:
        result = runner.invoke(app, ["inspect", str(worldclim_like)])
        assert result.exit_code == EXIT_CODES["ok"]
        assert "Modo de estructura" in result.stdout
        assert "Frecuencia inferida" in result.stdout


class TestValidate:
    def test_validate_exits_zero_on_homogeneous_input(self, worldclim_like: Path) -> None:
        result = runner.invoke(app, ["validate", str(worldclim_like)])
        assert result.exit_code == EXIT_CODES["ok"]
        assert "Pre-validación" in result.stdout


class TestConvert:
    def test_convert_basic_end_to_end(self, worldclim_like: Path, tmp_path: Path) -> None:
        out_dir = tmp_path / "out"
        result = runner.invoke(
            app,
            [
                "convert",
                str(worldclim_like),
                "--output",
                str(out_dir),
                "--method",
                "linear",
                "--year",
                "2023",
            ],
        )
        assert result.exit_code == EXIT_CODES["ok"]
        produced = list(out_dir.glob("*.nc"))
        assert len(produced) == 1

    def test_convert_with_report_writes_markdown(
        self, worldclim_like: Path, tmp_path: Path
    ) -> None:
        out_dir = tmp_path / "out"
        report_path = tmp_path / "report.md"
        result = runner.invoke(
            app,
            [
                "convert",
                str(worldclim_like),
                "--output",
                str(out_dir),
                "--method",
                "linear",
                "--year",
                "2023",
                "--report",
                str(report_path),
            ],
        )
        assert result.exit_code == EXIT_CODES["ok"]
        assert report_path.exists()
        content = report_path.read_text(encoding="utf-8")
        assert "Reporte de procesamiento tempify" in content

    def test_force_method_without_confirmation_flag_fails(
        self, worldclim_like: Path, tmp_path: Path
    ) -> None:
        result = runner.invoke(
            app,
            [
                "convert",
                str(worldclim_like),
                "--output",
                str(tmp_path / "out"),
                "--method",
                "linear",
                "--force-method",
            ],
        )
        assert result.exit_code == EXIT_CODES["user_cancellation"]
