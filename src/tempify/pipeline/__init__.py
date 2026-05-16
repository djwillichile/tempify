"""Pipeline layer (Capa 5) for tempify.

End-to-end orchestrator. Reads inputs, detects structure and temporal
frequency, validates coherence, interpolates with the requested method,
runs post-validation, writes outputs and emits a ``ProcessingReport``
with full provenance.

Per the architectural rule, this layer is the ONLY one that imports
from all the other tempify layers. It does NOT import ``typer``,
``rich``, ``sys.stdin`` or any UI dependency.
"""

from tempify.pipeline.callbacks import (
    PHASES,
    FrequencyResolverProtocol,
    PipelinePhase,
    ProgressCallback,
)
from tempify.pipeline.config import PipelineConfig
from tempify.pipeline.core import TempifyPipeline
from tempify.pipeline.errors import (
    EXIT_CODES,
    InvalidConfigError,
    PipelineInterpolationError,
    PipelinePreValidationError,
    PipelineReportError,
    PipelineWriteError,
    TempifyPipelineError,
)
from tempify.pipeline.report import ProcessingReport, ReportGenerator
from tempify.pipeline.result import PipelineResult

__all__ = [
    "EXIT_CODES",
    "PHASES",
    "FrequencyResolverProtocol",
    "InvalidConfigError",
    "PipelineConfig",
    "PipelineInterpolationError",
    "PipelinePhase",
    "PipelinePreValidationError",
    "PipelineReportError",
    "PipelineResult",
    "PipelineWriteError",
    "ProcessingReport",
    "ProgressCallback",
    "ReportGenerator",
    "TempifyPipeline",
    "TempifyPipelineError",
]
