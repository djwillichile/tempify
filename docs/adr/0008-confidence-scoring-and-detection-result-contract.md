# ADR-0008: Confidence scoring and DetectionResult contract

**Status:** Accepted
**Date:** 2026-05-16
**Decision-makers:** Guillermo Fuentes-Jaque

## Contexto

El contrato de la Capa 2 (Detection) presenta una discrepancia entre `steering/architecture.md` y las specs Draft de los módulos consumidores y productores del `DetectionResult`:

- `steering/architecture.md` (Capa 2) declara `DetectionResult.confidence: dict[str, float]`, es decir, un mapa de componentes con sus respectivas confianzas.
- `specs/structure-detection/requirements.md` REQ-006 declara `confidence` como un único score escalar entre 0 y 1, sin estructura interna.
- `specs/temporal-frequency-resolver/requirements.md` REQ-003 menciona un umbral 0.9 sobre una "confianza" sin definir su origen ni su tipo.
- `specs/pipeline/requirements.md` REQ-007 obliga a reportar "confidence scores" (plural) en el `ProcessingReport` y reconoce explícitamente el riesgo de drift por la falta de contrato del dict.
- `specs/gui/requirements.md` REQ-007 muestra el confidence en el preview, sin un campo canónico al que asociarse.

El contrato actual es ambiguo y rompe el pipeline: el reporte de procedencia (`ProcessingReport`) no puede inspeccionar un dict no contractualizado de manera estable, la GUI no sabe qué clave mostrar, y los resolvers internos no tienen un destino canónico para sus señales (tier, evidencia, votos). Sin un shape único acordado, cada capa terminará reinterpretando el contrato.

Este ADR resuelve la discrepancia fijando el shape canónico y el algoritmo de cómputo determinista de cada componente.

## Decisión

**Decisión doble:**

### 1. Shape canónico de `DetectionResult.confidence`

`DetectionResult.confidence` es un `dict[str, float]` (modelado como `TypedDict` para tipado fuerte sin perder compatibilidad con `dict`) con las siguientes claves obligatorias, todas con valores en el intervalo cerrado `[0.0, 1.0]`:

| Clave | Significado |
|---|---|
| `structure_mode` | Confianza en la clasificación A/B/C de `StructureDetector`. |
| `temporal_frequency` | Confianza en la frecuencia temporal inferida por `TemporalFrequencyResolver`. |
| `temporal_frequency_tier` | Codifica numéricamente el tier de evidencia que ganó: `1.0` = CF-conventions, `0.9` = nomenclatura, `0.7` = heurística por conteo, `0.4` = callback interactivo. |
| `variable_profile` | Confianza en la identificación de la variable por `VariableProfileMatcher`. |
| `homogeneity` | Confianza en la coherencia geoespacial de los archivos (modo B). En modos A y C se asigna `1.0` por construcción. |
| `overall` | Media ponderada de las claves anteriores. Si `overall < 0.6`, el pipeline emite un warning explícito en `ProcessingReport`. |

Las claves son obligatorias en todos los modos. Cuando una clave no aplica al modo, el detector asigna el valor neutro documentado (típicamente `1.0`) en lugar de omitirla, para preservar la estabilidad del schema.

### 2. Algoritmo de cómputo

Mezcla determinista basada en señales positivas/negativas (no ML). Reproducible bit-exact dado el mismo input y los mismos pesos. Pseudocódigo de referencia:

```python
def compute_structure_mode_confidence(files, mode_detected) -> float:
    """Confianza en la clasificación A/B/C."""
    score = 0.0
    # +0.4 si todos los archivos tienen mismo formato
    if all_same_format(files):
        score += 0.4
    # +0.3 si todos tienen mismo CRS
    if all_same_crs(files):
        score += 0.3
    # +0.2 si todos tienen misma extensión espacial
    if all_same_extent(files):
        score += 0.2
    # +0.1 si el conteo coincide con un tier conocido (12, 52, 365, 366)
    if len(files) in {12, 52, 365, 366}:
        score += 0.1
    return min(score, 1.0)


def compute_temporal_frequency_confidence(tier_used, evidence) -> float:
    """Confianza en la frecuencia temporal inferida."""
    if tier_used == "cf_units":
        # CF-conventions: 1.0 si match exacto, 0.95 si parcial (e.g. falta calendar)
        return 1.0 if evidence.match == "exact" else 0.95
    if tier_used == "nomenclature":
        # Regex catalog: max de todos los scores de patrones, tope 0.9
        return min(max(evidence.regex_scores), 0.9)
    if tier_used == "count_heuristic":
        # Heurística por conteo: 0.7 fijo (señal débil pero útil)
        return 0.7
    if tier_used == "interactive_callback":
        # Depende del usuario; el sistema no puede atestar su corrección
        return 0.4
    raise ValueError(f"Unknown tier: {tier_used}")


def compute_temporal_frequency_tier(tier_used) -> float:
    """Codificación numérica del tier ganador (no es probabilidad, es etiqueta)."""
    return {
        "cf_units": 1.0,
        "nomenclature": 0.9,
        "count_heuristic": 0.7,
        "interactive_callback": 0.4,
    }[tier_used]


def compute_variable_profile_confidence(matches) -> float:
    """Confianza en la variable: combina match exacto de standard_name y units."""
    score = 0.0
    if matches.standard_name_exact:
        score += 0.5
    elif matches.standard_name_fuzzy:
        score += 0.3
    if matches.units_compatible:
        score += 0.3
    if matches.long_name_match:
        score += 0.2
    return min(score, 1.0)


def compute_homogeneity_confidence(files, mode) -> float:
    """En modo B: fracción de archivos coherentes respecto al primero."""
    if mode in {"A", "C"}:
        return 1.0
    coherent = count_coherent_files(files, reference=files[0])
    return coherent / len(files)


def compute_overall_confidence(components: dict[str, float]) -> float:
    """Media ponderada. Pesos fijos y versionados en el código."""
    weights = {
        "structure_mode": 0.25,
        "temporal_frequency": 0.30,
        "variable_profile": 0.25,
        "homogeneity": 0.20,
    }
    # `temporal_frequency_tier` es etiqueta, no entra en la media.
    return sum(components[k] * w for k, w in weights.items())
```

Los pesos están versionados en código y solo cambian vía nuevo ADR (no son configuración runtime).

## Alternativas consideradas

| Alternativa | Decisión | Justificación |
|---|---|---|
| `confidence: float` (escalar único, como dice REQ-006 actual) | Rechazada | Pierde granularidad: no permite distinguir si la incertidumbre viene de structure, frequency o variable; la GUI no puede mostrar desglose útil; el reporte no es accionable. |
| `confidence: Decimal` (precisión arbitraria) | Rechazada | Overkill: las confianzas son señales heurísticas, no cantidades financieras. Añade fricción de tipado (Decimal vs float en numpy/xarray) sin beneficio. |
| `confidence: dict[str, float]` con claves canónicas (esta decisión) | Aceptada | Granularidad por componente, compatible con JSON-serialization para el `ProcessingReport`, fácil de mostrar en GUI, extensible (nuevas claves sin breaking changes si se mantienen las obligatorias). |
| Dataclass `DetectionConfidence` con atributos | Rechazada | Incompatible con la firma actual `dict[str, float]` en `architecture.md`; obliga a refactor amplio; menos ergonómico para serialización a JSON. Se opta por `TypedDict` como compromiso. |

## Consecuencias

### Positivas

- Contrato único: pipeline, GUI y reporte consumen el mismo schema.
- Determinismo: el algoritmo es función pura de las señales observables; bit-exact reproducible (alineado con ADR-0007).
- Trazabilidad: `temporal_frequency_tier` documenta qué tier ganó en cada ejecución, facilitando debugging y auditoría.

### Negativas / enmiendas necesarias

Este contrato impone enmiendas a las siguientes specs Draft:

- `specs/structure-detection/requirements.md` REQ-006: cambiar `confidence` de `float` a `dict[str, float]` con las claves canónicas; añadir REQ que obligue a calcular `structure_mode` y `homogeneity` por este ADR.
- `specs/temporal-frequency-resolver/requirements.md` REQ-003: el umbral 0.9 se reformula como tope del tier nomenclatura; añadir REQ que obligue a poblar `temporal_frequency` y `temporal_frequency_tier`.
- `specs/pipeline/requirements.md` REQ-007: reportar tanto `overall` como cada componente per-key; emitir warning si `overall < 0.6`.
- `specs/gui/requirements.md`: mostrar `overall` como score principal en el preview, con tooltip o panel expandible que liste cada componente.

### Riesgos

- Si en el futuro se añade un nuevo componente (e.g. `calendar_confidence`), debe agregarse vía nuevo ADR; las claves obligatorias actuales no pueden eliminarse sin breaking change explícito.

## Notas de implementación

- Definir `DetectionConfidence` como `TypedDict` en `tempify.detection.types`:

```python
from typing import TypedDict

class DetectionConfidence(TypedDict):
    structure_mode: float
    temporal_frequency: float
    temporal_frequency_tier: float
    variable_profile: float
    homogeneity: float
    overall: float
```

- `TypedDict` mantiene compatibilidad estructural con `dict[str, float]` declarado en `architecture.md`, satisface mypy/pyright para acceso por clave, y serializa transparentemente a JSON.
- Validación de invariantes (claves presentes, rangos `[0.0, 1.0]`) en el constructor de `DetectionResult` vía `__post_init__`.
- Tests obligatorios: `test_confidence_keys_present`, `test_confidence_values_in_range`, `test_overall_below_threshold_warns`, `test_tier_encoding_stable`.
- Los pesos de `overall` viven en una constante del módulo (`_CONFIDENCE_WEIGHTS`) y se versionan con el código; cambiarlos requiere nuevo ADR.

## Referencias

- ADR-0001: xarray como abstracción central (define el flujo `DetectionResult` → pipeline).
- ADR-0007: Política de reproducibilidad (justifica el cómputo determinista).
- `steering/architecture.md` § Capa 2 Detection.
- `specs/structure-detection/requirements.md` REQ-006.
- `specs/temporal-frequency-resolver/requirements.md` REQ-003.
- `specs/pipeline/requirements.md` REQ-007 y tabla de riesgos.
- `specs/gui/requirements.md` REQ-007.
- PEP 589 (TypedDict): https://peps.python.org/pep-0589/
