"""Detection layer (Capa 2) for tempify.

Identifies the structure of the input (single stack, monolayer
collection, explicit list) and infers temporal frequency before any
data is loaded into memory. The frequency-resolver sub-module is in
:mod:`tempify.detection.frequency`; this top-level package re-exports
the structure detector for ergonomic imports.
"""

from tempify.detection.structure import (
    SIDECAR_EXTENSIONS,
    AmbiguousStructureError,
    EmptyInputError,
    HeterogeneousFilesError,
    StructureConfidencePartial,
    StructureDetectionError,
    StructureDetectionResult,
    StructureDetector,
    StructureMode,
)

__all__ = [
    "SIDECAR_EXTENSIONS",
    "AmbiguousStructureError",
    "EmptyInputError",
    "HeterogeneousFilesError",
    "StructureConfidencePartial",
    "StructureDetectionError",
    "StructureDetectionResult",
    "StructureDetector",
    "StructureMode",
]
