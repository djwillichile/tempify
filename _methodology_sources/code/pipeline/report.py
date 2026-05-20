"""ProcessingReport dataclass + ReportGenerator (Markdown renderer)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tempify.detection import StructureDetectionResult
    from tempify.detection.frequency import ResolutionResult
    from tempify.pipeline.config import PipelineConfig
    from tempify.validation.report import ValidationReport


def _tempify_version() -> str:
    try:
        return version("tempify")
    except PackageNotFoundError:
        return "0.0.0-dev"


@dataclass(frozen=True, slots=True)
class ProcessingReport:
    """Canonical report attached to every pipeline run.

    Matches the schema in ``docs/schemas/processing-report.schema.md``.
    """

    tempify_version: str
    timestamp_utc: str
    method: str
    target_year: int
    structure_mode: str
    temporal_frequency: str
    detection_confidence: dict[str, float]
    pre_validation_summary: dict[str, int]
    post_validation_summary: dict[str, int] | None
    statistics: dict[str, dict[str, float]] | None
    inputs: tuple[Path, ...]
    outputs: tuple[Path, ...]
    dry_run: bool = field(default=False)
    notes: tuple[str, ...] = field(default_factory=tuple)


class ReportGenerator:
    """Build a :class:`ProcessingReport` from a pipeline run's outputs."""

    def build(
        self,
        config: PipelineConfig,
        detection: StructureDetectionResult,
        frequency: ResolutionResult,
        pre_validation: ValidationReport,
        post_validation: ValidationReport | None,
        outputs: tuple[Path, ...],
    ) -> ProcessingReport:
        """Assemble a :class:`ProcessingReport` from the run components."""
        notes: list[str] = []
        if config.dry_run:
            notes.append("[DRY_RUN] No interpolation, post-validation, or write occurred.")
        if config.force_method:
            notes.append(
                "Se aplicó --force-method; el método elegido no es recomendado "
                "científicamente para la variable detectada (ver attrs)."
            )
        # Pre-validation summary
        pre_summary = {
            "errors": len(pre_validation.errors),
            "warnings": len(pre_validation.warnings),
            "info": len(pre_validation.info_items),
        }
        post_summary: dict[str, int] | None = None
        if post_validation is not None:
            post_summary = {
                "errors": len(post_validation.errors),
                "warnings": len(post_validation.warnings),
                "info": len(post_validation.info_items),
            }
        return ProcessingReport(
            tempify_version=_tempify_version(),
            timestamp_utc=datetime.now(UTC).isoformat(timespec="seconds"),
            method=config.method,
            target_year=config.target_year,
            structure_mode=detection.structure_mode.value,
            temporal_frequency=frequency.frequency.value,
            detection_confidence={
                k: float(v)  # type: ignore[arg-type]
                for k, v in detection.confidence.items()
            },
            pre_validation_summary=pre_summary,
            post_validation_summary=post_summary,
            statistics=post_validation.statistics if post_validation is not None else None,
            inputs=detection.files,
            outputs=outputs,
            dry_run=config.dry_run,
            notes=tuple(notes),
        )

    def to_markdown(self, report: ProcessingReport) -> str:
        """Render ``report`` as a Markdown document (Spanish)."""
        prefix = "[DRY_RUN] " if report.dry_run else ""
        lines: list[str] = [
            f"# {prefix}Reporte de procesamiento tempify",
            "",
            f"- **Versión tempify:** {report.tempify_version}",
            f"- **Timestamp UTC:** {report.timestamp_utc}",
            f"- **Método:** `{report.method}`",
            f"- **Año destino:** {report.target_year}",
            f"- **Modo de estructura:** {report.structure_mode}",
            f"- **Frecuencia temporal inferida:** {report.temporal_frequency}",
            "",
            "## Confianza de detección",
            "",
        ]
        for key, value in report.detection_confidence.items():
            lines.append(f"- {key}: {value:.2f}")
        lines.extend(
            [
                "",
                "## Validación pre-procesamiento",
                "",
                f"- Errores: {report.pre_validation_summary['errors']}",
                f"- Advertencias: {report.pre_validation_summary['warnings']}",
                f"- Info: {report.pre_validation_summary['info']}",
                "",
            ]
        )
        if report.post_validation_summary is not None:
            lines.extend(
                [
                    "## Validación post-procesamiento",
                    "",
                    f"- Errores: {report.post_validation_summary['errors']}",
                    f"- Advertencias: {report.post_validation_summary['warnings']}",
                    f"- Info: {report.post_validation_summary['info']}",
                    "",
                ]
            )
        lines.extend(["## Archivos de entrada", ""])
        for p in report.inputs:
            lines.append(f"- `{p}`")
        lines.extend(["", "## Archivos de salida", ""])
        for p in report.outputs:
            lines.append(f"- `{p}`")
        if report.notes:
            lines.extend(["", "## Notas", ""])
            for note in report.notes:
                lines.append(f"- {note}")
        return "\n".join(lines) + "\n"

    def to_json(self, report: ProcessingReport) -> str:
        """Render ``report`` as a JSON document (for machine consumers)."""
        payload: dict[str, Any] = {
            "tempify_version": report.tempify_version,
            "timestamp_utc": report.timestamp_utc,
            "method": report.method,
            "target_year": report.target_year,
            "structure_mode": report.structure_mode,
            "temporal_frequency": report.temporal_frequency,
            "detection_confidence": report.detection_confidence,
            "pre_validation_summary": report.pre_validation_summary,
            "post_validation_summary": report.post_validation_summary,
            "statistics": report.statistics,
            "inputs": [str(p) for p in report.inputs],
            "outputs": [str(p) for p in report.outputs],
            "dry_run": report.dry_run,
            "notes": list(report.notes),
        }
        return json.dumps(payload, indent=2, ensure_ascii=False)
