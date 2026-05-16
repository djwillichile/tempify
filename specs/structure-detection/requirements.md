# Requirements — structure-detection

**Estado:** Approved
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-15
**Última actualización:** 2026-05-16

## 1. Propósito

Detectar automáticamente si los archivos de entrada constituyen un stack único multicapa (modo A), una colección de monocapas homogéneas en una carpeta (modo B), o una lista explícita ordenada provista por el usuario (modo C). Validar la coherencia estructural del input y emitir un contrato canónico `DetectionResult` consumible por las capas aguas abajo (`temporal-frequency-resolver`, `validation`, `pipeline`).

### Clase pública y jerarquía de errores

La capa expone la clase `StructureDetector` como punto de entrada. La jerarquía canónica de excepciones es:

```
StructureDetectionError (raíz)
  ├── AmbiguousStructureError    # heterogeneidad detectada, requiere disambiguación
  ├── EmptyInputError            # carpeta o lista sin archivos elegibles
  └── HeterogeneousFilesError    # mezcla de CRS, extent, resolución, formato o nodata
```

## 2. Alcance

### In-scope

- Detección de stack único multicapa (NetCDF con dim temporal, GeoTIFF multi-banda).
- Detección de colecciones de monocapas homogéneas en una carpeta.
- Aceptación de listas explícitas de rutas ordenadas (modo C) con bypass de detección estructural pero conservando validación geoespacial.
- Filtrado de archivos sidecar (`.aux.xml`, `.ovr`, `.tfw`, `.prj`, `.cpg`, `.lock`) durante el escaneo.
- Orden lexicográfico estable (Unicode NFC) de los archivos descubiertos para garantizar reproducibilidad cross-plataforma.
- Emisión del dataclass `DetectionResult` con `confidence: DetectionConfidence` (TypedDict).
- Aplicación de tolerancias canónicas (ADR-0009) al evaluar homogeneidad en modo B.

### Out-of-scope

- Inferencia de frecuencia temporal (responsabilidad de `temporal-frequency-resolver`).
- Validación geoespacial profunda post-stack (responsabilidad de `validation`).
- Lectura efectiva de los datos (responsabilidad de `io-handlers`).
- Detección de identidad de variable (perfil) más allá de un hint inicial.

## 3. Actores y casos de uso

### Actor: Operador de pipeline que necesita procesar carpetas heterogéneas sin saber a priori si contienen un stack o múltiples archivos.

**Caso de uso típico:** El operador apunta a una carpeta con varios `.tif`; el sistema detecta automáticamente que es una colección de 12 monocapas homogéneas (modo B), reporta `confidence` por dimensión, y procede.

### Actor: Usuario avanzado que ya sabe qué archivos procesar y en qué orden.

**Caso de uso típico:** El usuario pasa una lista Python explícita; el sistema acepta el modo C, fuerza `confidence.structure_mode = 1.0` y solo aplica la validación geoespacial.

## 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL identify the input structure mode as one of: A (single multi-layer stack), B (collection of single-layer files in a folder), or C (explicit ordered list of file paths).

### REQ-002 (Event-driven)

WHEN the input is a single NetCDF file with an internal time dimension of length N≥1, THE SYSTEM SHALL classify it as mode A. IF the time dimension has length 1, THE SYSTEM SHALL accept it as a degenerate mode A and emit a warning indicating low temporal coverage.

### REQ-003 (Event-driven)

WHEN the input is a folder containing N homogeneous raster files (same format, same CRS, same extent within tolerances, same resolution, same nodata, same dimensions), THE SYSTEM SHALL classify it as mode B. WHEN the folder contains exactly N=1 eligible file, THE SYSTEM SHALL default to mode A on that file.

### REQ-004 (Event-driven)

WHEN the input is a Python list or sequence of file paths, THE SYSTEM SHALL classify it as mode C and preserve the user-provided order verbatim without re-sorting.

### REQ-005 (Unwanted)

IF the folder contains heterogeneous files (mixed formats, mixed CRS, divergent extents beyond tolerances, multiple variables, or unrelated rasters), THEN THE SYSTEM SHALL raise `AmbiguousStructureError(report)` where `report` enumerates the detected groups, the offending dimension(s), and the per-file divergence diagnostics.

### REQ-005b (Optional / Event-driven)

WHERE a `disambiguation_callback: Callable[[AmbiguityReport], list[Path]] | None` is provided AND heterogeneity is detected, THE SYSTEM SHALL invoke the callback with the ambiguity report and SHALL adopt its returned list as the resolved file set instead of raising. IF the callback returns `None` or an empty list, THE SYSTEM SHALL raise `AmbiguousStructureError` as in REQ-005.

### REQ-006 (Ubiquitous)

THE SYSTEM SHALL return a `DetectionResult` dataclass with the fields `structure_mode: Literal["A","B","C"]`, `temporal_frequency: TemporalFrequency | None`, `variable_profile: VariableProfileHint | None`, `files: list[Path]` (ordered), and `confidence: DetectionConfidence`. The `confidence` field SHALL be a `TypedDict` with exactly the six canonical keys defined in ADR-0008 and `docs/schemas/detection-result.schema.md`: `structure_mode`, `temporal_frequency`, `variable_profile`, `crs_homogeneity`, `extent_homogeneity`, `nodata_homogeneity` (each `float` in `[0.0, 1.0]`).

### REQ-007 (Event-driven)

WHEN detecting mode B (collection), THE SYSTEM SHALL apply canonical tolerances from ADR-0009 when assessing homogeneity:

- **CRS:** strict match (EPSG code or canonical WKT digest equality).
- **Extent:** `rtol=1e-6` combined with `atol = 0.01 * pixel_size` (1% of pixel size).
- **Resolution:** `rtol=1e-6` on both `x` and `y` pixel size.
- **Nodata:** strict match (or both `None`).
- **Dimensions:** strict match on `(width, height)`.

Cualquier divergencia fuera de tolerancia eleva `HeterogeneousFilesError` (o, si aplica REQ-005b, dispara el callback).

### REQ-008 (Optional / Ubiquitous)

WHERE the user provides an explicit list of files (mode C), THE SYSTEM SHALL bypass automatic structure detection but SHALL still apply geospatial coherence validation (REQ-007 tolerances). The user assumes responsibility for the structural choice, and `confidence.structure_mode` SHALL be forced to `1.0`.

### REQ-009 (Event-driven)

WHEN the input is a single GeoTIFF or NetCDF with N≥2 bands or N≥2 time steps, THE SYSTEM SHALL classify it as mode A regardless of band semantics, AND SHALL require either the user or the `temporal-frequency-resolver` to confirm whether the bands represent time. IF band semantics cannot be confirmed, THE SYSTEM SHALL emit a warning and set `confidence.temporal_frequency < 1.0`.

### REQ-010 (Ubiquitous)

THE SYSTEM SHALL ignore canonical sidecar extensions during folder scan: `.aux.xml`, `.ovr`, `.tfw`, `.prj`, `.cpg`, `.lock`, `.tmp`. THE SYSTEM SHALL sort eligible files using Unicode NFC lexicographic order to guarantee deterministic ordering across Windows (case-insensitive FS) and Linux (case-sensitive FS).

### REQ-011 (Ubiquitous)

THE SYSTEM SHALL NOT descend into subdirectories by default. WHERE `recursive=True` is explicitly passed, THE SYSTEM SHALL descend AND SHALL skip symlinks to avoid recursion loops.

## 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Performance | Detección sobre 1000 archivos en <2s sobre SSD | Benchmark `tests/benchmarks/test_detection_perf.py` con dataset sintético |
| NFR-002 | Maintainability | Cobertura del módulo ≥85% | `pytest --cov=tempify.detection --cov-fail-under=85` |
| NFR-003 | Reliability | Confidence scoring estable: misma entrada produce mismo `DetectionConfidence` (mismas claves, mismos valores) | Property test con Hypothesis |

## 6. Criterios de aceptación

Cada REQ se traza a tests nombrados en `tests/structure_detection/`:

- [ ] REQ-001/REQ-002: `test_detect_mode_A_single_stack`
- [ ] REQ-003: `test_detect_mode_B_collection`
- [ ] REQ-003 (N=1): `test_single_file_folder_defaults_to_mode_A`
- [ ] REQ-004: `test_explicit_list_preserves_user_order`
- [ ] REQ-005: `test_ambiguous_structure_raises`
- [ ] REQ-005b: `test_disambiguation_callback_invoked`
- [ ] REQ-006: `test_detection_result_shape`, `test_confidence_dict_keys_canonical`
- [ ] REQ-007: `test_detect_mode_B_with_canonical_tolerances`, `test_heterogeneous_crs_raises`, `test_extent_within_pixel_tolerance_accepted`
- [ ] REQ-008: `test_explicit_list_bypasses_detection_but_runs_coherence`, `test_mode_C_forces_structure_confidence_to_one`
- [ ] REQ-009: `test_multiband_geotiff_mode_A`, `test_netcdf_singleton_time_dim_warns`
- [ ] REQ-010: `test_sidecar_extensions_ignored`, `test_nfc_lexicographic_sort_stable`
- [ ] REQ-011: `test_recursive_false_by_default`, `test_recursive_skips_symlinks`
- [ ] NFR-001: `test_detection_perf_1000_files`
- [ ] NFR-003: `test_confidence_dict_property_stable`

Criterios adicionales:

- [ ] Cobertura del módulo ≥85%
- [ ] Documentación API completa (docstrings NumPy, type hints)
- [ ] CHANGELOG actualizado
- [ ] Excepciones documentadas en docstring de `StructureDetector.detect`

## 7. Dependencias y supuestos

### Specs relacionadas

- **Bloqueada por:** [io-handlers](../io-handlers/requirements.md) (lectura de metadatos CRS/extent/dims sin cargar datos).
- **Bloquea:** [validation](../validation/requirements.md), [pipeline](../pipeline/requirements.md), [temporal-frequency-resolver](../temporal-frequency-resolver/requirements.md) (consume `DetectionResult`), [cli](../cli/requirements.md), [gui](../gui/requirements.md).

### ADRs referenciados

- [ADR-0008](../../docs/adr/0008-confidence-scoring-and-detection-result-contract.md) — contrato canónico `DetectionResult` y `DetectionConfidence`.
- [ADR-0009](../../docs/adr/0009-geospatial-coherence-tolerances.md) — tolerancias de homogeneidad.

### Schemas

- [docs/schemas/detection-result.schema.md](../../docs/schemas/detection-result.schema.md) — shape canónico.

### Supuestos

- Los inputs son archivos legibles por GDAL via rioxarray.
- La capa `io-handlers` expone `metadata(path) -> dict` sin materializar el array.
- El usuario opera sobre filesystems locales (no objetos remotos por ahora).

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Falsos positivos modo B por archivos sidecar (`.aux.xml`, `.ovr`, `.tfw`) | Alta | Medio | REQ-010: lista canónica de extensiones a ignorar durante el escaneo |
| Orden de archivos inconsistente entre Windows (case-insensitive) y Linux (case-sensitive) | Alta | Alto (reproducibilidad) | REQ-010: orden lexicográfico Unicode NFC explícito |
| Carpeta con un único archivo: colisión semántica modo A vs B | Media | Bajo | REQ-003: si N=1, default a modo A |
| NetCDF con dim temporal de tamaño 1 (degenerado) | Media | Bajo | REQ-002: aceptar como mode A degenerado pero advertir |
| Symlinks o recursión infinita en subdirectorios | Baja | Alto | REQ-011: por default no descender; con `recursive=True` saltar symlinks |
| Edge cases en formatos no estándar | Media | Bajo | Fixtures extensivas + manejo robusto de excepciones |

## 8. Referencias

- ADR-0008: contrato `DetectionResult` / `DetectionConfidence`.
- ADR-0009: tolerancias geoespaciales canónicas.
- CF Conventions: https://cfconventions.org/
- EARS notation: https://alistairmavin.com/ears/
- Unicode NFC: https://www.unicode.org/reports/tr15/
