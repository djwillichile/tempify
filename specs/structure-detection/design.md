# Design — structure-detection

**Estado:** Draft
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-15

## 1. Visión técnica

La feature implementa la Capa 2 del pipeline (sub-módulo `tempify.detection.structure`) responsable de identificar el modo estructural del input (A, B, C) sin materializar datos. El entry point único es `StructureDetector`, una clase pequeña con un método `detect(source)` que devuelve un `StructureDetectionResult` (subconjunto del `DetectionResult` global, faltando todavía `temporal_frequency` y `variable_profile`, que son responsabilidad de otros resolvers en la misma capa).

La lógica se descompone en cuatro pasos puros: (1) normalización del input, (2) clasificación A/B/C por árbol de decisión, (3) verificación de homogeneidad para modo B vía tolerancias canónicas (ADR-0009, delegado al helper de `tempify.validation.geocoherence`), (4) cálculo determinista del confidence parcial (ADR-0008). El módulo no abre los rásteres: solo consume el `metadata(path) -> dict` que expone la Capa 1 (`io-handlers`), garantizando bajo coste y reproducibilidad.

## 2. Arquitectura propuesta

### Diagrama de componentes

```
                         StructureDetector.detect(source)
                                       │
                ┌──────────────────────┼──────────────────────┐
                ▼                      ▼                      ▼
        _normalize_source     _classify_mode_A_B_C     _filter_sidecars
        (Path | list[Path])   (decision tree)          (sidecar extensions)
                │                      │                      │
                └──────────────────────┴──────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────────┐
                  │ Mode A: header inspection (bands/time dim)  │
                  │ Mode B: geocoherence.is_homogeneous(...)    │
                  │ Mode C: pass-through (preserve order)       │
                  └─────────────────────────────────────────────┘
                                       │
                                       ▼
                  compute_structure_mode_confidence (ADR-0008)
                                       │
                                       ▼
                          StructureDetectionResult
                          (subconjunto de DetectionResult)
```

### Componentes nuevos

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| `StructureDetector` | `src/tempify/detection/structure.py` | Entry point; orquesta clasificación A/B/C, sidecar filter, homogeneidad, confidence. |
| `StructureMode` | `src/tempify/detection/types.py` | `StrEnum` (`"A"`, `"B"`, `"C"`) compartido con el schema canónico. |
| `StructureDetectionResult` | `src/tempify/detection/types.py` | Dataclass `frozen` con `structure_mode`, `files`, `confidence`, `evidence`, `metadata_index`. |
| `AmbiguityReport` | `src/tempify/detection/types.py` | Dataclass con grupos detectados, dimensiones ofensoras, diagnostics por archivo. |
| `StructureDetectionError` y subclases | `src/tempify/detection/errors.py` | `AmbiguousStructureError`, `EmptyInputError`, `HeterogeneousFilesError`. |
| `SIDECAR_EXTENSIONS` | `src/tempify/detection/constants.py` | Frozenset de extensiones canónicas a ignorar. |
| `compute_structure_mode_confidence` | `src/tempify/detection/confidence.py` | Pseudocódigo de ADR-0008 implementado bit-exact. |

### Componentes modificados

| Componente | Ubicación | Cambio |
|---|---|---|
| `tempify.validation.geocoherence` | `src/tempify/validation/geocoherence.py` | Exponer `is_homogeneous(metadata_list, tolerances) -> tuple[bool, list[Inconsistency]]` para reuso desde Capa 2 (consumo de tolerancias canónicas, ADR-0009). |
| `tempify.detection.__init__` | `src/tempify/detection/__init__.py` | Re-export de `StructureDetector`, `StructureMode`, errores y schema. |

## 3. Contratos públicos (APIs)

### Clase `StructureDetector`

```python
from collections.abc import Callable
from pathlib import Path
from typing import Final

from tempify.detection.types import (
    AmbiguityReport,
    StructureDetectionResult,
    StructureMode,
)
from tempify.validation.geocoherence import CANONICAL_TOLERANCES, Tolerances


DisambiguationCallback = Callable[[AmbiguityReport], list[Path] | None]


class StructureDetector:
    """Detect structural mode (A/B/C) of a raster input set.

    Parameters
    ----------
    tolerances
        Geospatial homogeneity tolerances. Default: CANONICAL_TOLERANCES
        (frozen, ADR-0009). Exposed as keyword for testing only.
    disambiguation_callback
        Optional hook invoked with an AmbiguityReport when a folder is
        detected as heterogeneous (REQ-005b). If the callback returns a
        non-empty list, the detector adopts it as the resolved set.
    recurse
        If True, descend into subdirectories (REQ-011). Symlinks are
        always skipped to avoid recursion loops. Default False.
    """

    def __init__(
        self,
        *,
        tolerances: Tolerances = CANONICAL_TOLERANCES,
        disambiguation_callback: DisambiguationCallback | None = None,
        recurse: bool = False,
    ) -> None: ...

    def detect(self, source: Path | list[Path]) -> StructureDetectionResult:
        """Classify the input source into mode A, B, or C.

        Parameters
        ----------
        source
            Either a single Path (file or folder) or an ordered list of
            file Paths. A list triggers mode C unconditionally.

        Returns
        -------
        StructureDetectionResult
            Frozen dataclass with structure_mode, files (ordered),
            partial confidence (structure_mode, homogeneity), evidence
            strings, and a metadata_index keyed by Path.

        Raises
        ------
        EmptyInputError
            If `source` is an empty folder or empty list, or if all
            eligible files were filtered as sidecars.
        AmbiguousStructureError
            If the folder is heterogeneous AND no disambiguation_callback
            was provided (or the callback returned None/[]).
        HeterogeneousFilesError
            If the explicit list (mode C) fails geocoherence checks
            (REQ-008): mode C bypasses structure detection but not
            geospatial validation.
        FileNotFoundError
            If any path in the list or the folder itself does not exist.
        """
```

**Pre-condiciones:**
- `source` es un `Path` existente o una lista no vacía de `Path` existentes.
- La Capa 1 (`tempify.io.metadata`) está disponible para leer headers.

**Post-condiciones:**
- El `StructureDetectionResult` retornado es inmutable.
- `result.files` está ordenado por NFC lexicográfico salvo en modo C, que preserva orden del usuario.
- `result.confidence["structure_mode"]` y `result.confidence["homogeneity"]` están en `[0.0, 1.0]`. En modo C, `structure_mode = 1.0`. En modos A y C, `homogeneity = 1.0`.

**Excepciones lanzadas:** ver bloque Raises arriba; todas heredan de `StructureDetectionError`.

### Función helper `is_homogeneous` (Capa 3, reutilizada)

```python
def is_homogeneous(
    metadata_list: list[RasterMetadata],
    tolerances: Tolerances = CANONICAL_TOLERANCES,
) -> tuple[bool, list[Inconsistency]]:
    """Check geospatial coherence across raster metadata records.

    The first element is taken as reference. Each Inconsistency carries
    a code (GEO-001..GEO-005, ADR-0009), the offending Path, and the
    numerical magnitude of the divergence.
    """
```

## 4. Modelos de datos

### `StructureMode` (StrEnum)

```python
from enum import StrEnum


class StructureMode(StrEnum):
    """Estructural mode detected by StructureDetector.

    Values match the canonical schema (docs/schemas/detection-result.schema.md):
    `"A"`, `"B"`, `"C"`. Inherits from str for JSON / xarray.attrs
    transparency.
    """
    SINGLE_STACK = "A"
    MONOLAYER_COLLECTION = "B"
    EXPLICIT_LIST = "C"
```

### `StructureDetectionResult`

Es un subconjunto del `DetectionResult` global definido en `docs/schemas/detection-result.schema.md`. Solo carga los campos que esta capa puede computar; el ensamblaje del `DetectionResult` completo (con `temporal_frequency`, `variable_profile`) lo realiza el pipeline tras invocar `TemporalFrequencyResolver` y `VariableProfileMatcher`.

```python
from dataclasses import dataclass
from pathlib import Path

from tempify.detection.types import RasterMetadata, StructureMode
from tempify.detection.confidence import PartialConfidence


@dataclass(frozen=True)
class StructureDetectionResult:
    """Output of StructureDetector.detect. Subset of DetectionResult.

    Attributes
    ----------
    structure_mode
        Detected mode A/B/C.
    files
        Ordered list of resolved file paths. NFC lexicographic order
        except in mode C, where user-provided order is preserved.
    confidence
        Partial DetectionConfidence with the keys this layer computes:
        `structure_mode` and `homogeneity`. The remaining keys
        (`temporal_frequency`, `temporal_frequency_tier`,
        `variable_profile`, `overall`) are populated downstream by the
        pipeline assembler.
    evidence
        Dict[str, str] with short textual signals per component
        (matches docs/schemas/detection-result.schema.md rule 6).
    metadata_index
        Map Path -> RasterMetadata as read from io-handlers. Cached so
        downstream consumers do not re-open the files.
    """
    structure_mode: StructureMode
    files: list[Path]
    confidence: PartialConfidence       # TypedDict with structure_mode + homogeneity
    evidence: dict[str, str]
    metadata_index: dict[Path, RasterMetadata]
```

### `PartialConfidence` (TypedDict)

```python
from typing import TypedDict


class PartialConfidence(TypedDict):
    """Subset of DetectionConfidence (ADR-0008) computed by Capa 2 Structure.

    The full DetectionConfidence with the six canonical keys is
    assembled by the pipeline after TemporalFrequencyResolver and
    VariableProfileMatcher have run.
    """
    structure_mode: float
    homogeneity: float
```

### `AmbiguityReport`

```python
@dataclass(frozen=True)
class AmbiguityReport:
    """Diagnostic context handed to a disambiguation_callback (REQ-005b)."""
    groups: list[list[Path]]                 # Clusters of mutually homogeneous files
    offending_dimensions: list[str]          # e.g. ["crs", "extent"]
    inconsistencies: list[Inconsistency]     # GEO-001..GEO-005 with magnitudes
    candidate_files: list[Path]              # All eligible files (post sidecar filter)
```

### Excepciones

```python
class StructureDetectionError(Exception):
    """Root of the structure-detection error hierarchy."""

class EmptyInputError(StructureDetectionError):
    """Folder or list contains no eligible raster files."""

class AmbiguousStructureError(StructureDetectionError):
    """Heterogeneous folder; report enumerates groups and divergences."""
    def __init__(self, report: AmbiguityReport, message: str | None = None) -> None: ...

class HeterogeneousFilesError(StructureDetectionError):
    """Geocoherence failure (CRS / extent / resolution / nodata / shape)."""
```

### Sidecar canonical list

Lista canónica de extensiones a ignorar durante el escaneo en modo B. Sincronizada con REQ-010 y revisada en este design para ampliar con `.json` provenance (artefactos que tempify puede haber dejado en la carpeta).

| Extensión | Origen | Motivo de exclusión |
|---|---|---|
| `.aux.xml` | GDAL PAM | Sidecar de estadísticas / metadatos. |
| `.ovr` | GDAL overview | Pirámides multiresolución. |
| `.tfw` | World file | Georreferenciación accesoria. |
| `.prj` | ESRI projection | Texto de CRS, no ráster. |
| `.cpg` | ESRI codepage | Codepage de shapefiles asociados. |
| `.lock` | Lockfiles | Concurrencia GDAL. |
| `.tmp` | Temporales | Escrituras parciales. |
| `.json` | Procedencia tempify | Reportes propios (`*.tempify.json`). |

`SIDECAR_EXTENSIONS` se declara `Final[frozenset[str]]` y se versiona en código; cualquier cambio amerita nota en CHANGELOG.

## 5. Algoritmos clave

### Algoritmo 1: Clasificación A/B/C (árbol de decisión)

```
def _classify(source):
    if isinstance(source, list):                       # REQ-004
        return MODE_C
    if source.is_file():
        meta = io.metadata(source)
        if meta.is_netcdf and meta.has_time_dim:       # REQ-002
            return MODE_A
        if meta.is_geotiff and meta.band_count >= 2:   # REQ-009
            return MODE_A
        # Single-banded single file: treat as degenerate A
        return MODE_A
    if source.is_dir():
        candidates = _scan_dir(source, recurse)        # NFC-sorted, sidecars off
        if len(candidates) == 0:
            raise EmptyInputError
        if len(candidates) == 1:                       # REQ-003 N=1
            return MODE_A
        return MODE_B
    raise FileNotFoundError(source)
```

**Complejidad:** O(N) sobre el listado del directorio; las llamadas a `io.metadata` son O(N) headers, no lectura de datos.

**Trade-offs:** privilegiamos lectura de headers (cheap) sobre heurística por nombre. El árbol es determinista y trivialmente testeable.

### Algoritmo 2: Verificación de homogeneidad en modo B (REQ-007, ADR-0009)

Delegado a `tempify.validation.geocoherence.is_homogeneous(metadata_list, CANONICAL_TOLERANCES)`. Devuelve `(bool, list[Inconsistency])`. Si la lista no está vacía:

1. Si `disambiguation_callback is None`: construir `AmbiguityReport` y `raise AmbiguousStructureError(report)`.
2. Si hay callback: invocar con el reporte. Si devuelve lista no vacía, repetir verificación con esa lista (un solo nivel de recursión, sin loop). Si devuelve `None` o `[]`: `raise AmbiguousStructureError(report)`.

**Justificación de no reinventar la rueda:** la lógica de tolerancias ya vive en Capa 3 según ADR-0009. La Capa 2 la importa; no duplica.

### Algoritmo 3: Modo A multi-banda GeoTIFF (REQ-009)

Cuando el archivo es un GeoTIFF con `band_count >= 2`:

1. Se clasifica como A independientemente de la semántica de bandas.
2. La semántica temporal se delega: si hay `disambiguation_callback` y la Capa 2 detecta ambigüedad de bandas (sin metadata CF y nomenclatura no-conclusiva), se invoca el callback con el reporte. En contraposición, si el callback no resuelve, se emite warning y se anota en `evidence["structure_mode"]` para que `TemporalFrequencyResolver` (Capa 2 también, otra spec) decida en su tier interactivo.
3. La confianza `structure_mode` se reduce en `-0.1` cuando la semántica de bandas no es confirmable, manteniendo la cota `[0.0, 1.0]`.

### Algoritmo 4: Confidence scoring (pseudocódigo ADR-0008)

```python
def compute_structure_mode_confidence(metadata_list, mode_detected) -> float:
    score = 0.0
    if _all_same_format(metadata_list):
        score += 0.4
    if _all_same_crs(metadata_list):
        score += 0.3
    if _all_same_extent(metadata_list):
        score += 0.2
    if len(metadata_list) in {12, 52, 365, 366}:
        score += 0.1
    return min(score, 1.0)


def compute_homogeneity_confidence(metadata_list, mode) -> float:
    if mode in {StructureMode.SINGLE_STACK, StructureMode.EXPLICIT_LIST}:
        return 1.0
    coherent = _count_coherent(metadata_list, reference=metadata_list[0])
    return coherent / len(metadata_list)
```

Modo C: `confidence["structure_mode"] = 1.0` por construcción (REQ-008, schema rule 8). En modo A degenerado (folder con N=1), aplicamos los mismos +0.4/+0.3/+0.2 con el único archivo como su propia referencia (siempre da 0.9; el +0.1 por conteo conocido no aplica).

### Algoritmo 5: Sidecar filtering y orden NFC

```python
def _scan_dir(path, recurse=False):
    entries = path.rglob("*") if recurse else path.iterdir()
    files = [
        p for p in entries
        if p.is_file()
        and not _is_sidecar(p)
        and not (recurse and p.is_symlink())          # REQ-011
    ]
    return sorted(
        files,
        key=lambda p: unicodedata.normalize("NFC", p.name),
    )


def _is_sidecar(p: Path) -> bool:
    suffix = "".join(p.suffixes).lower()              # cubre `.aux.xml`
    return any(suffix.endswith(ext) for ext in SIDECAR_EXTENSIONS)
```

**Complejidad:** O(N log N) por el sort. Determinista cross-platform porque la normalización NFC elimina diferencias entre Windows (case-insensitive FS, NFC nativo) y Linux (case-sensitive, NFD posible en HFS+ residual).

## 6. Decisiones de diseño

### Decisión 1: No recursión por default

**Opciones consideradas:**
1. `recurse=True` por default, para "just work" con árboles profundos.
2. `recurse=False` por default y opt-in explícito.

**Decisión:** opción 2.
**Razón:** REQ-011 lo dicta. La recursión por default invitaría a recoger archivos sin querer (subcarpetas con productos no relacionados) y a tener problemas con symlinks. El usuario que quiere recursión la pide.
**Trade-offs:** una llamada extra del usuario; aceptable a cambio de la previsibilidad.

### Decisión 2: Mode C bypass de detección, no de validación

**Opciones consideradas:**
1. Modo C salta detección y validación geoespacial completamente.
2. Modo C salta detección, pero aplica validación geoespacial (tolerancias ADR-0009).

**Decisión:** opción 2 (alineada con REQ-008).
**Razón:** el usuario asume responsabilidad sobre la elección estructural y el orden, pero no sobre la viabilidad técnica del stack. Mezclar archivos con CRS distinto rompe la interpolación silenciosamente.
**Trade-offs:** un check adicional en modo C; coste despreciable. `confidence["structure_mode"]` se fuerza a `1.0` (schema rule 8), pero `HeterogeneousFilesError` puede dispararse si las tolerancias fallan.

### Decisión 3: Sidecar list canónica versionada en código

**Opciones consideradas:**
1. Lista configurable vía parámetro.
2. Lista canónica, no configurable, definida en código y documentada en tabla revisable.

**Decisión:** opción 2.
**Razón:** la lista es contractual; un usuario que quiere otro filtro pre-filtra la lista y entra por modo C. Mantiene reproducibilidad alineada con ADR-0007.
**Trade-offs:** menos flexibilidad; mitigado por modo C.

### Decisión 4: PartialConfidence en lugar de DetectionConfidence completo

**Opciones consideradas:**
1. Esta capa rellena las seis claves del `DetectionConfidence` con valores neutros para las que no le competen.
2. Esta capa devuelve un `PartialConfidence` con las dos claves que realmente computa; el pipeline ensambla el `DetectionConfidence` completo.

**Decisión:** opción 2.
**Razón:** evita falsos positivos de confianza en componentes que esta capa no observa; mantiene separación de responsabilidades. El schema canónico se ensambla en un solo lugar (pipeline).
**Trade-offs:** un mapping extra; documentado en el schema (subconjunto explícito).

> No se registra ADR adicional: esta decisión no contradice ADR-0008, simplemente clarifica la frontera de responsabilidad entre Capa 2 sub-módulos y el ensamblador del pipeline.

## 7. Estrategia de testing

### Tests unitarios

Cobertura por tipo de detección (uno por mode/path):

- `test_detect_mode_A_single_stack` — REQ-001, REQ-002: NetCDF con `time` de longitud N≥2.
- `test_netcdf_singleton_time_dim_warns` — REQ-002: time de longitud 1 emite warning.
- `test_detect_mode_B_collection` — REQ-003: 12 GeoTIFF coherentes.
- `test_single_file_folder_defaults_to_mode_A` — REQ-003 N=1.
- `test_explicit_list_preserves_user_order` — REQ-004.
- `test_explicit_list_bypasses_detection_but_runs_coherence` — REQ-008.
- `test_mode_C_forces_structure_confidence_to_one` — REQ-008.
- `test_ambiguous_structure_raises` — REQ-005: mezcla de CRS sin callback.
- `test_disambiguation_callback_invoked` — REQ-005b: callback resuelve subset.
- `test_disambiguation_callback_returns_none_raises` — REQ-005b: fallback a error.
- `test_multiband_geotiff_mode_A` — REQ-009: GeoTIFF de 12 bandas.
- `test_detect_mode_B_with_canonical_tolerances` — REQ-007 / ADR-0009.
- `test_heterogeneous_crs_raises` — REQ-007 GEO-001.
- `test_extent_within_pixel_tolerance_accepted` — REQ-007 GEO-002.
- `test_resolution_outside_tolerance_raises` — REQ-007 GEO-003.
- `test_nodata_mismatch_raises` — REQ-007 GEO-004.
- `test_shape_mismatch_raises` — REQ-007 GEO-005.
- `test_sidecar_extensions_ignored` — REQ-010.
- `test_nfc_lexicographic_sort_stable` — REQ-010.
- `test_recursive_false_by_default` — REQ-011.
- `test_recursive_skips_symlinks` — REQ-011.
- `test_detection_result_shape` — REQ-006: forma del dataclass.
- `test_confidence_dict_keys_canonical` — REQ-006: dos claves esperadas en `PartialConfidence`.
- `test_empty_folder_raises` — EmptyInputError.
- `test_empty_list_raises` — EmptyInputError.

### Tests property-based (hypothesis)

- `test_confidence_dict_property_stable` — NFR-003: misma entrada (ordenada) produce mismo dict.
- `test_sidecar_filter_idempotent` — REQ-010: aplicar el filtro dos veces da igual resultado.
- `test_nfc_sort_total_order` — REQ-010: el orden NFC es total y antisimétrico sobre nombres arbitrarios.

### Tests de integración

- `test_integration_with_io_handlers_metadata_only` — verifica que `StructureDetector` solo invoca `io.metadata` (no `io.read`), midiendo la ausencia de carga de arrays.
- `test_end_to_end_worldclim_like_collection` — fixture de 12 GeoTIFF tipo WorldClim, asegura modo B con `confidence["structure_mode"] >= 0.9`.
- `test_end_to_end_netcdf_chelsa_like_stack` — fixture de NetCDF mensual con dim `time`.

### Tests de performance (NFR-001)

- `test_detection_perf_1000_files` — benchmark sobre 1000 GeoTIFF sintéticos homogéneos; assert `<2s` en SSD (CI lo marca como skip si no es local).

### Fixtures necesarios

- `synthetic_3x3_monthly.nc` — existente.
- `synthetic_12_geotiff_homogeneous/` — generar en setup, 12 monocapas coherentes con CRS EPSG:4326.
- `synthetic_12_geotiff_mixed_crs/` — heterogéneo (REQ-005).
- `synthetic_12_geotiff_with_sidecars/` — incluye `.aux.xml`, `.tfw`, `.json` (REQ-010).
- `synthetic_multiband_geotiff_12.tif` — single multibanda.
- `synthetic_perf_1000_geotiff/` — generar bajo demanda en benchmark.

## 8. Plan de migración

No aplica: feature nueva, no hay usuarios actuales. Cuando aparezcan, el contrato se asegura por:
- Re-export estable desde `tempify.detection`.
- `StructureMode` heredando de `str`/`StrEnum` preserva compatibilidad estructural con el `Literal["A","B","C"]` que hoy declara `architecture.md`.
- `PartialConfidence` es subconjunto exacto de `DetectionConfidence` (sin claves extra).

## 9. Métricas de calidad

| Métrica | Umbral |
|---|---|
| Coverage del módulo `tempify.detection.structure` | ≥ 85% (NFR-002) |
| Performance detección 1000 archivos | < 2 s en SSD (NFR-001) |
| Memoria peak detección 1000 archivos | < 200 MB (solo headers) |
| Estabilidad confidence | 100% bit-exact en property tests (NFR-003) |
| Linter / type-check | `ruff` + `mypy --strict` sin warnings en el módulo |

## 10. Trazabilidad requirements → design

| Requirement | Componente / sección que lo implementa |
|---|---|
| REQ-001 | `StructureDetector.detect` (entry point) + `_classify` (Algoritmo 1) |
| REQ-002 | `_classify` rama NetCDF + warning en `evidence` |
| REQ-003 | `_classify` rama folder + N=1 default a modo A |
| REQ-004 | `_classify` rama list + preservación de orden en `StructureDetectionResult.files` |
| REQ-005 | `AmbiguousStructureError(AmbiguityReport)` en Algoritmo 2 |
| REQ-005b | `disambiguation_callback` en constructor + paso 2 de Algoritmo 2 |
| REQ-006 | `StructureDetectionResult` dataclass + `PartialConfidence` TypedDict |
| REQ-007 | Delegación a `tempify.validation.geocoherence.is_homogeneous` con `CANONICAL_TOLERANCES` |
| REQ-008 | Decisión 2 + modo C en Algoritmo 1, `confidence["structure_mode"] = 1.0` forzado |
| REQ-009 | Algoritmo 3 (multi-banda GeoTIFF) + reducción de confidence cuando semántica incierta |
| REQ-010 | `SIDECAR_EXTENSIONS` (sección §4 tabla) + Algoritmo 5 (sort NFC) |
| REQ-011 | Parámetro `recurse: bool = False` + skip de symlinks en `_scan_dir` |
| NFR-001 | `test_detection_perf_1000_files` (sección §7) + uso exclusivo de `io.metadata` |
| NFR-002 | Métrica de coverage (sección §9) |
| NFR-003 | `test_confidence_dict_property_stable` con hypothesis (sección §7) |
