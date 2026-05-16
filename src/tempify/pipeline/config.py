"""PipelineConfig: immutable run-time configuration for the pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from tempify.pipeline.callbacks import FrequencyResolverProtocol, ProgressCallback
from tempify.pipeline.errors import InvalidConfigError

InterpolationMethod = Literal["linear", "pchip", "pchip_mp", "fourier"]
OutputFormat = Literal["netcdf", "geotiff_collection", "multiband_geotiff", "zarr"]
ReproMode = Literal["strict", "parallel"]
MonthlyAnchor = Literal["midpoint", "start", "end", "custom"]


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Frozen, validated configuration for a single pipeline run."""

    method: InterpolationMethod
    target_year: int
    output_dir: Path
    output_format: OutputFormat = "netcdf"
    chunk_size: int = 512
    scheduler: Literal["threaded", "synchronous"] = "threaded"
    reproducibility_mode: ReproMode = "parallel"
    progress_callback: ProgressCallback | None = None
    progress_frequency_hz: float = 4.0
    frequency_resolver_callback: FrequencyResolverProtocol | None = None
    dry_run: bool = False
    skip_pre_validation: bool = False
    force_method: bool = False
    variable_profile_override: str | None = None
    monthly_anchor: MonthlyAnchor = "midpoint"
    custom_time_axis: tuple[datetime, ...] | None = None
    seed: int | None = None
    method_options: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.skip_pre_validation and not self.dry_run:
            raise InvalidConfigError(
                "skip_pre_validation=True requires dry_run=True (inspect mode)."
            )
        if self.monthly_anchor == "custom" and self.custom_time_axis is None:
            raise InvalidConfigError("monthly_anchor='custom' requires custom_time_axis to be set.")
        if self.monthly_anchor != "custom" and self.custom_time_axis is not None:
            raise InvalidConfigError(
                "custom_time_axis can only be provided with monthly_anchor='custom'."
            )
        if self.chunk_size <= 0:
            raise InvalidConfigError(f"chunk_size must be positive; got {self.chunk_size}")
        if self.progress_frequency_hz <= 0:
            raise InvalidConfigError(
                f"progress_frequency_hz must be positive; got {self.progress_frequency_hz}"
            )
