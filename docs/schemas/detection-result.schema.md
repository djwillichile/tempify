# DetectionResult Schema

> Documento normativo del shape del dataclass `DetectionResult` y sus tipos auxiliares (`StructureMode`, `TemporalFrequency`, `DetectionConfidence`). Este schema es el contrato entre la Capa 2 (Detection) y sus consumidores aguas abajo (Validation, Interpolation, Pipeline, GUI, Reporting). Cualquier divergencia con este documento debe resolverse vía nuevo ADR, no mediante cambios locales.

## Propósito

`DetectionResult` es la salida unificada de la Capa 2 (`tempify.detection`) según `steering/architecture.md`. Representa el estado del conocimiento del sistema sobre QUÉ son los datos antes de procesarlos: cómo están estructurados en disco (modo A/B/C), a qué frecuencia temporal corresponden, qué variable física codifican, y cuál es la confianza por componente en cada una de esas inferencias.

El dataclass se construye una vez tras la fase de detección y se propaga (inmutable) por todo el pipeline. Es consumido por:

- **Validation** (Capa 3): usa `variable_profile` y `files` para verificar coherencia geoespacial y compatibilidad método-variable.
- **Interpolation** (Capa 4): usa `temporal_frequency` y `variable_profile` para parametrizar el motor.
- **Pipeline** (`specs/pipeline/requirements.md` REQ-007): incluye `confidence` y `evidence` en el `ProcessingReport`, emite warning si `confidence.overall < 0.6`.
- **GUI** (`specs/gui/requirements.md` REQ-007): muestra `confidence.overall` como score principal con desglose por componente.
- **Reporting**: serializa el objeto completo (con enums como strings) en el reporte de procedencia.

El contrato canónico de `confidence` está fijado en [ADR-0008](../adr/0008-confidence-scoring-and-detection-result-contract.md).

## Shape canónico

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal, TypedDict


class StructureMode(str, Enum):
    """Modo estructural detectado por StructureDetector.

    Hereda de str para serialización transparente a JSON y a
    DataArray.attrs sin conversión manual.
    """
    SINGLE_STACK = "A"          # Un único archivo multibanda
    MONOLAYER_COLLECTION = "B"  # N archivos monocapa coherentes
    EXPLICIT_LIST = "C"         # Lista pasada por el usuario


class TemporalFrequency(str, Enum):
    """Frecuencia temporal inferida por TemporalFrequencyResolver."""
    MONTHLY = "monthly"
    DAILY = "daily"
    WEEKLY = "weekly"
    HOURLY = "hourly"
    YEARLY = "yearly"
    CLIMATOLOGICAL = "climatological"  # 12 valores sin años (promedio climatico)


class DetectionConfidence(TypedDict):
    """Confianzas por componente. Contrato fijado por ADR-0008.

    Todas las claves son obligatorias en todos los modos.
    Valores en el intervalo cerrado [0.0, 1.0].
    """
    structure_mode: float           # Confianza en clasificacion A/B/C
    temporal_frequency: float       # Confianza en la frecuencia inferida
    temporal_frequency_tier: float  # Etiqueta numerica del tier ganador:
                                    #   1.0 = CF-conventions
                                    #   0.9 = nomenclatura
                                    #   0.7 = heuristica por conteo
                                    #   0.4 = callback interactivo
    variable_profile: float         # Confianza en VariableProfileMatcher
    homogeneity: float              # Coherencia geoespacial entre archivos (modo B)
    overall: float                  # Media ponderada (pesos en ADR-0008)


@dataclass(frozen=True)
class DetectionResult:
    """Salida unificada de la Capa 2 Detection.

    Inmutable (frozen=True). No contiene los xr.DataArray, solo Path y
    metadatos; la carga efectiva la realiza la Capa 1 (IO) cuando el
    pipeline lo solicita.
    """
    structure_mode: StructureMode
    temporal_frequency: TemporalFrequency
    variable_profile: "VariableProfile"   # Tipo opaco, ver variable-profile.schema.yaml
    files: list[Path]
    confidence: DetectionConfidence
    evidence: dict[str, str]              # Texto explicativo por tier (para reporte)
    # Eje temporal canónico (ADR-0015). Ensamblado por el Pipeline tras la
    # fase `detect`, no por la Capa 2 directamente; las layers productoras
    # (StructureDetector, TemporalFrequencyResolver) entregan los inputs y
    # el Pipeline materializa el axis final aquí.
    time_axis: list["datetime"] | None = None
    time_bnds: list[tuple["datetime", "datetime"]] | None = None
    calendar_agnostic: bool = False
    monthly_anchor: Literal["midpoint", "start", "end", "custom"] = "midpoint"
```

#### Semántica de los nuevos campos (ADR-0015)

- **`time_axis`:** lista de `datetime` correspondientes a cada paso temporal del stack, expresados en la convención **midpoint** del periodo de agregación por defecto (per ADR-0015 §1). Cuando `monthly_anchor != "midpoint"`, el axis sigue la convención indicada (`start`, `end` o `custom`). `None` solo durante la construcción intermedia: en el `DetectionResult` final que sale del Pipeline siempre está poblado.
- **`time_bnds`:** lista de bounds `[first_day_of_period, first_day_of_next_period)` por paso, requerido para output CF con la variable auxiliar `time:bounds` (ADR-0015 §2). Longitud igual a `time_axis`.
- **`calendar_agnostic`:** `True` cuando el axis se sintetizó sin información de año real (proxy 2026 u otro año testigo), típico de WorldClim y otros productos de climatología sin coordenada temporal explícita. Consumidores aguas abajo deben tratar el año del axis como simbólico.
- **`monthly_anchor`:** la convención efectivamente aplicada al construir `time_axis`. Permite trazabilidad inversa: dado el `DetectionResult` se reconstruye qué política temporal materializó el axis.

### Mapeo con `architecture.md`

`steering/architecture.md` § Capa 2 declara el dataclass con `structure_mode: Literal["A", "B", "C"]` y `confidence: dict[str, float]`. Este schema reemplaza el `Literal` por el enum `StructureMode` (cuyos valores son los mismos strings `"A"`, `"B"`, `"C"`, manteniendo compatibilidad estructural) y tipa `confidence` como `DetectionConfidence` (un `TypedDict` que sigue siendo asignable a `dict[str, float]`). No es breaking change: ambos son evoluciones de tipado, no de runtime shape.

## Reglas semánticas

Reglas obligatorias que cualquier productor o consumidor del `DetectionResult` debe respetar.

1. **Orden canónico de `files`.** Siempre ordenada por nombre lexicográfico canónico (NFC, Unicode Normalization Form C) para reproducibilidad bit-exact (alineado con ADR-0007). Los productores deben aplicar `pathlib.Path.name` normalizado a NFC antes de ordenar; el orden en disco del sistema operativo no es contractual.

2. **Inmutabilidad.** `DetectionResult` es `frozen=True`. Cualquier corrección (por ejemplo, un override interactivo de la frecuencia tras detección) genera un nuevo objeto, no muta el existente. Esto permite cachear y comparar resultados por identidad estructural.

3. **Claves obligatorias en `confidence`.** Las seis claves del `DetectionConfidence` están presentes siempre, en todos los modos. Cuando una clave no aplica al modo, se asigna el valor neutro documentado (típicamente `1.0`) en lugar de omitirla. Por ejemplo, en modo A (un solo archivo) no hay homogeneidad entre archivos, por lo que `confidence.homogeneity = 1.0` por construcción.

4. **Rango de valores.** Todas las claves de `confidence` están en `[0.0, 1.0]` cerrado. Validación obligatoria en `__post_init__` (ADR-0008, notas de implementación).

5. **Umbral de warning.** Si `confidence.overall < 0.6`, el pipeline emite un warning explícito en `ProcessingReport`. El umbral es contractual (ADR-0008) y solo cambia vía nuevo ADR.

6. **`evidence`: textos cortos por componente.** El campo `evidence` es un `dict[str, str]` con entradas opcionales pero estandarizadas. Cada string es corto (límite recomendado <200 caracteres) y describe la señal observable que justifica el componente correspondiente. Ejemplos canónicos:

   - `evidence["temporal_frequency"] = "CF time:units = 'months since 1970-01-01'"`
   - `evidence["structure_mode"] = "12 archivos TIF coherentes, mismo CRS EPSG:4326"`
   - `evidence["variable_profile"] = "standard_name='air_temperature', units='K' (exact match)"`

   El reporte de procedencia (`ProcessingReport`) consume estos strings tal cual. No deben contener saltos de línea ni caracteres de escape.

7. **Separación datos / metadatos.** El dataclass NO contiene los `xr.DataArray`. Solo los `Path` y los metadatos de detección. Los datos se cargan después por la Capa 1 (IO handlers) cuando el pipeline los solicita explícitamente.

8. **`temporal_frequency_tier` es etiqueta, no probabilidad.** A pesar de tener valores en `[0.0, 1.0]`, esta clave es un encoding numérico discreto del tier ganador, NO una probabilidad. No entra en la media ponderada de `overall` (ADR-0008, función `compute_overall_confidence`). Sus únicos valores válidos son `{1.0, 0.9, 0.7, 0.4}`.

9. **Ensamblaje canónico de `time_axis` y `time_bnds`.** El Pipeline (Capa 5) ensambla `time_axis` y `time_bnds` a partir del `ResolutionResult` que produce la Capa 2 (`temporal-frequency-resolver`) y los stamps del propio `DetectionResult` (e.g. `band_descriptions` cuando es modo A multi-banda GeoTIFF, lista de filenames cuando es modo B/C). La Capa 2 no rellena estos campos por sí sola: el `StructureDetectionResult` y el `ResolutionResult` proporcionan los insumos, y el Pipeline materializa el axis final antes de pasar el `DetectionResult` completo a Validation e Interpolation. La política de anchor por defecto (`"midpoint"`) y el override por usuario están fijados en ADR-0015. Cuando el resolver no logra inferir años reales, el Pipeline aplica un año proxy (2026 por convención del módulo) y marca `calendar_agnostic=True`.

## Compatibilidad con xarray

Cuando `DetectionResult` se serializa hacia `xr.DataArray.attrs["tempify_detection"]` del DataArray procesado:

- Los enums (`StructureMode`, `TemporalFrequency`) se serializan como sus valores `str` subyacentes (`"A"`, `"monthly"`, etc.), aprovechando que ambos heredan de `str`. Esto los hace compatibles con NetCDF y Zarr sin codecs custom.
- `files` se serializa como lista de strings (resultado de `str(Path)`), no como `Path` (los `Path` no son CF-serializables).
- `confidence` se serializa como JSON-string (un `dict[str, float]` plano), embebido en un único atributo `tempify_detection_confidence`. Esto evita la fragmentación en N atributos top-level y respeta el límite de longitud de atributos NetCDF clásico.
- `evidence` se serializa también como JSON-string en `tempify_detection_evidence`, por las mismas razones.
- `variable_profile` se serializa como su identificador (`profile.name`), no como el objeto completo (el perfil completo se reconstruye al releer, consultando `profiles/*.yaml` por nombre).

El método helper canónico es `DetectionResult.to_attrs(self) -> dict[str, str | float]` y su inverso `DetectionResult.from_attrs(attrs: Mapping) -> DetectionResult`.

## Casos límite

Casos que el contrato cubre explícitamente para evitar ambigüedades en consumidores.

- **Modo `EXPLICIT_LIST` (C).** Cuando el usuario provee una lista explícita de archivos asumiendo responsabilidad sobre su coherencia, `confidence.homogeneity` se fuerza a `1.0` (el sistema no verifica). El campo `evidence["homogeneity"]` debe documentar este hecho con un string del tipo `"user-asserted: explicit list, homogeneity not verified"`.

- **`TemporalFrequency.CLIMATOLOGICAL`.** Aplica cuando se detectan exactamente 12 archivos sin información de año (ej. WorldClim long-term means). Distinto de `MONTHLY` (12 valores asociados a un año específico). La distinción es contractual: los métodos de interpolación tratan ambos casos con preservación de media mensual, pero el reporte y la GUI los etiquetan distinto.

- **Modo `SINGLE_STACK` (A) con un solo archivo multibanda.** `confidence.homogeneity = 1.0` por construcción (no hay archivos múltiples que comparar). `len(files) == 1`.

- **Tier `interactive_callback`.** Cuando el `TemporalFrequencyResolver` recurre a callback (CLI prompt o parámetro API), `confidence.temporal_frequency = 0.4` y `confidence.temporal_frequency_tier = 0.4`. El sistema no puede atestar la corrección del input humano; el bajo score es intencional para forzar visibilidad en el reporte.

- **Frecuencias mixtas o no detectables.** Si el resolver agota la jerarquía y el callback se rechaza, el detector falla con excepción (`FrequencyResolutionError`); no se permite un `DetectionResult` con `temporal_frequency = None`. Esta política está alineada con `specs/temporal-frequency-resolver/requirements.md`.

- **`confidence.overall` exactamente en el umbral.** El warning se dispara con `<` estricto, no `<=`. Un `overall == 0.6` no emite warning.

## Validación obligatoria

El constructor (`__post_init__`) debe validar:

1. Todas las seis claves de `DetectionConfidence` están presentes.
2. Cada valor de `confidence` está en `[0.0, 1.0]`.
3. `confidence.temporal_frequency_tier` es uno de `{1.0, 0.9, 0.7, 0.4}`.
4. `files` es no-vacío.
5. En modos A y C: `confidence.homogeneity == 1.0` exactamente.
6. `structure_mode` y `temporal_frequency` son instancias de los enums correspondientes (no strings crudos), aunque la serialización los aplane después.

Cualquier violación lanza `ValueError` con mensaje accionable indicando qué invariante falló.

## Referencias

- [ADR-0008](../adr/0008-confidence-scoring-and-detection-result-contract.md): Confidence scoring and DetectionResult contract (contrato canónico).
- [ADR-0007](../adr/0007-reproducibility-policy.md): Política de reproducibilidad (justifica orden NFC y determinismo del cómputo).
- [ADR-0015](../adr/0015-monthly-value-temporal-placement.md): Posicionamiento temporal de valores agregados (midpoint convention, `time_bnds`, override por usuario).
- CF Conventions 7.4 (Climatological Statistics): https://cfconventions.org/Data/cf-conventions/cf-conventions-1.10/cf-conventions.html#climatological-statistics
- `steering/architecture.md` § Capa 2 Detection.
- `specs/structure-detection/requirements.md` REQ-006.
- `specs/temporal-frequency-resolver/requirements.md` REQ-003.
- `specs/pipeline/requirements.md` REQ-007.
- `specs/gui/requirements.md` REQ-007.
- `docs/schemas/variable-profile.schema.yaml` (tipo opaco `VariableProfile`).
- PEP 589 (TypedDict): https://peps.python.org/pep-0589/
