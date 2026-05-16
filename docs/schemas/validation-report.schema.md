# ValidationReport Schema

## Propósito

Salida unificada de la Capa 3 Validation (pre y post-interpolación). Consumida por Pipeline para fail-fast (pre) o warn-and-continue (post) y por el ReportGenerator para el reporte final.

## Shape canónico

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal

class CheckSeverity(str, Enum):
    INFO = "info"
    WARN = "warn"
    ERROR = "error"

class CheckPhase(str, Enum):
    PRE_PROCESS = "pre"   # fail-fast
    POST_PROCESS = "post" # warn-and-continue

@dataclass(frozen=True)
class CheckResult:
    check_id: str        # ej. "GEO-001", "POST-001"
    name: str            # ej. "CRS coherence"
    severity: CheckSeverity
    phase: CheckPhase
    passed: bool
    message: str         # mensaje en español
    details: dict[str, object] = field(default_factory=dict)

@dataclass(frozen=True)
class ValidationReport:
    checks: list[CheckResult]
    pre_passed: bool          # all PRE_PROCESS checks passed (ignoring INFO)
    post_passed: bool         # all POST_PROCESS ERROR-level passed
    warnings: list[CheckResult]    # severity==WARN
    errors: list[CheckResult]      # severity==ERROR
    statistics: dict[str, dict[str, float]]  # por banda: min/max/mean/std/nan_pct

    def failed_errors(self) -> list[CheckResult]: ...
    def has_warnings(self) -> bool: ...
```

## Catálogo de códigos de error (mínimo)

| ID | Descripción | Phase | Severidad típica |
|---|---|---|---|
| GEO-001 | CRS inconsistente entre archivos | pre | ERROR |
| GEO-002 | Extent inconsistente entre archivos | pre | ERROR |
| GEO-003 | Resolución inconsistente | pre | ERROR |
| GEO-004 | NoData inconsistente | pre | ERROR |
| GEO-005 | Dimensiones inconsistentes | pre | ERROR |
| COMPAT-001 | Método no permitido para variable | pre | ERROR |
| COMPAT-002 | Precipitación con método suave | pre | ERROR |
| COMPAT-003 | Override `--force-method` activo | pre | WARN |
| POST-001 | Conservación de media mensual fuera de tolerancia | post | WARN |
| POST-002 | Continuidad cíclica rota | post | WARN |
| POST-003 | Valor fuera de rango físico declarado en perfil | post | WARN |
| POST-004 | NaN inesperado en output donde input tenía valor | post | ERROR |

## Estadísticas reportadas

Por cada banda temporal del input y output, el `StatisticalReporter` reporta:
- min, max, mean, std
- nan_pct (porcentaje de NaN sobre total de píxeles)
- count_valid

## Reglas semánticas

- `pre_passed = all(c.passed for c in checks if c.phase == PRE_PROCESS and c.severity != INFO)`.
- Si `pre_passed == False`, el Pipeline lanza `PreValidationError(report)` antes de interpolar.
- Si `post_passed == False`, el Pipeline emite warning pero continúa (per architecture.md política).
- `checks` está ordenada por `(phase, severity_desc, check_id)`.

## Referencias

- ADR-0009, ADR-0010.
- specs/validation/requirements.md.
