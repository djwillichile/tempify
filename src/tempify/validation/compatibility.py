"""Method-variable compatibility checker.

Per ADR-0004 (precipitation policy), smooth methods (Linear, PCHIP,
PCHIP+RM, Fourier) are not appropriate for precipitation. The checker
raises :class:`MethodVariableIncompatibilityError` by default; with
``force=True`` it instead emits a ``COMPAT-003`` WARN that the Pipeline
forwards to the output's provenance attrs.
"""

from __future__ import annotations

from tempify.validation._codes import (
    COMPAT_FORCE_OVERRIDE_USED,
    COMPAT_METHOD_NOT_ALLOWED,
    COMPAT_PRECIPITATION_SMOOTH,
)
from tempify.validation.errors import MethodVariableIncompatibilityError
from tempify.validation.profiles import VariableProfile
from tempify.validation.report import (
    CheckPhase,
    CheckResult,
    CheckSeverity,
)

SMOOTH_METHODS: frozenset[str] = frozenset(
    {"linear", "pchip", "pchip_mp", "fourier", "akima", "cubic"}
)


class MethodVariableCompatibilityChecker:
    """Verify that ``method`` is allowed by ``profile`` per ADR-0004."""

    def check(
        self,
        method: str,
        profile: VariableProfile,
        *,
        force: bool = False,
    ) -> CheckResult:
        """Return a CheckResult describing the compatibility verdict.

        If ``method not in profile.allowed_methods`` and ``force is False``,
        raises :class:`MethodVariableIncompatibilityError`. With
        ``force=True`` the check passes but emits severity WARN and code
        ``COMPAT-003`` so the violation is recorded in the report.
        """
        if method in profile.allowed_methods:
            return CheckResult(
                check_id=COMPAT_METHOD_NOT_ALLOWED,
                name="Method-variable compatibility",
                severity=CheckSeverity.INFO,
                phase=CheckPhase.PRE_PROCESS,
                passed=True,
                message=(f"El método '{method}' está permitido para la variable '{profile.name}'."),
                details={
                    "method": method,
                    "variable": profile.name,
                    "allowed": list(profile.allowed_methods),
                },
            )

        # Special case: smooth method on precipitation
        is_precip_smooth = profile.name == "precipitation" and method in SMOOTH_METHODS
        if force:
            check_id = (
                COMPAT_PRECIPITATION_SMOOTH if is_precip_smooth else COMPAT_FORCE_OVERRIDE_USED
            )
            return CheckResult(
                check_id=check_id,
                name="Method-variable compatibility (force override)",
                severity=CheckSeverity.WARN,
                phase=CheckPhase.PRE_PROCESS,
                passed=True,
                message=(
                    f"Se aplicó --force-method para el método '{method}' "
                    f"sobre la variable '{profile.name}'. El resultado NO es "
                    "científicamente recomendado y queda registrado en la "
                    "procedencia del output (ADR-0004)."
                ),
                details={
                    "method": method,
                    "variable": profile.name,
                    "allowed": list(profile.allowed_methods),
                    "force_method_used": True,
                },
            )

        raise MethodVariableIncompatibilityError(
            method=method,
            variable=profile.name,
            allowed=profile.allowed_methods,
        )
