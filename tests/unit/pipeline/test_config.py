"""Tests for PipelineConfig invariants."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from tempify.pipeline import InvalidConfigError, PipelineConfig


class TestPipelineConfigInvariants:
    def test_basic_construction(self, tmp_path: Path) -> None:
        cfg = PipelineConfig(
            method="linear",
            target_year=2023,
            output_dir=tmp_path,
        )
        assert cfg.method == "linear"
        assert cfg.scheduler == "threaded"
        assert cfg.reproducibility_mode == "parallel"

    def test_skip_pre_validation_requires_dry_run(self, tmp_path: Path) -> None:
        with pytest.raises(InvalidConfigError, match="skip_pre_validation"):
            PipelineConfig(
                method="linear",
                target_year=2023,
                output_dir=tmp_path,
                skip_pre_validation=True,
                dry_run=False,
            )

    def test_skip_pre_validation_with_dry_run_is_ok(self, tmp_path: Path) -> None:
        cfg = PipelineConfig(
            method="linear",
            target_year=2023,
            output_dir=tmp_path,
            skip_pre_validation=True,
            dry_run=True,
        )
        assert cfg.dry_run is True

    def test_custom_anchor_requires_axis(self, tmp_path: Path) -> None:
        with pytest.raises(InvalidConfigError, match="custom_time_axis"):
            PipelineConfig(
                method="linear",
                target_year=2023,
                output_dir=tmp_path,
                monthly_anchor="custom",
            )

    def test_custom_axis_without_custom_anchor_raises(self, tmp_path: Path) -> None:
        with pytest.raises(InvalidConfigError, match="custom_time_axis"):
            PipelineConfig(
                method="linear",
                target_year=2023,
                output_dir=tmp_path,
                custom_time_axis=tuple(datetime(2023, m, 15) for m in range(1, 13)),
            )

    def test_invalid_chunk_size(self, tmp_path: Path) -> None:
        with pytest.raises(InvalidConfigError, match="chunk_size"):
            PipelineConfig(
                method="linear",
                target_year=2023,
                output_dir=tmp_path,
                chunk_size=0,
            )

    def test_is_frozen(self, tmp_path: Path) -> None:
        cfg = PipelineConfig(method="linear", target_year=2023, output_dir=tmp_path)
        with pytest.raises((AttributeError, TypeError)):
            cfg.method = "pchip"  # type: ignore[misc]
