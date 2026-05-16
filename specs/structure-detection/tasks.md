# Tasks — structure-detection

**Estado:** Approved
**Design doc:** [design.md](design.md)
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-15

## Reglas para tasks

- Atómicas (≤ 4h por task, un commit).
- TDD estricto: test rojo antes de impl.
- Verificables: criterio de done observable.
- Trazables a REQ-NNN / NFR-NNN.

## Fase 1: Fundamentos

### task-1.1: Scaffolding del paquete `tempify.detection`

**Tipo:** chore
**Estimación:** 0.5h
**Bloquea:** task-1.2, task-1.3, task-1.4, task-1.5
**Bloqueada por:** —

**Descripción:** Crear estructura de paquete con módulos vacíos (stubs con `pass` o `...`) y `__init__.py` mínimo. Verificar que `python -c "import tempify.detection"` funcione.

**Criterio de done:**
- [ ] Árbol creado: `structure.py`, `types.py`, `errors.py`, `constants.py`, `confidence.py`
- [ ] `tests/structure_detection/__init__.py` y `conftest.py` vacíos
- [ ] `mypy --strict src/tempify/detection` pasa sobre stubs
- [ ] `ruff check src/tempify/detection` pasa

**Archivos:**
- `src/tempify/detection/__init__.py`
- `src/tempify/detection/structure.py`
- `src/tempify/detection/types.py`
- `src/tempify/detection/errors.py`
- `src/tempify/detection/constants.py`
- `src/tempify/detection/confidence.py`
- `tests/structure_detection/__init__.py`
- `tests/structure_detection/conftest.py`

### task-1.2: Definir `StructureMode` (StrEnum)

**Tipo:** impl
**Estimación:** 0.5h
**Bloquea:** task-1.3, task-1.6
**Bloqueada por:** task-1.1

**Descripción:** Implementar `StructureMode(StrEnum)` con valores `"A"`, `"B"`, `"C"` en `types.py` per design §4. Test de equivalencia con `Literal["A","B","C"]` para garantizar compatibilidad con el schema canónico.

**Criterio de done:**
- [ ] `test_structure_mode_str_values` verde (valores exactos `"A"`, `"B"`, `"C"`)
- [ ] `test_structure_mode_is_str_subclass` verde
- [ ] mypy + ruff verdes
- [ ] Docstring NumPy presente

**Archivos:**
- `src/tempify/detection/types.py`
- `tests/structure_detection/test_types.py`

### task-1.3: Definir `StructureConfidencePartial` (TypedDict)

**Tipo:** impl
**Estimación:** 0.5h
**Bloquea:** task-1.6
**Bloqueada por:** task-1.2

**Descripción:** TypedDict con dos claves `structure_mode: float` y `homogeneity: float` per ADR-0008 (composición por capas). Test `test_confidence_dict_keys_canonical` (REQ-006) que valida set de claves exacto.

**Criterio de done:**
- [ ] `test_confidence_dict_keys_canonical` verde
- [ ] Re-exportado en `tempify.detection.__init__`
- [ ] Docstring referencia ADR-0008

**Archivos:**
- `src/tempify/detection/confidence.py`
- `tests/structure_detection/test_confidence_shape.py`

### task-1.4: Definir jerarquía de excepciones

**Tipo:** impl
**Estimación:** 0.5h
**Bloquea:** task-2.4, task-2.5
**Bloqueada por:** task-1.1

**Descripción:** Implementar `StructureDetectionError` (raíz) y subclases `AmbiguousStructureError(report)`, `EmptyInputError`, `HeterogeneousFilesError`. La primera acepta un `AmbiguityReport` y un mensaje opcional.

**Criterio de done:**
- [ ] `test_error_hierarchy_inheritance` verde (issubclass de la raíz)
- [ ] `test_ambiguous_error_carries_report` verde
- [ ] Re-exportadas en `__init__`

**Archivos:**
- `src/tempify/detection/errors.py`
- `tests/structure_detection/test_errors.py`

### task-1.5: Constante `SIDECAR_EXTENSIONS`

**Tipo:** impl
**Estimación:** 0.5h
**Bloquea:** task-2.10
**Bloqueada por:** task-1.1

**Descripción:** Declarar `SIDECAR_EXTENSIONS: Final[frozenset[str]]` con las extensiones canónicas: `.aux.xml`, `.ovr`, `.tfw`, `.prj`, `.cpg`, `.lock`, `.tmp`, `.json` (design §4 tabla). Test verifica tipo `frozenset` e inmutabilidad (intento de mutación → `AttributeError`).

**Criterio de done:**
- [ ] `test_sidecar_extensions_is_frozen` verde
- [ ] `test_sidecar_extensions_canonical_set` verde
- [ ] mypy `Final` enforced

**Archivos:**
- `src/tempify/detection/constants.py`
- `tests/structure_detection/test_constants.py`

### task-1.6: Dataclasses `StructureDetectionResult` y `AmbiguityReport`

**Tipo:** impl
**Estimación:** 1h
**Bloquea:** task-2.1, task-2.4
**Bloqueada por:** task-1.2, task-1.3

**Descripción:** Implementar `@dataclass(frozen=True) StructureDetectionResult` con campos del design §4 incluyendo `band_descriptions: list[str] | None = None` (ADR-0015). Implementar `AmbiguityReport` con `groups`, `offending_dimensions`, `inconsistencies`, `candidate_files`.

**Criterio de done:**
- [ ] `test_detection_result_shape` verde (REQ-006)
- [ ] `test_detection_result_is_frozen` verde
- [ ] `test_detection_result_band_descriptions_default_none` verde
- [ ] `test_ambiguity_report_shape` verde

**Archivos:**
- `src/tempify/detection/types.py`
- `tests/structure_detection/test_types.py`

### task-1.7: Fixtures sintéticas base

**Tipo:** test
**Estimación:** 2h
**Bloquea:** Fase 2 entera
**Bloqueada por:** task-1.1

**Descripción:** Crear fixtures pytest en `conftest.py` y/o helpers en `tests/structure_detection/fixtures/`:
- `synthetic_12_geotiff_homogeneous/` (12 .tif EPSG:4326 coherentes)
- `synthetic_12_geotiff_mixed_crs/` (mezcla CRS)
- `synthetic_12_geotiff_with_sidecars/` (incluye `.aux.xml`, `.tfw`, `.json`)
- `synthetic_multiband_geotiff_12.tif` (12 bandas, con y sin `GDAL_BAND_DESCRIPTIONS`)
- `synthetic_3x3_monthly.nc` (reusar si existe; si no, generar)
- `synthetic_single_file_folder/` (1 .tif)

**Criterio de done:**
- [ ] Todos los fixtures generables on-demand (no commits binarios pesados)
- [ ] `tmp_path` o `tmp_path_factory` usados (no contaminar repo)
- [ ] Documentadas en `conftest.py` con docstrings

**Archivos:**
- `tests/structure_detection/conftest.py`
- `tests/structure_detection/fixtures/builders.py`

## Fase 2: Implementación incremental

### task-2.1: Test + impl `_filter_sidecars`

**Tipo:** test + impl
**Estimación:** 1h
**Bloquea:** task-2.2
**Bloqueada por:** task-1.5, task-1.7

**Descripción:** TDD para `_is_sidecar(path)` y `_filter_sidecars(paths)`. Cubre extensiones compuestas (`.aux.xml`) via `"".join(p.suffixes).lower()`. Tests:
- `test_sidecar_extensions_ignored` (REQ-010)
- `test_sidecar_filter_idempotent` (property test)

**Criterio de done:**
- [ ] Tests verdes
- [ ] Cobertura del helper 100%
- [ ] mypy + ruff verdes

**Archivos:**
- `src/tempify/detection/structure.py`
- `tests/structure_detection/test_sidecar_filter.py`

### task-2.2: Test + impl `_scan_dir` + orden NFC

**Tipo:** test + impl
**Estimación:** 1.5h
**Bloquea:** task-2.6
**Bloqueada por:** task-2.1

**Descripción:** Implementar `_scan_dir(path, recurse)` con sort NFC determinista (design §5 algoritmo 5). Tests:
- `test_nfc_lexicographic_sort_stable` (REQ-010): nombres mixtos NFC/NFD producen orden estable
- `test_nfc_sort_total_order` (Hypothesis property)
- `test_recursive_false_by_default` (REQ-011)
- `test_recursive_skips_symlinks` (REQ-011, skip en Windows si no aplica)

**Criterio de done:**
- [ ] Cuatro tests verdes
- [ ] Symlinks skip verificable (en Linux/macOS; xfail en Windows)
- [ ] Cobertura del helper ≥95%

**Archivos:**
- `src/tempify/detection/structure.py`
- `tests/structure_detection/test_scan_dir.py`

### task-2.3: Test + impl `_normalize_source` + EmptyInputError

**Tipo:** test + impl
**Estimación:** 1h
**Bloquea:** task-2.6
**Bloqueada por:** task-1.4, task-1.7

**Descripción:** Función que normaliza `Path | list[Path]` y valida no-vacío. Tests:
- `test_empty_folder_raises` (carpeta sin archivos elegibles → `EmptyInputError`)
- `test_empty_list_raises` (lista vacía → `EmptyInputError`)
- `test_nonexistent_path_raises_filenotfound`
- `test_sidecars_only_folder_raises_empty` (carpeta con solo `.aux.xml`)

**Criterio de done:**
- [ ] Cuatro tests verdes
- [ ] Mensaje de error incluye la ruta ofendida

**Archivos:**
- `src/tempify/detection/structure.py`
- `tests/structure_detection/test_normalize_source.py`

### task-2.4: Test + impl Modo A — single NetCDF

**Tipo:** test + impl
**Estimación:** 2h
**Bloquea:** task-2.7
**Bloqueada por:** task-1.6, task-1.7

**Descripción:** Rama `_classify` para NetCDF con dim temporal (design §5 algoritmo 1). Tests:
- `test_detect_mode_A_single_stack` (REQ-001, REQ-002): `time` length N≥2
- `test_netcdf_singleton_time_dim_warns` (REQ-002): N=1 emite `UserWarning` con `pytest.warns`
- `test_single_file_folder_defaults_to_mode_A` (REQ-003 N=1)

**Criterio de done:**
- [ ] Tres tests verdes
- [ ] `structure_mode == StructureMode.SINGLE_STACK`
- [ ] `evidence["structure_mode"]` con string informativo

**Archivos:**
- `src/tempify/detection/structure.py`
- `tests/structure_detection/test_mode_a_netcdf.py`

### task-2.5: Test + impl Modo A — GeoTIFF multibanda + propagación `band_descriptions`

**Tipo:** test + impl
**Estimación:** 2.5h
**Bloquea:** task-2.7
**Bloqueada por:** task-2.4

**Descripción:** Rama `_classify` para GeoTIFF `band_count >= 2` (REQ-009, design §5 algoritmo 3 + ADR-0015). Extracción de `GDAL_BAND_DESCRIPTIONS` y propagación a `StructureDetectionResult.band_descriptions`. Tests:
- `test_multiband_geotiff_mode_A` (REQ-009)
- `test_multiband_geotiff_band_descriptions_propagated` (con descripciones parseables como fechas → lista poblada)
- `test_multiband_geotiff_no_descriptions_keeps_none` (sin metadata → `band_descriptions is None`)
- `test_multiband_geotiff_unparseable_descriptions_kept_for_diagnosis` (strings no-fecha → lista poblada + nota en `evidence`)

**Criterio de done:**
- [ ] Cuatro tests verdes
- [ ] `confidence["structure_mode"]` reducido en -0.1 cuando semántica de bandas no es confirmable
- [ ] Docstring referencia ADR-0015

**Archivos:**
- `src/tempify/detection/structure.py`
- `tests/structure_detection/test_mode_a_multiband.py`

### task-2.6: Test + impl Modo B — colección homogénea (delegación a geocoherence)

**Tipo:** test + impl
**Estimación:** 2.5h
**Bloquea:** task-2.7, task-2.8
**Bloqueada por:** task-2.2, task-2.3

**Descripción:** Rama `_classify` para carpetas con N≥2 archivos (REQ-003, REQ-007). Delegación a `tempify.validation.geocoherence.is_homogeneous(metadata_list, CANONICAL_TOLERANCES)` (ADR-0009). Si el helper aún no existe, crear un stub mínimo en `validation/geocoherence.py` con la signature contractual y dejar TODO. Tests:
- `test_detect_mode_B_collection` (REQ-003)
- `test_detect_mode_B_with_canonical_tolerances` (REQ-007)
- `test_extent_within_pixel_tolerance_accepted` (REQ-007 GEO-002)

**Criterio de done:**
- [ ] Tres tests verdes
- [ ] `is_homogeneous` invocado con `CANONICAL_TOLERANCES` (verificado con mock o spy)
- [ ] `metadata_index` poblado con todos los paths

**Archivos:**
- `src/tempify/detection/structure.py`
- `src/tempify/validation/geocoherence.py` (stub si no existe)
- `tests/structure_detection/test_mode_b_collection.py`

### task-2.7: Test + impl Modo C — lista explícita + bypass + coherencia

**Tipo:** test + impl
**Estimación:** 1.5h
**Bloquea:** task-2.9
**Bloqueada por:** task-2.4, task-2.5, task-2.6

**Descripción:** Rama lista (REQ-004, REQ-008). Preservar orden del usuario verbatim, forzar `confidence["structure_mode"] = 1.0`, pero ejecutar `is_homogeneous` igualmente (mode C bypass de detección, no de validación). Tests:
- `test_explicit_list_preserves_user_order` (REQ-004): orden user-provided respetado, sin re-sort
- `test_explicit_list_bypasses_detection_but_runs_coherence` (REQ-008)
- `test_mode_C_forces_structure_confidence_to_one` (REQ-008)
- `test_mode_C_heterogeneous_raises_HeterogeneousFilesError` (REQ-008)

**Criterio de done:**
- [ ] Cuatro tests verdes
- [ ] En mode C, `homogeneity == 1.0` también (design post-condición)

**Archivos:**
- `src/tempify/detection/structure.py`
- `tests/structure_detection/test_mode_c_explicit.py`

### task-2.8: Test + impl Heterogeneidad → AmbiguousStructureError + callback

**Tipo:** test + impl
**Estimación:** 2h
**Bloquea:** task-2.9
**Bloqueada por:** task-2.6

**Descripción:** Cuando `is_homogeneous` reporta inconsistencias en modo B, construir `AmbiguityReport` con groups, dimensions y diagnostics; invocar callback si existe (REQ-005b), o `raise AmbiguousStructureError`. Tests:
- `test_ambiguous_structure_raises` (REQ-005)
- `test_disambiguation_callback_invoked` (REQ-005b): callback resuelve subset coherente
- `test_disambiguation_callback_returns_none_raises` (REQ-005b: fallback a error)
- `test_disambiguation_callback_returns_empty_raises`
- `test_heterogeneous_crs_raises` (REQ-007 GEO-001)
- `test_resolution_outside_tolerance_raises` (REQ-007 GEO-003)
- `test_nodata_mismatch_raises` (REQ-007 GEO-004)
- `test_shape_mismatch_raises` (REQ-007 GEO-005)

**Criterio de done:**
- [ ] Ocho tests verdes
- [ ] Recursión callback de un solo nivel (no loop infinito); test que verifica
- [ ] `AmbiguityReport.groups` con clusters mutuamente homogéneos

**Archivos:**
- `src/tempify/detection/structure.py`
- `tests/structure_detection/test_ambiguity_and_callback.py`

### task-2.9: Test + impl `compute_structure_mode_confidence` (ADR-0008)

**Tipo:** test + impl
**Estimación:** 2h
**Bloquea:** task-2.11
**Bloqueada por:** task-2.7, task-2.8

**Descripción:** Implementar `compute_structure_mode_confidence` y `compute_homogeneity_confidence` bit-exact al pseudocódigo del design §5 algoritmo 4 / ADR-0008. Tests:
- `test_confidence_all_same_format_plus_crs_plus_extent` → 0.9
- `test_confidence_known_count_12_adds_0_1` → 1.0
- `test_confidence_mode_C_forced_to_one`
- `test_confidence_mode_A_homogeneity_is_one`
- `test_confidence_mode_B_partial_coherence_proportional`
- `test_confidence_clipped_to_one_max`

**Criterio de done:**
- [ ] Seis tests verdes
- [ ] Output bit-exact (mismas claves, mismos floats, mismo orden interno)
- [ ] Cobertura del módulo `confidence.py` ≥95%

**Archivos:**
- `src/tempify/detection/confidence.py`
- `tests/structure_detection/test_confidence_compute.py`

### task-2.10: Property test estabilidad de confidence (NFR-003)

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-3.2
**Bloqueada por:** task-2.9

**Descripción:** Property tests con Hypothesis:
- `test_confidence_dict_property_stable` (NFR-003): misma entrada produce mismo dict (estructural y numéricamente)
- `test_confidence_keys_set_invariant`: claves siempre exactamente `{"structure_mode", "homogeneity"}`
- `test_confidence_values_in_unit_interval`: ambos floats en `[0.0, 1.0]`

**Criterio de done:**
- [ ] Tres property tests verdes con `max_examples=200`
- [ ] Estrategias Hypothesis documentadas

**Archivos:**
- `tests/structure_detection/test_confidence_property.py`

### task-2.11: Integración `StructureDetector.detect` — wiring final

**Tipo:** impl
**Estimación:** 2h
**Bloquea:** task-3.1
**Bloqueada por:** task-2.9, task-2.10

**Descripción:** Ensamblar `StructureDetector.__init__` (con `tolerances`, `disambiguation_callback`, `recurse`) y `detect(source)` orquestando todos los helpers. Verificar que end-to-end retorne `StructureDetectionResult` correcto en cada modo. Test integrador:
- `test_detect_end_to_end_mode_A_netcdf`
- `test_detect_end_to_end_mode_B_collection_worldclim_like`
- `test_detect_end_to_end_mode_C_list`

**Criterio de done:**
- [ ] Tres tests integradores verdes
- [ ] Cobertura global `tempify.detection` ≥85% (NFR-002)
- [ ] `confidence["structure_mode"] >= 0.9` en fixture WorldClim-like

**Archivos:**
- `src/tempify/detection/structure.py`
- `tests/structure_detection/test_detector_end_to_end.py`

## Fase 3: Documentación e integración

### task-3.1: Docstrings NumPy completos + re-exports

**Tipo:** docs
**Estimación:** 1.5h
**Bloquea:** task-3.4
**Bloqueada por:** task-2.11

**Descripción:** Docstrings NumPy en todas las funciones/clases públicas (`StructureDetector`, `StructureDetectionResult`, `StructureMode`, errores, `compute_*_confidence`). Documentar excepciones lanzadas en `detect`. Verificar re-exports limpios en `tempify.detection.__init__`.

**Criterio de done:**
- [ ] `pydocstyle` (o `ruff` con `D` ruleset) sin warnings en el módulo
- [ ] `help(StructureDetector.detect)` muestra docstring legible
- [ ] `from tempify.detection import StructureDetector, StructureMode, StructureDetectionError, ...` funciona

**Archivos:**
- `src/tempify/detection/*.py`
- `src/tempify/detection/__init__.py`

### task-3.2: Test de integración con pipeline mock (propagación `band_descriptions`)

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-3.4
**Bloqueada por:** task-3.1

**Descripción:** Test integrador que verifica el contrato Capa 2 → resolver: dado un `StructureDetectionResult` (mode A multibanda con `band_descriptions` parseables), un pipeline mock invoca `TemporalFrequencyResolver.resolve(files=..., cf_metadata=..., band_descriptions=...)` y verifica que el resolver recibe los descriptors correctos (ADR-0015 §3 override-by-file).

**Criterio de done:**
- [ ] `test_pipeline_mock_propagates_band_descriptions_to_resolver` verde
- [ ] `test_pipeline_mock_mode_B_passes_filenames_to_resolver` verde (algoritmo 3b)
- [ ] Mock del resolver verifica argumentos por keyword

**Archivos:**
- `tests/structure_detection/test_pipeline_integration_mock.py`

### task-3.3: Benchmark NFR-001 (1000 archivos < 2s)

**Tipo:** test
**Estimación:** 2h
**Bloquea:** task-3.4
**Bloqueada por:** task-2.11

**Descripción:** Benchmark con `pytest-benchmark` o `time.perf_counter`. Generar 1000 GeoTIFF sintéticos homogéneos en `tmp_path_factory`. Assert `mean < 2.0s`. Marker `@pytest.mark.benchmark` y `skip` en CI si no es local (`--run-benchmark` opt-in).

**Criterio de done:**
- [ ] `test_detection_perf_1000_files` verde localmente (`pytest -m benchmark`)
- [ ] CI lo skipea por default
- [ ] Reporte de tiempo medio impreso

**Archivos:**
- `tests/benchmarks/test_detection_perf.py`
- `pyproject.toml` (marker registrado si falta)

### task-3.4: CHANGELOG + impl-log

**Tipo:** docs
**Estimación:** 0.5h
**Bloquea:** —
**Bloqueada por:** task-3.1, task-3.2, task-3.3

**Descripción:** Actualizar `CHANGELOG.md` con entrada `### Added — structure-detection` enumerando la API pública (`StructureDetector`, `StructureMode`, errores, `SIDECAR_EXTENSIONS`). Cerrar `specs/structure-detection/impl-log.md` con resumen final y métricas.

**Criterio de done:**
- [ ] CHANGELOG con sección bajo `[Unreleased]`
- [ ] impl-log con coverage final, perf medida, REQs cubiertos
- [ ] Spec marcada `Complete` en encabezado

**Archivos:**
- `CHANGELOG.md`
- `specs/structure-detection/impl-log.md`
- `specs/structure-detection/requirements.md` (cambio de estado)

## Resumen

| Fase | # tasks | Estimación total |
|---|---|---|
| Fase 1 (Fundamentos) | 7 | 5.5h |
| Fase 2 (Incremental) | 11 | 19.5h |
| Fase 3 (Docs+Integración) | 4 | 5.5h |
| **Total** | **22** | **30.5h** |

## Trazabilidad tasks → requirements

| REQ / NFR | Tasks |
|---|---|
| REQ-001 | task-2.4, task-2.5, task-2.6, task-2.7 |
| REQ-002 | task-2.4 |
| REQ-003 | task-2.4 (N=1), task-2.6 |
| REQ-004 | task-2.7 |
| REQ-005 | task-2.8 |
| REQ-005b | task-2.8 |
| REQ-006 | task-1.3, task-1.6, task-2.11 |
| REQ-007 | task-2.6, task-2.8 |
| REQ-008 | task-2.7 |
| REQ-009 | task-2.5 |
| REQ-010 | task-1.5, task-2.1, task-2.2 |
| REQ-011 | task-2.2 |
| NFR-001 | task-3.3 |
| NFR-002 | task-2.11, task-3.4 |
| NFR-003 | task-2.10 |
| ADR-0008 | task-1.3, task-2.9, task-2.10 |
| ADR-0009 | task-2.6, task-2.8 |
| ADR-0015 | task-2.5, task-3.2 |
