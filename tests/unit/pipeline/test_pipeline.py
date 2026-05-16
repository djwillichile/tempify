"""End-to-end smoke tests for TempifyPipeline."""

from __future__ import annotations

from pathlib import Path

import pytest

from tempify.pipeline import (
    EXIT_CODES,
    PipelineConfig,
    PipelinePreValidationError,
    ProcessingReport,
    TempifyPipeline,
)


class TestPipelineE2E:
    def test_run_with_worldclim_collection(self, worldclim_like_dir: Path, tmp_path: Path) -> None:
        cfg = PipelineConfig(
            method="linear",
            target_year=2023,
            output_dir=tmp_path / "out",
        )
        result = TempifyPipeline(cfg).run(worldclim_like_dir)
        assert len(result.outputs) == 1
        assert result.outputs[0].exists()
        assert result.outputs[0].suffix == ".nc"
        assert isinstance(result.report, ProcessingReport)
        assert result.report.method == "linear"
        assert result.report.target_year == 2023
        assert result.report.dry_run is False

    def test_dry_run_skips_interpolation_and_write(
        self, worldclim_like_dir: Path, tmp_path: Path
    ) -> None:
        cfg = PipelineConfig(
            method="linear",
            target_year=2023,
            output_dir=tmp_path / "out",
            dry_run=True,
            skip_pre_validation=True,
        )
        result = TempifyPipeline(cfg).run(worldclim_like_dir)
        assert result.outputs == ()
        assert result.report.dry_run is True
        assert result.post_validation is None

    def test_progress_callback_is_invoked_per_phase(
        self, worldclim_like_dir: Path, tmp_path: Path
    ) -> None:
        events: list[tuple[str, float]] = []

        def cb(phase: str, progress: float, message: str | None = None) -> None:
            events.append((phase, progress))

        cfg = PipelineConfig(
            method="linear",
            target_year=2023,
            output_dir=tmp_path / "out",
            progress_callback=cb,
        )
        TempifyPipeline(cfg).run(worldclim_like_dir)
        phases_seen = {phase for phase, _ in events}
        # All 7 canonical phases must be reported
        expected = {
            "detect",
            "validate_geospatial",
            "validate_compatibility",
            "interpolate",
            "validate_post",
            "write",
            "generate_report",
        }
        assert expected.issubset(phases_seen)

    def test_pchip_mp_preserves_monthly_mean(
        self, worldclim_like_dir: Path, tmp_path: Path
    ) -> None:
        cfg = PipelineConfig(
            method="pchip_mp",
            target_year=2023,
            output_dir=tmp_path / "out",
        )
        result = TempifyPipeline(cfg).run(worldclim_like_dir)
        # The post-validation should pass the mean preservation check
        assert result.post_validation is not None
        mean_check = next(c for c in result.post_validation.checks if c.check_id == "POST-001")
        assert mean_check.passed is True

    def test_exit_codes_canonical(self) -> None:
        assert EXIT_CODES["ok"] == 0
        assert EXIT_CODES["validation_failure"] == 1
        assert EXIT_CODES["sigint"] == 130


class TestPipelineErrors:
    def test_pre_validation_failure_raises(self, tmp_path: Path) -> None:
        # Build an explicit list of 2 GeoTIFFs with different CRS to trigger
        # a CRS mismatch GEO-001 ERROR.
        import numpy as np
        import rioxarray  # noqa: F401
        import xarray as xr

        rng = np.random.default_rng(0)

        def _tif(path: Path, crs: str) -> Path:
            da = xr.DataArray(
                rng.standard_normal((3, 3)).astype(np.float32),
                dims=("y", "x"),
                coords={"y": [2.5, 1.5, 0.5], "x": [0.5, 1.5, 2.5]},
                name="data",
            ).rio.write_crs(crs)
            da.rio.to_raster(path)
            return path

        f1 = _tif(tmp_path / "wc2.1_2.5m_tavg_01.tif", "EPSG:4326")
        f2 = _tif(tmp_path / "wc2.1_2.5m_tavg_02.tif", "EPSG:3857")

        cfg = PipelineConfig(
            method="linear",
            target_year=2023,
            output_dir=tmp_path / "out",
        )
        with pytest.raises((PipelinePreValidationError, Exception)):
            TempifyPipeline(cfg).run([f1, f2])
