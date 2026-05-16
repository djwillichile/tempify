# Tasks — temporal-frequency-resolver

**Estado:** Approved
**Design doc:** [design.md](design.md)
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-15

## Reglas para tasks

Cada task es atómica (≤4h), verificable, y sigue TDD estricto (test → impl). Cada task atómica = un commit. Trazabilidad explícita REQ/NFR → task en columna inferior. Las tasks de tests preceden a las de impl.

## Fase 1: Fundamentos

### task-1.1: Scaffolding del paquete `tempify.detection.frequency`

**Tipo:** chore
**Estimación:** 0.5h
**Bloquea:** task-1.2, task-1.3, task-1.4, task-1.5, task-1.6, task-1.7, task-1.8
**Bloqueada por:** —

**Descripción:** Crear estructura de directorios y archivos `__init__.py` vacíos para el paquete y sus subpaquetes (`parsers/`). Configurar `pyproject.toml` con el subpaquete (sin entry points aún; se cubre en task-2.30).

**Criterio de done:**
- [ ] Existen `src/tempify/detection/frequency/__init__.py`, `resolver.py`, `registry.py`, `cf_tier.py`, `heuristic.py`, `errors.py`, `parsers/__init__.py`, `parsers/base.py`
- [ ] `pytest --collect-only` no rompe
- [ ] `ruff check src/tempify/detection/frequency/` pasa (módulos vacíos)
- [ ] `mypy --strict` pasa

**Archivos:**
- `src/tempify/detection/frequency/__init__.py`
- `src/tempify/detection/frequency/resolver.py`
- `src/tempify/detection/frequency/registry.py`
- `src/tempify/detection/frequency/cf_tier.py`
- `src/tempify/detection/frequency/heuristic.py`
- `src/tempify/detection/frequency/errors.py`
- `src/tempify/detection/frequency/parsers/__init__.py`
- `src/tempify/detection/frequency/parsers/base.py`

### task-1.2: Test del enum `TemporalFrequency`

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** task-1.3
**Bloqueada por:** task-1.1

**Descripción:** Test que importa `TemporalFrequency` y verifica los seis miembros canónicos (`MONTHLY`, `DAILY`, `WEEKLY`, `CLIMATOLOGICAL`, `HOURLY`, `YEARLY`), valores como string, y consistencia con `docs/schemas/detection-result.schema.md`.

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre presencia de cada valor del schema canónico

**Archivos:**
- `tests/detection/frequency/test_enums.py`

### task-1.3: Impl `TemporalFrequency` enum

**Tipo:** impl
**Estimación:** 0.5h
**Bloquea:** task-1.4, task-2.x (todas las de tiers)
**Bloqueada por:** task-1.2

**Descripción:** Implementar `TemporalFrequency(StrEnum)` con valores en lowercase alineados al schema. Re-exportar desde `tempify.detection.frequency.__init__`.

**Criterio de done:**
- [ ] Test de task-1.2 verde
- [ ] Docstring NumPy completo
- [ ] mypy + ruff verdes

**Archivos:**
- `src/tempify/detection/frequency/resolver.py` (o módulo dedicado `enums.py`)

### task-1.4: Test del enum `ResolutionTier`

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** task-1.5
**Bloqueada por:** task-1.3

**Descripción:** Test de los cinco miembros (`CF_METADATA`, `FILENAME_PATTERN`, `COUNT_HEURISTIC`, `INTERACTIVE_CALLBACK`, `USER_OVERRIDE`) con sus string values exactos del design § 4.

**Criterio de done:**
- [ ] Test rojo
- [ ] Asserts sobre `.value` exacto

**Archivos:**
- `tests/detection/frequency/test_enums.py`

### task-1.5: Impl `ResolutionTier`

**Tipo:** impl
**Estimación:** 0.5h
**Bloquea:** task-1.6
**Bloqueada por:** task-1.4

**Descripción:** Implementar `ResolutionTier(StrEnum)` per design § 4.

**Criterio de done:**
- [ ] Test verde
- [ ] Docstring NumPy

**Archivos:**
- `src/tempify/detection/frequency/resolver.py`

### task-1.6: Test `ParseResult` dataclass

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-1.7
**Bloqueada por:** task-1.5

**Descripción:** Tests de construcción del dataclass `ParseResult` con sus siete campos (`frequency`, `confidence`, `time_point`, `time_range`, `month_of_year`, `year`, `band_index`). Verificar inmutabilidad (`frozen=True`, `slots=True`), tipos opcionales, y validación básica (e.g. `confidence ∈ [0, 1]`, `month_of_year ∈ [1, 12]`).

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre construcción válida e inválida (raises `ValueError`)

**Archivos:**
- `tests/detection/frequency/test_parse_result.py`

### task-1.7: Impl `ParseResult`

**Tipo:** impl
**Estimación:** 1h
**Bloquea:** task-1.8, task-2.4, task-2.6, task-2.8, task-2.10
**Bloqueada por:** task-1.6

**Descripción:** Implementar `ParseResult` dataclass `frozen=True, slots=True` con `__post_init__` validando rangos. Docstring NumPy.

**Criterio de done:**
- [ ] Tests verdes
- [ ] mypy --strict pasa
- [ ] Docstring documenta cada campo y su semántica

**Archivos:**
- `src/tempify/detection/frequency/parsers/base.py`

### task-1.8: Test `ResolutionResult` extendido

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-1.9
**Bloqueada por:** task-1.7

**Descripción:** Tests de `ResolutionResult` con campos `frequency`, `tier_used`, `confidence`, `source_evidence`, `time_axis`, `monthly_anchor_applied`, `calendar_agnostic`. Cubrir `__post_init__`: (a) `confidence ∈ [0, 1]`, (b) `len(source_evidence) < 200`, (c) sin `\n`, (d) `tier_used` ∈ enum, (e) `time_axis` estrictamente creciente cuando no es None, (f) `monthly_anchor_applied` ∈ literal.

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre cada invariante con caso negativo (raises)

**Archivos:**
- `tests/detection/frequency/test_resolution_result.py`

### task-1.9: Impl `ResolutionResult`

**Tipo:** impl
**Estimación:** 1.5h
**Bloquea:** task-1.10, task-2.x
**Bloqueada por:** task-1.8

**Descripción:** Implementar `ResolutionResult(frozen=True)` con `__post_init__` validando los siete invariantes. Mapeo documentado a `DetectionResult` per design § 4.

**Criterio de done:**
- [ ] Tests de task-1.8 verdes (`test_resolution_result_shape` incluido)
- [ ] Docstring NumPy con mapeo al schema
- [ ] mypy --strict pasa

**Archivos:**
- `src/tempify/detection/frequency/resolver.py`

### task-1.10: Test jerarquía de excepciones

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** task-1.11
**Bloqueada por:** task-1.9

**Descripción:** Tests para `FrequencyResolutionError` (incluye atributo `partial_evidence: dict`), `UnsupportedCalendarError` (subclase de la anterior), `ParserRegistrationError` (subclase de `ValueError`). Verificar herencia y construcción.

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre `isinstance` checks y atributo `partial_evidence`

**Archivos:**
- `tests/detection/frequency/test_errors.py`

### task-1.11: Impl excepciones

**Tipo:** impl
**Estimación:** 0.5h
**Bloquea:** task-1.12, task-2.x
**Bloqueada por:** task-1.10

**Descripción:** Implementar las tres excepciones per design § 3 con docstrings.

**Criterio de done:**
- [ ] Tests verdes
- [ ] Docstrings NumPy

**Archivos:**
- `src/tempify/detection/frequency/errors.py`

### task-1.12: Test `BaseFilenameParser` ABC

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** task-1.13
**Bloqueada por:** task-1.11

**Descripción:** Test que verifica que `BaseFilenameParser` es ABC: instanciar la clase base raises `TypeError`, exige `name: ClassVar[str]`, `confidence: ClassVar[float]`, y método abstracto `parse(filename: str) -> ParseResult | None`.

**Criterio de done:**
- [ ] Test rojo
- [ ] Subclase dummy que olvida `parse` no instancia

**Archivos:**
- `tests/detection/frequency/test_base_parser.py`

### task-1.13: Impl `BaseFilenameParser` ABC

**Tipo:** impl
**Estimación:** 0.5h
**Bloquea:** task-1.14, task-2.4..task-2.11
**Bloqueada por:** task-1.12

**Descripción:** Implementar la ABC con los atributos `ClassVar` y el método abstracto. Docstring que documenta el contrato.

**Criterio de done:**
- [ ] Test verde
- [ ] Docstring NumPy con pre/postcondiciones

**Archivos:**
- `src/tempify/detection/frequency/parsers/base.py`

### task-1.14: Test `FrequencyParserRegistry` (core API)

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-1.15
**Bloqueada por:** task-1.13

**Descripción:** Tests del registry core: `register(parser_cls)`, `iter_parsers()` retorna instancias en orden (built-ins → entry points → programmatic), `with_builtins()` factory. Cubre colisión de `name` → `ParserRegistrationError`. NO incluye entry points discovery (cubierto en task-2.32).

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre `test_registry_collision_raises`

**Archivos:**
- `tests/detection/frequency/test_registry.py`

### task-1.15: Impl `FrequencyParserRegistry` (sin entry points)

**Tipo:** impl
**Estimación:** 2h
**Bloquea:** task-1.16, task-2.x
**Bloqueada por:** task-1.14

**Descripción:** Implementar `FrequencyParserRegistry` con `register`, `iter_parsers`, `with_builtins`. Flag `load_entry_points=True` placeholder (no-op por ahora). Built-ins se registran como stubs si aún no existen (importar lazy o inyectar luego). Orden de iteración garantizado.

**Criterio de done:**
- [ ] Tests de task-1.14 verdes
- [ ] Docstring NumPy
- [ ] mypy --strict pasa

**Archivos:**
- `src/tempify/detection/frequency/registry.py`

### task-1.16: Test esqueleto `TemporalFrequencyResolver`

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-1.17
**Bloqueada por:** task-1.15

**Descripción:** Test que verifica el constructor (`registry`, `callback`) y la firma del método `resolve(files, cf_metadata=None, *, override=None) -> ResolutionResult`. Cubre `test_user_override_skips_detection` (REQ-005): pasar `override=TemporalFrequency.DAILY` retorna `ResolutionResult(DAILY, USER_OVERRIDE, 1.0, "user override")`.

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre REQ-005

**Archivos:**
- `tests/detection/frequency/test_resolver.py`

### task-1.17: Impl esqueleto `TemporalFrequencyResolver` + `override`

**Tipo:** impl
**Estimación:** 1h
**Bloquea:** task-2.1, task-2.2, task-2.x
**Bloqueada por:** task-1.16

**Descripción:** Implementar el constructor y el short-circuit `override` (líneas 1-3 del Algoritmo 1 del design). Resto del método raise `NotImplementedError` por ahora.

**Criterio de done:**
- [ ] Tests de task-1.16 verdes
- [ ] Docstring NumPy con pre/postcondiciones

**Archivos:**
- `src/tempify/detection/frequency/resolver.py`

## Fase 2: Incremental (tiers, parsers, ejes temporales, conflict resolution)

### task-2.1: Test tier 1 — CF metadata happy path

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.2
**Bloqueada por:** task-1.17

**Descripción:** Tests para `_parse_cf_metadata` (helper en `cf_tier.py`): (a) `units="days since 1970-01-01"`, valores `[0, 1, 2, ...]` → `DAILY` con confidence `1.0`; (b) deltas ~30d → `MONTHLY`; (c) deltas ~7d → `WEEKLY`; (d) deltas ~1h → `HOURLY`; (e) deltas ~365d → `YEARLY`. Fixture `synthetic_cf_monthly.json`.

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre cinco frecuencias canónicas

**Archivos:**
- `tests/detection/frequency/test_cf_tier.py`
- `tests/fixtures/synthetic_cf_monthly.json`

### task-2.2: Impl tier 1 — `_parse_cf_metadata`

**Tipo:** impl
**Estimación:** 2h
**Bloquea:** task-2.3
**Bloqueada por:** task-2.1

**Descripción:** Implementar `_parse_cf_metadata` per Algoritmo 2 del design usando `cftime.num2date`. Retorna `ResolutionResult` con `tier_used=CF_METADATA` y `confidence ∈ {0.95, 1.0}`. `source_evidence` formato `"CF time:units='...', Δ_mediana=Xd"`.

**Criterio de done:**
- [ ] Tests de task-2.1 verdes
- [ ] Confidence 0.95 cuando falta `calendar` (asumido `standard`)
- [ ] Docstring NumPy

**Archivos:**
- `src/tempify/detection/frequency/cf_tier.py`

### task-2.3: Test + impl `UnsupportedCalendarError` para calendarios no-estándar

**Tipo:** test+impl
**Estimación:** 1h
**Bloquea:** task-2.4
**Bloqueada por:** task-2.2

**Descripción:** Test `test_tier_cf_unsupported_calendar`: calendars `360_day`, `noleap`, `julian`, `all_leap` → `UnsupportedCalendarError`. Impl en `_parse_cf_metadata` la validación previa.

**Criterio de done:**
- [ ] Test rojo → verde tras impl
- [ ] Mensaje accionable en la excepción
- [ ] Cubre los cuatro calendarios prohibidos

**Archivos:**
- `tests/detection/frequency/test_cf_tier.py`
- `src/tempify/detection/frequency/cf_tier.py`

### task-2.4: Test `WorldClimParser` (REQ-010)

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.5
**Bloqueada por:** task-2.3

**Descripción:** Test `test_tier_worldclim_pattern_match`: 12 nombres canónicos `wc2.1_30s_tavg_01.tif`...`12.tif` → cada `parse()` retorna `ParseResult(frequency=MONTHLY, confidence=0.9, month_of_year=N, year=None)`. Variante con `year`: `wc2.1_30s_tavg_2020_01.tif`. Fixture `worldclim_names_set.json` con ≥10 variantes.

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre con/sin año, distintas resoluciones (30s/2.5m/5m/10m)

**Archivos:**
- `tests/detection/frequency/test_parsers_worldclim.py`
- `tests/fixtures/worldclim_names_set.json`

### task-2.5: Impl `WorldClimParser`

**Tipo:** impl
**Estimación:** 1.5h
**Bloquea:** task-2.6
**Bloqueada por:** task-1.7, task-1.13, task-2.4

**Descripción:** Implementar `WorldClimParser` con regex de grupos nombrados (`year?`, `month`) per design § 6. Docstring documenta patrón. Registrarlo como built-in en `FrequencyParserRegistry.with_builtins`.

**Criterio de done:**
- [ ] Tests verdes
- [ ] `name="worldclim"`, `confidence=0.9`
- [ ] Patrón en docstring

**Archivos:**
- `src/tempify/detection/frequency/parsers/worldclim.py`
- `src/tempify/detection/frequency/registry.py` (registro built-in)

### task-2.6: Test `ChelsaParser`

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** task-2.7
**Bloqueada por:** task-2.5

**Descripción:** Test `test_tier_chelsa_pattern_match`: nombres `CHELSA_tas_01_2020_V.2.1.tif` → `MONTHLY` con `year=2020`, `month_of_year=1`. Fixture `chelsa_names_set.json` con ≥10 variantes.

**Criterio de done:**
- [ ] Test rojo
- [ ] ≥10 variantes en fixture

**Archivos:**
- `tests/detection/frequency/test_parsers_chelsa.py`
- `tests/fixtures/chelsa_names_set.json`

### task-2.7: Impl `ChelsaParser`

**Tipo:** impl
**Estimación:** 1h
**Bloquea:** task-2.8
**Bloqueada por:** task-2.6

**Descripción:** Implementar `ChelsaParser` con regex de design § 6. Built-in registrado.

**Criterio de done:**
- [ ] Tests verdes
- [ ] Docstring documenta patrón

**Archivos:**
- `src/tempify/detection/frequency/parsers/chelsa.py`

### task-2.8: Test `ChirpsParser` (con y sin día)

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.9
**Bloqueada por:** task-2.7

**Descripción:** Test `test_tier_chirps_pattern_match`: (a) `chirps-v2.0.2020.01.15.tif` → `DAILY` con `time_point=datetime(2020,1,15)`; (b) `chirps-v2.0.2020.01.tif` → `MONTHLY` con `month_of_year=1`, `year=2020`. Fixture con ≥10 variantes mixtas.

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre ramificación con/sin grupo `day`

**Archivos:**
- `tests/detection/frequency/test_parsers_chirps.py`
- `tests/fixtures/chirps_names_set.json`

### task-2.9: Impl `ChirpsParser`

**Tipo:** impl
**Estimación:** 1h
**Bloquea:** task-2.10
**Bloqueada por:** task-2.8

**Descripción:** Implementar `ChirpsParser` con grupo `day` opcional. Frecuencia condicional al match del grupo.

**Criterio de done:**
- [ ] Tests verdes

**Archivos:**
- `src/tempify/detection/frequency/parsers/chirps.py`

### task-2.10: Test `Era5Parser` HOURLY vs DAILY

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-2.11
**Bloqueada por:** task-2.9

**Descripción:** Test `test_tier_era5_pattern_match`: (a) `era5_tas_20200115_00.nc` (grupo `hour` capturado) → `HOURLY`, `confidence=0.9`, `time_point` con hora; (b) `era5_tas_20200115.nc` (sin sufijo `_hh`) → `DAILY`, `confidence=0.85`. Validar grupos nombrados `var`, `year`, `month`, `day`, `hour`. Fixture con ≥10 variantes.

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre regla "presencia/ausencia del grupo `hour`" del design § 6

**Archivos:**
- `tests/detection/frequency/test_parsers_era5.py`
- `tests/fixtures/era5_names_set.json`

### task-2.11: Impl `Era5Parser`

**Tipo:** impl
**Estimación:** 1.5h
**Bloquea:** task-2.12
**Bloqueada por:** task-2.10

**Descripción:** Implementar `Era5Parser` con regex de cinco grupos nombrados y desambiguación HOURLY/DAILY por presencia del grupo `hour`.

**Criterio de done:**
- [ ] Tests verdes
- [ ] Docstring documenta la regla de desambiguación

**Archivos:**
- `src/tempify/detection/frequency/parsers/era5.py`

### task-2.12: Test `_try_parsers` consenso entre archivos

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.13
**Bloqueada por:** task-2.11

**Descripción:** Test del helper `_try_parsers(files, registry)`: (a) set homogéneo de 12 WorldClim → retorna `ResolutionResult` MONTHLY; (b) set con consenso parcial 9/12 (>=75%) → acepta; (c) consenso <75% → retorna None; (d) dos parsers matchean distintas frecuencias → primer parser gana, `source_evidence` con `WARN: nomenclature parsers in conflict`.

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre umbral 75% y colisión de parsers

**Archivos:**
- `tests/detection/frequency/test_resolver.py`

### task-2.13: Impl `_try_parsers`

**Tipo:** impl
**Estimación:** 2h
**Bloquea:** task-2.14
**Bloqueada por:** task-2.12

**Descripción:** Implementar `_try_parsers` per Algoritmo 3 del design (primeros K=min(8, N), consenso ≥75%, anota colisiones).

**Criterio de done:**
- [ ] Tests verdes
- [ ] Docstring NumPy

**Archivos:**
- `src/tempify/detection/frequency/resolver.py`

### task-2.14: Test `MultiBandGeoTIFFBandDescriptionParser`

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.15
**Bloqueada por:** task-2.13

**Descripción:** Test del parser auxiliar: input `band_descriptions=["2020-01-15", "2020-01-16", ...]` → retorna `ResolutionResult` con `time_axis` directo (REQ-013). Si solo subconjunto parsea ISO 8601 → retorna `None` (sin fallback parcial). Cubre formatos `YYYY-MM-DD` y `YYYY-MM-DDTHH:MM:SS`.

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre éxito total y degradación

**Archivos:**
- `tests/detection/frequency/test_parsers_band_descriptions.py`

### task-2.15: Impl `MultiBandGeoTIFFBandDescriptionParser`

**Tipo:** impl
**Estimación:** 1.5h
**Bloquea:** task-2.16
**Bloqueada por:** task-2.14

**Descripción:** Implementar el parser auxiliar per Algoritmo 7. NO se registra como `BaseFilenameParser` regular (firma distinta: recibe band descriptions, no filename); se expone como helper inyectable al resolver vía parámetro opcional.

**Criterio de done:**
- [ ] Tests verdes
- [ ] Docstring documenta diferencia con `BaseFilenameParser`

**Archivos:**
- `src/tempify/detection/frequency/parsers/band_descriptions.py`

### task-2.16: Test tier 3 — count heuristic 12 con/sin año

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.17
**Bloqueada por:** task-2.15

**Descripción:** Test `test_tier_heuristic_count_12_means_monthly`: (a) 12 nombres con token `\d{4}` → `MONTHLY`; (b) 12 nombres sin `\d{4}` → `CLIMATOLOGICAL`. Confidence `0.7`. `source_evidence = "count_heuristic N=12, year_token=present|absent"`.

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre los dos sub-casos

**Archivos:**
- `tests/detection/frequency/test_heuristic.py`

### task-2.17: Test tier 3 — count heuristic 24/52/365/366/YEARLY

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** task-2.18
**Bloqueada por:** task-2.16

**Descripción:** Tests `test_tier_heuristic_count_365_means_daily`, `test_tier_heuristic_count_24_means_hourly`, `test_tier_heuristic_count_52_means_weekly`, `test_tier_heuristic_n_distinct_years_means_yearly`, `test_tier_heuristic_no_match_returns_none`.

**Criterio de done:**
- [ ] Tests rojos
- [ ] Cubre cada rama del match-case del Algoritmo 4

**Archivos:**
- `tests/detection/frequency/test_heuristic.py`

### task-2.18: Impl `_resolve_from_count`

**Tipo:** impl
**Estimación:** 1.5h
**Bloquea:** task-2.19
**Bloqueada por:** task-2.17

**Descripción:** Implementar `_resolve_from_count` per Algoritmo 4 con match-case sobre N. Confidence fija `0.7`.

**Criterio de done:**
- [ ] Tests de task-2.16 y task-2.17 verdes
- [ ] Idempotencia: orden de `files` no afecta resultado (test `test_count_heuristic_idempotent`)

**Archivos:**
- `src/tempify/detection/frequency/heuristic.py`

### task-2.19: Test tier 4 — callback injection

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.20
**Bloqueada por:** task-2.18

**Descripción:** Tests `test_callback_invoked_when_ambiguous` (REQ-004a) y `test_raises_when_no_callback_and_unknown` (REQ-004b): (a) tiers no convergen + callback inyectado → callback recibe `candidates: list[ResolutionResult]`, retorna `TemporalFrequency`, resolver retorna `ResolutionResult(..., INTERACTIVE_CALLBACK, 0.4, "callback chose <freq>")`; (b) sin callback → `FrequencyResolutionError` con `partial_evidence` poblado.

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre los dos REQ
- [ ] Test `test_partial_evidence_in_exception` verifica las tres keys en el dict

**Archivos:**
- `tests/detection/frequency/test_resolver.py`

### task-2.20: Impl orquestación completa `resolve()` (sin conflict annotation)

**Tipo:** impl
**Estimación:** 2.5h
**Bloquea:** task-2.21
**Bloqueada por:** task-2.19

**Descripción:** Implementar el Algoritmo 1 completo en `TemporalFrequencyResolver.resolve` (líneas 1-13: override, tier 1, tier 2, tier 3, first-non-null winner, tier 4 callback, raise). Aún sin `_annotate_conflicts` (cubierto en task-2.22). Verifica que `_try_parsers` puede aceptar tanto el `MultiBandGeoTIFFBandDescriptionParser` (vía parámetro opcional `band_descriptions`) como los filename parsers.

**Criterio de done:**
- [ ] Tests de task-2.19 verdes
- [ ] Docstring NumPy completa
- [ ] mypy --strict pasa

**Archivos:**
- `src/tempify/detection/frequency/resolver.py`

### task-2.21: Test higher-wins conflict resolution (REQ-008)

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.22
**Bloqueada por:** task-2.20

**Descripción:** Test `test_conflicting_tiers_higher_wins`: CF=MONTHLY, parser=DAILY → `tier_used=CF_METADATA`, frequency=MONTHLY, `source_evidence` empieza con `WARN: cf_units=monthly > nomenclature=daily`. Variantes: dos pares de tiers, y caso "no hay conflicto" (no se inyecta WARN).

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre tres escenarios

**Archivos:**
- `tests/detection/frequency/test_resolver.py`

### task-2.22: Impl `_annotate_conflicts`

**Tipo:** impl
**Estimación:** 1.5h
**Bloquea:** task-2.23
**Bloqueada por:** task-2.21

**Descripción:** Implementar `_annotate_conflicts(winner, partial)` per Algoritmo 5. Detecta discrepancias en `frequency` entre tiers no-null y prefija `source_evidence` con `WARN: <winner_tier>={X} > <other_tier>={Y}`. Mantiene `<200 chars`.

**Criterio de done:**
- [ ] Tests de task-2.21 verdes
- [ ] Asegura no superar el límite de 200 chars (truncado controlado si necesario)

**Archivos:**
- `src/tempify/detection/frequency/resolver.py`

### task-2.23: Test construcción de `time_axis` desde filenames (REQ-011)

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-2.24
**Bloqueada por:** task-2.22

**Descripción:** Tests `test_worldclim_extracts_month_only_axis_with_midpoint`, `test_chelsa_extracts_year_month_axis`, `test_chirps_extracts_daily_axis`, `test_era5_extracts_hourly_axis`. Validan: (a) axis presente en `ResolutionResult.time_axis`; (b) longitud consistente con files; (c) midpoint aplicado (día ≈15) cuando solo hay mes; (d) `calendar_agnostic=True` cuando no hay año (WorldClim sin año).

**Criterio de done:**
- [ ] Tests rojos
- [ ] Cubre los cuatro catálogos built-in

**Archivos:**
- `tests/detection/frequency/test_time_axis.py`

### task-2.24: Impl `_build_time_axis` (sin anchor configurable)

**Tipo:** impl
**Estimación:** 2.5h
**Bloquea:** task-2.25
**Bloqueada por:** task-2.23

**Descripción:** Implementar `_build_time_axis(parse_results, anchor="midpoint", band_descriptions=None)` per Algoritmo 6 pasos 1-3, 5, 7-8. Default anchor=midpoint (ADR-0015). Ordena y deduplica. Valida continuidad ±10%.

**Criterio de done:**
- [ ] Tests de task-2.23 verdes
- [ ] Docstring NumPy referencia ADR-0015

**Archivos:**
- `src/tempify/detection/frequency/resolver.py` (o módulo `_axis.py` dedicado)

### task-2.25: Test `monthly_anchor` override (REQ-012)

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.26
**Bloqueada por:** task-2.24

**Descripción:** Tests `test_monthly_anchor_override_start` (todos los time points caen en día 1), `test_monthly_anchor_override_end` (último día del mes), `test_monthly_anchor_override_custom` (callable inyectado). Validar `ResolutionResult.monthly_anchor_applied` refleja el anchor usado.

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre los cuatro valores del literal

**Archivos:**
- `tests/detection/frequency/test_time_axis.py`

### task-2.26: Impl `monthly_anchor` override en `_build_time_axis`

**Tipo:** impl
**Estimación:** 1.5h
**Bloquea:** task-2.27
**Bloqueada por:** task-2.25

**Descripción:** Extender `_build_time_axis` para aceptar `anchor: Literal['midpoint','start','end','custom']` y `custom_fn` opcional. Aplicar en pasos 4-5 del Algoritmo 6. Propagar a `resolve()` vía parámetro opcional. Poblar `monthly_anchor_applied`.

**Criterio de done:**
- [ ] Tests de task-2.25 verdes
- [ ] Default sigue siendo `midpoint`
- [ ] `custom` sin `custom_fn` → `ValueError`

**Archivos:**
- `src/tempify/detection/frequency/resolver.py`

### task-2.27: Test warning calendar-agnostic

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** task-2.28
**Bloqueada por:** task-2.26

**Descripción:** Test `test_calendar_agnostic_warning_when_no_year`: set WorldClim sin año → captura warning con `pytest.warns` cuyo mensaje contiene `CALENDAR_AGNOSTIC`. Verificar `ResolutionResult.calendar_agnostic=True`.

**Criterio de done:**
- [ ] Test rojo
- [ ] Captura warning con `pytest.warns(UserWarning)`

**Archivos:**
- `tests/detection/frequency/test_time_axis.py`

### task-2.28: Impl emisión de warning calendar-agnostic

**Tipo:** impl
**Estimación:** 0.5h
**Bloquea:** task-2.29
**Bloqueada por:** task-2.27

**Descripción:** Emitir `warnings.warn("CALENDAR_AGNOSTIC: month-only encoding (no year present)", UserWarning, stacklevel=2)` en paso 5 del Algoritmo 6.

**Criterio de done:**
- [ ] Test verde
- [ ] Warning solo se emite cuando ningún ParseResult del set tiene `year`

**Archivos:**
- `src/tempify/detection/frequency/resolver.py`

### task-2.29: Test precedencia band descriptions > filename (REQ-013)

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.30
**Bloqueada por:** task-2.28

**Descripción:** Test `test_multiband_geotiff_band_description_axis`: input multi-band con `band_descriptions` ISO 8601 válidas + filenames WorldClim → axis viene de las band descriptions; filename parsing se invoca pero NO contribuye al axis. Si band descriptions no parsean ISO → fallback a filenames.

**Criterio de done:**
- [ ] Test rojo
- [ ] Cubre precedencia y fallback

**Archivos:**
- `tests/detection/frequency/test_time_axis.py`

### task-2.30: Impl precedencia band descriptions

**Tipo:** impl
**Estimación:** 1h
**Bloquea:** task-2.31
**Bloqueada por:** task-2.29

**Descripción:** Implementar paso 1 del Algoritmo 6: si `band_descriptions` parsean todas → usar; si no → ignorar y caer a filename parsing. Integrar en `resolve()`.

**Criterio de done:**
- [ ] Tests verdes
- [ ] Sin fallback parcial (todo o nada per Algoritmo 7)

**Archivos:**
- `src/tempify/detection/frequency/resolver.py`

### task-2.31: Test `test_builtin_parsers_preregistered` (REQ-006)

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** task-2.32
**Bloqueada por:** task-2.30

**Descripción:** Test que verifica que `FrequencyParserRegistry.with_builtins()` contiene exactamente los cuatro built-ins por `name`: `worldclim`, `chelsa`, `chirps`, `era5`. `iter_parsers()` los retorna en ese orden.

**Criterio de done:**
- [ ] Test verde con los parsers ya implementados

**Archivos:**
- `tests/detection/frequency/test_registry.py`

### task-2.32: Test + impl entry point discovery (REQ-009, NFR-003)

**Tipo:** test+impl
**Estimación:** 3h
**Bloquea:** task-2.33
**Bloqueada por:** task-2.31

**Descripción:** Tests `test_registry_entry_point_discovery` y `test_registry_accepts_external_parser`. Fixture instala un parser dummy vía mock de `importlib.metadata.entry_points(group="tempify.frequency_parsers")`; verificar descubrimiento. Impl: en `FrequencyParserRegistry.__init__` con `load_entry_points=True`, cargar entry points y cachearlos. Orden: built-ins → entry points → programmatic.

**Criterio de done:**
- [ ] Tests rojos → verdes
- [ ] Cubre NFR-003 (mecanismo dual documentado)
- [ ] Test de orden de iteración

**Archivos:**
- `tests/detection/frequency/test_registry.py`
- `tests/detection/frequency/fixtures/dummy_external_parser.py`
- `src/tempify/detection/frequency/registry.py`

### task-2.33: Property test catálogo built-in (NFR-002)

**Tipo:** test
**Estimación:** 2h
**Bloquea:** task-3.1
**Bloqueada por:** task-2.32

**Descripción:** Test `test_catalog_property_coverage` parametrizado con `@pytest.mark.parametrize` sobre fixtures de ≥10 variantes por catálogo (WorldClim, CHELSA, CHIRPS, ERA5). Cada variante debe ser reconocida por su parser correspondiente y rechazada por los otros tres. Opcionalmente usar `hypothesis` para generar variantes de resolución (`30s`, `2.5m`, ...) y de números de mes/día.

**Criterio de done:**
- [ ] Todas las variantes reconocidas
- [ ] 40+ casos parametrizados
- [ ] Cumple NFR-002

**Archivos:**
- `tests/detection/frequency/test_catalog_property.py`

## Fase 3: Documentación, integración y rendimiento

### task-3.1: Docstrings NumPy en API pública

**Tipo:** docs
**Estimación:** 2h
**Bloquea:** task-3.2
**Bloqueada por:** task-2.33

**Descripción:** Auditar y completar docstrings NumPy en `TemporalFrequencyResolver`, `ResolutionResult`, `ParseResult`, `FrequencyParserRegistry`, `BaseFilenameParser`, las cuatro subclases built-in, `MultiBandGeoTIFFBandDescriptionParser`, jerarquía de excepciones, helpers `_parse_cf_metadata`, `_resolve_from_count`, `_build_time_axis`. Incluir Parameters, Returns, Raises, Examples, Notes con referencias a REQ/ADR.

**Criterio de done:**
- [ ] `pydocstyle` pasa
- [ ] Cada función pública tiene Example ejecutable
- [ ] Referencias a ADR-0008 y ADR-0015 presentes

**Archivos:**
- Todos los `.py` del paquete

### task-3.2: Integration test con mock de `StructureDetector`

**Tipo:** test
**Estimación:** 2h
**Bloquea:** task-3.3
**Bloqueada por:** task-3.1

**Descripción:** Test de integración: instanciar `TemporalFrequencyResolver` con built-ins y un mock de `StructureDetector` que consume el `ResolutionResult` y construye un `DetectionResult` parcial. Verificar mapeo per design § 4: `frequency → temporal_frequency`, `tier_used → confidence.temporal_frequency_tier` (vía tabla ADR-0008), `confidence → confidence.temporal_frequency`, `source_evidence → evidence.temporal_frequency`. Cubre los cinco tier values.

**Criterio de done:**
- [ ] Test verde
- [ ] Schema validation contra `docs/schemas/detection-result.schema.md`

**Archivos:**
- `tests/integration/test_resolver_with_structure_detector.py`

### task-3.3: Benchmark NFR-001 (<100 ms para 366 archivos)

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-3.4
**Bloqueada por:** task-3.2

**Descripción:** Benchmark `test_366_files_under_100ms`: input sintético de 366 nombres CHIRPS, ejecución single-thread, `pytest-benchmark` o `time.perf_counter`. Asserta `< 100 ms`. Variante con 12 nombres WorldClim debe ser <10 ms.

**Criterio de done:**
- [ ] Benchmark pasa en CI
- [ ] Reporte de p50/p95 documentado
- [ ] No regresión

**Archivos:**
- `bench/test_resolver_perf.py`

### task-3.4: CHANGELOG + cierre

**Tipo:** docs
**Estimación:** 0.5h
**Bloquea:** —
**Bloqueada por:** task-3.3

**Descripción:** Añadir entrada en `CHANGELOG.md` bajo `[Unreleased]` describiendo: nuevo módulo `tempify.detection.frequency`, enums `TemporalFrequency` y `ResolutionTier`, dataclasses `ParseResult` y `ResolutionResult`, registry extensible, cuatro parsers built-in, parser auxiliar de band descriptions, jerarquía de excepciones. Referenciar REQs cubiertos.

**Criterio de done:**
- [ ] CHANGELOG actualizado
- [ ] Sección "Added" lista cada componente
- [ ] Referencias a ADR-0008, ADR-0015

**Archivos:**
- `CHANGELOG.md`

## Trazabilidad REQ/NFR → tasks

| REQ/NFR | Tasks |
|---|---|
| REQ-001 (jerarquía de tiers + enum) | task-1.2, task-1.3, task-2.20 |
| REQ-002 (CF metadata tier) | task-2.1, task-2.2, task-2.3 |
| REQ-003 (parser tier confidence ≤0.9) | task-1.12, task-1.13, task-2.4..task-2.11 |
| REQ-004a (callback) | task-2.19, task-2.20 |
| REQ-004b (raise sin callback) | task-2.19, task-2.20 |
| REQ-005 (user override) | task-1.16, task-1.17 |
| REQ-006 (built-ins pre-registrados) | task-2.5, task-2.7, task-2.9, task-2.11, task-2.31 |
| REQ-007 (ResolutionResult shape) | task-1.8, task-1.9 |
| REQ-008 (higher-wins conflict) | task-2.21, task-2.22 |
| REQ-009 (registry extensible) | task-1.14, task-1.15, task-2.32 |
| REQ-010 (cuatro parsers built-in) | task-2.4..task-2.11 |
| REQ-011 (time_axis desde filenames) | task-2.23, task-2.24 |
| REQ-012 (monthly_anchor) | task-2.25, task-2.26 |
| REQ-013 (band descriptions ISO) | task-2.14, task-2.15, task-2.29, task-2.30 |
| NFR-001 (perf <100 ms) | task-3.3 |
| NFR-002 (property test ≥10 variantes) | task-2.33 |
| NFR-003 (registry dual) | task-2.32 |
| NFR-004 (coverage ≥85%) | cobertura emergente de la suite + CI |

## Resumen

| Fase | # tasks | Estimación total |
|---|---|---|
| Fase 1 Fundamentos | 17 (task-1.1..task-1.17) | 13.5h |
| Fase 2 Incremental | 33 (task-2.1..task-2.33) | 41.5h |
| Fase 3 Docs+Integración | 4 (task-3.1..task-3.4) | 6h |
| **Total** | **54** | **61h** |
