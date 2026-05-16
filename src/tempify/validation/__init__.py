"""Validation layer (Capa 3) for tempify.

Performs pre-process geospatial coherence checks (fail-fast), method/variable
compatibility checks (with precipitation rejection per ADR-0004),
post-interpolation validation (warn-and-continue, with monthly mean
preservation per ADR-0010), per-band statistical reporting, and variable
profile matching.

The layer exposes typed exceptions and the canonical :class:`ValidationReport`
shape consumed by the pipeline and the processing report.
"""

from tempify.validation.compatibility import MethodVariableCompatibilityChecker
from tempify.validation.errors import (
    GeospatialIncoherenceError,
    MethodVariableIncompatibilityError,
    PreValidationError,
    UnknownVariableProfileError,
    ValidationTempifyError,
)
from tempify.validation.geocoherence import (
    CANONICAL_TOLERANCES,
    GeospatialCoherenceValidator,
    Tolerances,
)
from tempify.validation.post import PostInterpolationValidator
from tempify.validation.profiles import (
    VariableProfile,
    VariableProfileMatcher,
    iter_builtin_profiles,
)
from tempify.validation.report import (
    CheckPhase,
    CheckResult,
    CheckSeverity,
    ValidationReport,
)
from tempify.validation.statistics import StatisticalReporter

__all__ = [
    "CANONICAL_TOLERANCES",
    "CheckPhase",
    "CheckResult",
    "CheckSeverity",
    "GeospatialCoherenceValidator",
    "GeospatialIncoherenceError",
    "MethodVariableCompatibilityChecker",
    "MethodVariableIncompatibilityError",
    "PostInterpolationValidator",
    "PreValidationError",
    "StatisticalReporter",
    "Tolerances",
    "UnknownVariableProfileError",
    "ValidationReport",
    "ValidationTempifyError",
    "VariableProfile",
    "VariableProfileMatcher",
    "iter_builtin_profiles",
]
