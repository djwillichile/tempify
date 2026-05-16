"""Typed exceptions for the validation layer.

All exceptions carry a referenceable code attribute and a Spanish-language
human-readable message per NFR-005.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from tempify.validation.report import ValidationReport


class ValidationTempifyError(Exception):
    """Base class for all validation-layer errors."""

    code: ClassVar[str] = "TEMPIFY-VAL-000"


class PreValidationError(ValidationTempifyError):
    """Raised by the pipeline when a pre-process validation fails.

    Wraps a :class:`ValidationReport` so the caller can inspect the
    failing checks programmatically.
    """

    code: ClassVar[str] = "TEMPIFY-VAL-001"

    def __init__(self, report: ValidationReport) -> None:
        self.report = report
        errors_list = ", ".join(c.check_id for c in report.errors)
        super().__init__(
            f"La validación pre-procesamiento falló con los siguientes "
            f"chequeos en error: {errors_list or '(ninguno)'}. "
            "Consulte el atributo .report para el detalle."
        )


class GeospatialIncoherenceError(ValidationTempifyError):
    """Raised by GeospatialCoherenceValidator when rasters are not homogeneous."""

    code: ClassVar[str] = "TEMPIFY-VAL-002"

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(
            f"Inconsistencia geoespacial detectada: {reason}. "
            "tempify v0.1.0 no aplica reproyección automática; armonice los "
            "archivos antes de procesarlos."
        )


class MethodVariableIncompatibilityError(ValidationTempifyError):
    """Raised when a method is not allowed for a given variable profile."""

    code: ClassVar[str] = "TEMPIFY-VAL-003"

    def __init__(self, method: str, variable: str, allowed: tuple[str, ...]) -> None:
        self.method = method
        self.variable = variable
        self.allowed = allowed
        allowed_str = ", ".join(allowed) if allowed else "(ninguno)"
        super().__init__(
            f"El método '{method}' no está permitido para la variable "
            f"'{variable}'. Métodos permitidos: {allowed_str}. "
            "Use --force-method --i-know-what-i-am-doing en la CLI para "
            "anular esta restricción bajo su responsabilidad (ver ADR-0004)."
        )


class UnknownVariableProfileError(ValidationTempifyError):
    """Raised when no matching variable profile is found for a request."""

    code: ClassVar[str] = "TEMPIFY-VAL-004"

    def __init__(self, name: str, available: tuple[str, ...]) -> None:
        self.name = name
        self.available = available
        avail = ", ".join(available) if available else "(ninguno)"
        super().__init__(
            f"No existe un perfil de variable llamado '{name}'. Perfiles disponibles: {avail}."
        )
