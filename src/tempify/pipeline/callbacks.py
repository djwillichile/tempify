"""Protocols and constants for pipeline callbacks."""

from __future__ import annotations

from pathlib import Path
from typing import Final, Literal, Protocol, runtime_checkable

from tempify.detection.frequency import TemporalFrequency

PipelinePhase = Literal[
    "detect",
    "validate_geospatial",
    "validate_compatibility",
    "interpolate",
    "validate_post",
    "write",
    "generate_report",
]
"""The 7 canonical pipeline phases (per ADR-0014/ADR-0016 design clarifications)."""

PHASES: Final[tuple[PipelinePhase, ...]] = (
    "detect",
    "validate_geospatial",
    "validate_compatibility",
    "interpolate",
    "validate_post",
    "write",
    "generate_report",
)


@runtime_checkable
class ProgressCallback(Protocol):
    """Protocol invoked by :class:`TempifyPipeline` to report progress."""

    def __call__(
        self,
        phase: PipelinePhase,
        progress: float,
        message: str | None = None,
    ) -> None:
        """Receive a progress update.

        Parameters
        ----------
        phase : PipelinePhase
            Current pipeline phase.
        progress : float
            Position in [0.0, 1.0]; ``0.0`` at phase start, ``1.0`` at end.
        message : str | None
            Optional human-readable note (in Spanish).
        """


@runtime_checkable
class FrequencyResolverProtocol(Protocol):
    """Protocol invoked when temporal frequency cannot be inferred automatically."""

    def __call__(self, files: tuple[Path, ...]) -> TemporalFrequency:
        """Resolve the temporal frequency for the given ``files``."""
