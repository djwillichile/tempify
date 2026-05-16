"""PipelineResult: the return value of :meth:`TempifyPipeline.run`."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tempify.detection import StructureDetectionResult
    from tempify.detection.frequency import ResolutionResult
    from tempify.pipeline.report import ProcessingReport
    from tempify.validation.report import ValidationReport


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Outcome of a single pipeline run.

    Attributes
    ----------
    outputs : tuple[Path, ...]
        Path(s) written by the writer.
    report : ProcessingReport
        Full provenance + statistics report.
    detection : StructureDetectionResult
        Structure detection outcome.
    frequency : ResolutionResult
        Temporal frequency resolution outcome.
    pre_validation : ValidationReport
        Pre-process validation report.
    post_validation : ValidationReport | None
        Post-process validation report (``None`` in dry_run / skip mode).
    """

    outputs: tuple[Path, ...]
    report: ProcessingReport
    detection: StructureDetectionResult
    frequency: ResolutionResult
    pre_validation: ValidationReport
    post_validation: ValidationReport | None
