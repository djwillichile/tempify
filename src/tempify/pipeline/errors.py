"""Typed exceptions and canonical exit codes for the pipeline layer."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

if TYPE_CHECKING:
    from tempify.validation.report import ValidationReport


class TempifyPipelineError(Exception):
    """Base class for pipeline-layer errors."""

    code: ClassVar[str] = "TEMPIFY-PIPE-000"


class PipelinePreValidationError(TempifyPipelineError):
    """Raised when pre-process validation flags ERROR severity."""

    code: ClassVar[str] = "TEMPIFY-PIPE-001"

    def __init__(self, report: ValidationReport) -> None:
        self.report = report
        codes = ", ".join(c.check_id for c in report.errors)
        super().__init__(
            "La validación pre-procesamiento falló. Chequeos en ERROR: "
            f"{codes or '(ninguno)'}. Consulte .report para el detalle."
        )


class PipelineInterpolationError(TempifyPipelineError):
    """Raised when the interpolator fails (wrapping the original exception)."""

    code: ClassVar[str] = "TEMPIFY-PIPE-002"


class PipelineWriteError(TempifyPipelineError):
    """Raised when persisting the output fails."""

    code: ClassVar[str] = "TEMPIFY-PIPE-003"


class PipelineReportError(TempifyPipelineError):
    """Raised when ``ReportGenerator`` cannot build the final report."""

    code: ClassVar[str] = "TEMPIFY-PIPE-004"


class InvalidConfigError(TempifyPipelineError):
    """Raised when ``PipelineConfig`` carries inconsistent options."""

    code: ClassVar[str] = "TEMPIFY-PIPE-005"


EXIT_CODES: Final[dict[str, int]] = {
    "ok": 0,
    "validation_failure": 1,
    "user_cancellation": 2,
    "internal_error": 3,
    "sigint": 130,
}
"""Canonical exit codes consumed by the CLI (per spec/cli)."""
