"""ValidationReport dataclass and supporting enums.

Implements the canonical shape defined in
``docs/schemas/validation-report.schema.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class CheckSeverity(StrEnum):
    """Severity of an individual validation check."""

    INFO = "info"
    WARN = "warn"
    ERROR = "error"


class CheckPhase(StrEnum):
    """Phase in which a check was evaluated."""

    PRE_PROCESS = "pre"
    POST_PROCESS = "post"


@dataclass(frozen=True, slots=True)
class CheckResult:
    """Outcome of a single validation check.

    Attributes
    ----------
    check_id : str
        Stable code from ``tempify.validation._codes`` (e.g. ``'GEO-001'``).
    name : str
        Short human-readable name (e.g. ``'CRS coherence'``).
    severity : CheckSeverity
        ``info`` / ``warn`` / ``error``.
    phase : CheckPhase
        ``pre`` or ``post`` (per validation policy in ADR-0007 + design).
    passed : bool
        ``True`` iff the check did not flag any anomaly.
    message : str
        Spanish-language explanation visible to the end user.
    details : dict[str, Any]
        Optional structured payload for downstream consumers (e.g.,
        reporters, the GUI).
    """

    check_id: str
    name: str
    severity: CheckSeverity
    phase: CheckPhase
    passed: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Aggregate result of all validation checks (pre and post)."""

    checks: tuple[CheckResult, ...]
    statistics: dict[str, dict[str, float]] = field(default_factory=dict)

    @property
    def errors(self) -> tuple[CheckResult, ...]:
        return tuple(c for c in self.checks if c.severity == CheckSeverity.ERROR)

    @property
    def warnings(self) -> tuple[CheckResult, ...]:
        return tuple(c for c in self.checks if c.severity == CheckSeverity.WARN)

    @property
    def info_items(self) -> tuple[CheckResult, ...]:
        return tuple(c for c in self.checks if c.severity == CheckSeverity.INFO)

    @property
    def pre_passed(self) -> bool:
        """True iff no PRE_PROCESS check has severity ERROR."""
        return not any(
            c.phase == CheckPhase.PRE_PROCESS and c.severity == CheckSeverity.ERROR
            for c in self.checks
        )

    @property
    def post_passed(self) -> bool:
        """True iff no POST_PROCESS check has severity ERROR."""
        return not any(
            c.phase == CheckPhase.POST_PROCESS and c.severity == CheckSeverity.ERROR
            for c in self.checks
        )

    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
