# Tasks — validation

**Estado:** Approved
**Design doc:** [design.md](design.md)
**Última actualización:** 2026-05-15

## Reglas para tasks

Cada task es atómica (≤ 4h, un commit), verificable (criterio observable de done), independiente cuando es posible, y estimada. Aplica TDD estricto: el test precede a la implementación.

Formato de cada task:

```
### task-N.M: <título corto>

**Tipo:** test | impl | refactor | docs | chore
**Estimación:** <horas>h
**Bloquea:** task-X.Y
**Bloqueada por:** task-W.V

**Descripción:** ...
**Criterio de done:**
- [ ] ...
**Archivos:**
- `path/to/file.py`
```

## Fase 1: Fundamentos

### task-1.1: Scaffolding del paquete `tempify.validation`

**Tipo:** chore
**Estimación:** 0.5h
**Bloquea:** task-1.2, task-1.3, task-1.4, task-1.5, task-1.6
**Bloqueada por:** —

**Descripción:** Crear la estructura del paquete con módulos vacíos placeholders (con docstrings + `__all__` vacíos) para permitir imports tempranos en tests.

**Criterio de done:**
- [ ] `src/tempify/validation/__init__.py` re-exporta los símbolos canónicos del design § 2.
- [ ] Módulos vacíos `errors.py`, `_codes.py`, `report.py`, `geocoherence.py`, `compatibility.py`, `post.py`, `statistics.py`, `profiles.py`.
- [ ] `mypy --strict` y `ruff` pasan sobre el paquete vacío.

**Archivos:**
- `src/tempify/validation/__init__.py`
- `src/tempify/validation/{errors,_codes,report,geocoherence,compatibility,post,statistics,profiles}.py`

### task-1.2: Test de enums `CheckSeverity` y `CheckPhase`

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** task-1.3
**Bloqueada por:** task-1.1

**Descripción:** Escribir test que valide los valores canónicos `INFO|WARN|ERROR` y `PRE_PROCESS|POST_PROCESS` declarados en `docs/schemas/validation-report.schema.md`.

**Criterio de done:**
- [ ] `test_check_severity_values` y `test_check_phase_values` fallan por falta de impl.
- [ ] Test verifica orden de severidad (`INFO < WARN < ERROR`).

**Archivos:**
- `tests/unit/validation/test_report.py`

### task-1.3: Implementar enums `CheckSeverity`, `CheckPhase`

**Tipo:** impl
**Estimación:** 0.5h
**Bloquea:** task-1.5
**Bloqueada por:** task-1.2

**Descripción:** `StrEnum` con los valores del schema.

**Criterio de done:**
- [ ] Tests de task-1.2 verdes.
- [ ] Docstring NumPy + type hints.

**Archivos:**
- `src/tempify/validation/report.py`

### task-1.4: Test de `CheckResult` y `ValidationReport` (schema canónico)

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-1.5
**Bloqueada por:** task-1.1

**Descripción:** Tests que verifican la shape exacta del `ValidationReport` contra `docs/schemas/validation-report.schema.md`. Cubre: campos canónicos (`checks`, `pre_passed`, `post_passed`, `warnings`, `errors`, `statistics`), helpers (`failed_errors`, `has_warnings`), y `to_json()` (NFR-001).

**Criterio de done:**
- [ ] `test_validation_report_serialization_keys` falla por falta de impl.
- [ ] `test_check_result_required_fields` (code, phase, severity, passed, message, details).
- [ ] `test_validation_report_to_json_roundtrip`.

**Archivos:**
- `tests/unit/validation/test_report.py`

### task-1.5: Implementar `CheckResult` y `ValidationReport`

**Tipo:** impl
**Estimación:** 2h
**Bloquea:** task-2.3, task-2.6, task-2.9
**Bloqueada por:** task-1.3, task-1.4

**Descripción:** Dataclasses (o pydantic v2) conformes al schema; `to_json` vía `json.dumps` con encoder para enums y `datetime`. `pre_passed`/`post_passed` derivados de `checks` por fase.

**Criterio de done:**
- [ ] Tests de task-1.4 verdes.
- [ ] Coverage del módulo ≥ 90%.
- [ ] mypy --strict + ruff verdes.

**Archivos:**
- `src/tempify/validation/report.py`

### task-1.6: Test + impl de `Tolerances` y `CANONICAL_TOLERANCES`

**Tipo:** test+impl
**Estimación:** 1h
**Bloquea:** task-2.5
**Bloqueada por:** task-1.1

**Descripción:** Frozen dataclass con los valores literales de ADR-0009 (`extent_rtol=1e-6`, `extent_atol_pixel_fraction=0.01`, `resolution_rtol=1e-6`, `crs_ignore_axis_order=True`, `nodata_strict=True`). Test verifica inmutabilidad y valores exactos.

**Criterio de done:**
- [ ] `test_canonical_tolerances_match_adr_0009` verde.
- [ ] Intento de mutación lanza `FrozenInstanceError`.

**Archivos:**
- `src/tempify/validation/geocoherence.py`
- `tests/unit/validation/test_geocoherence.py`

### task-1.7: Catálogo de códigos `_codes.py`

**Tipo:** impl
**Estimación:** 1.5h
**Bloquea:** task-2.5, task-2.7, task-2.9
**Bloqueada por:** task-1.1

**Descripción:** Diccionario inmutable mapeando cada código (`GEO-001..005`, `COMPAT-001..003`, `POST-001..004`) a `(default_severity, default_phase, message_template_es)`. Mensajes en español (NFR-002). Función `get_message(code, **kwargs)` para formateo.

**Criterio de done:**
- [ ] Todos los 12 códigos registrados.
- [ ] `test_codes_catalog_completeness` enumera y verifica.
- [ ] `test_error_messages_spanish` (NFR-002) verde con regex anti-inglés básica.

**Archivos:**
- `src/tempify/validation/_codes.py`
- `tests/unit/validation/test_codes.py`

### task-1.8: Excepciones tipadas

**Tipo:** test+impl
**Estimación:** 1h
**Bloquea:** task-2.5, task-2.7
**Bloqueada por:** task-1.5

**Descripción:** `PreValidationError(report)` y subclases `GeospatialIncoherenceError`, `MethodVariableIncompatibilityError`, `UnknownVariableProfileError`. Test verifica que portan `ValidationReport` accesible vía `.report`.

**Criterio de done:**
- [ ] `test_pre_validation_error_carries_report` verde.
- [ ] Jerarquía MRO correcta.

**Archivos:**
- `src/tempify/validation/errors.py`
- `tests/unit/validation/test_errors.py`

## Fase 2: Validadores (incremental)

### task-2.1: Test de carga `VariableProfile` contra schema

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-2.2
**Bloqueada por:** task-1.1

**Descripción:** Tests que cargan YAML válidos e inválidos (faltan required, `default_method ∉ allowed_methods`, units inconsistentes) y validan contra `docs/schemas/variable-profile.schema.yaml` con `jsonschema`. Verifican que pydantic v2 instancia con `frozen=True`, `extra="forbid"`.

**Criterio de done:**
- [ ] `test_profile_yaml_validates_against_schema` (fixtures válidas).
- [ ] `test_profile_yaml_rejects_invalid` (cada fixture inválida).
- [ ] `test_profile_is_frozen`.

**Archivos:**
- `tests/unit/validation/test_profiles.py`
- `tests/fixtures/profiles/valid/*.yaml`
- `tests/fixtures/profiles/invalid/*.yaml`

### task-2.2: Implementar loader `VariableProfile`

**Tipo:** impl
**Estimación:** 2.5h
**Bloquea:** task-2.4, task-2.7, task-2.9
**Bloqueada por:** task-2.1

**Descripción:** `VariableProfile.from_yaml(path)`: `yaml.safe_load` → validación `jsonschema` contra el schema canónico → `BaseModel(...)` pydantic con `frozen=True`. Carga del schema vía `importlib.resources.files("tempify.schemas")`.

**Criterio de done:**
- [ ] Tests de task-2.1 verdes.
- [ ] Tiempo de carga < 50 ms (verificable manual).

**Archivos:**
- `src/tempify/validation/profiles.py`

### task-2.3: 4 perfiles canónicos en `tempify.profiles`

**Tipo:** chore
**Estimación:** 2h
**Bloquea:** task-2.4, task-3.2
**Bloqueada por:** task-2.2

**Descripción:** Crear `temperature.yaml`, `precipitation.yaml`, `humidity.yaml`, `solar_radiation.yaml` conformes al schema. `precipitation.yaml` con `allowed_methods: []` y `default_method: linear` (per ADR-0004). Tests cargan cada perfil y verifican identidad de `canonical_name`.

**Criterio de done:**
- [ ] Los 4 archivos validados contra schema en test.
- [ ] `test_precipitation_profile_has_empty_allowed_methods` verde.
- [ ] `physical_range` con `strict=True` en precipitación (no negativos).

**Archivos:**
- `src/tempify/profiles/{temperature,precipitation,humidity,solar_radiation}.yaml`
- `tests/unit/validation/test_canonical_profiles.py`

### task-2.4: Test + impl `VariableProfileMatcher`

**Tipo:** test+impl
**Estimación:** 3h
**Bloquea:** task-3.2
**Bloqueada por:** task-2.3

**Descripción:** Matcher por scoring: CF `standard_name` (peso 3), alias exacto (peso 2), unidades + alias parcial (peso 1). Tests: `test_profile_matcher_cf_first`, `test_profile_matcher_alias_fallback`, `test_unknown_variable_raises` (lanza `UnknownVariableProfileError`).

**Criterio de done:**
- [ ] 3 tests verdes.
- [ ] Coverage ≥ 90% del módulo.

**Archivos:**
- `src/tempify/validation/profiles.py`
- `tests/unit/validation/test_profile_matcher.py`

### task-2.5: Test `GeospatialCoherenceValidator` (un test por código GEO)

**Tipo:** test
**Estimación:** 2.5h
**Bloquea:** task-2.6
**Bloqueada por:** task-1.6, task-1.7

**Descripción:** Fixtures sintéticos vía `rioxarray` con un solo eje alterado por test:
- `test_crs_mismatch_raises` → GEO-001.
- `test_extent_mismatch_raises` → GEO-002.
- `test_resolution_mismatch_raises` → GEO-003.
- `test_nodata_mismatch_raises` → GEO-004.
- `test_shape_mismatch_raises` → GEO-005.
- `test_homogeneous_passes_all_geo_checks` → INFO.

**Criterio de done:**
- [ ] 6 tests fallan por falta de impl.
- [ ] Fixtures generados en `conftest.py`.

**Archivos:**
- `tests/unit/validation/test_geocoherence.py`
- `tests/conftest.py`

### task-2.6: Impl `GeospatialCoherenceValidator`

**Tipo:** impl
**Estimación:** 3.5h
**Bloquea:** task-3.2
**Bloqueada por:** task-2.5, task-1.5

**Descripción:** Implementar comparaciones del design § 5.1 contra el primer raster como referencia. Devuelve `ValidationReport` con TODAS las inconsistencias (no short-circuit). Usa `pyproj.CRS.equals(ignore_axis_order=True)` y `numpy.isclose` con tolerancias canónicas.

**Criterio de done:**
- [ ] Los 6 tests de task-2.5 verdes.
- [ ] `mypy --strict` + `ruff` verdes.
- [ ] Coverage ≥ 85%.

**Archivos:**
- `src/tempify/validation/geocoherence.py`

### task-2.7: Test `MethodVariableCompatibilityChecker`

**Tipo:** test
**Estimación:** 2h
**Bloquea:** task-2.8
**Bloqueada por:** task-2.3, task-1.8

**Descripción:** Matriz de combinaciones (4 métodos × 4 variables):
- `test_method_variable_compat` (matriz COMPAT-001).
- `test_precipitation_rejects_smooth_methods` (COMPAT-002, ERROR, raises `MethodVariableIncompatibilityError`).
- `test_force_method_override_emits_warn` (REQ-010: COMPAT-003 WARN + `details["force_method"]`).

**Criterio de done:**
- [ ] 3 tests fallan por falta de impl.

**Archivos:**
- `tests/unit/validation/test_compatibility.py`

### task-2.8: Impl `MethodVariableCompatibilityChecker`

**Tipo:** impl
**Estimación:** 2h
**Bloquea:** task-3.2
**Bloqueada por:** task-2.7

**Descripción:** Implementar reglas del design § 5.2. Distingue precipitación (`allowed_methods == []`) → COMPAT-002 ERROR vs otras incompatibilidades → COMPAT-001 ERROR. `force=True` degrada a COMPAT-003 WARN.

**Criterio de done:**
- [ ] 3 tests de task-2.7 verdes.
- [ ] El caller (no este componente) lanza la excepción; el checker solo emite `CheckResult`.

**Archivos:**
- `src/tempify/validation/compatibility.py`

### task-2.9: Test `PostInterpolationValidator` (POST-001 conservación de media)

**Tipo:** test
**Estimación:** 2h
**Bloquea:** task-2.10
**Bloqueada por:** task-2.2, task-1.5

**Descripción:** `test_post_mean_preservation`: dos casos (preservación dentro de `atol=1e-4, rtol=1e-6` y violación). Property-based `test_mean_preservation_invariant` con hypothesis: arrays sintéticos donde el output es la repetición exacta del input mensual nunca falla.

**Criterio de done:**
- [ ] Test fail-case y pass-case definidos.
- [ ] Property test con ≥ 50 examples.

**Archivos:**
- `tests/unit/validation/test_post.py`

### task-2.10: Impl POST-001 (mean preservation)

**Tipo:** impl
**Estimación:** 3h
**Bloquea:** task-2.11
**Bloqueada por:** task-2.9

**Descripción:** Vectorizado con `xr.apply_ufunc(dask="parallelized")`. Tolerancia jerárquica: `profile.acceptable_mean_error` > `POST_VALIDATION_ABS_TOL=1e-4`, con `rtol=1e-6` (ADR-0010). `details` incluye `pixel_failure_pct`, `max_abs_error`, `tol_source`.

**Criterio de done:**
- [ ] Tests de task-2.9 verdes.
- [ ] Soporta inputs con `dask` chunks.

**Archivos:**
- `src/tempify/validation/post.py`

### task-2.11: Test + impl POST-002 (cyclic continuity)

**Tipo:** test+impl
**Estimación:** 3h
**Bloquea:** task-2.12
**Bloqueada por:** task-2.10

**Descripción:** Test `test_post_cyclic_continuity` con fixture `discontinuous_dec_jan.nc` (escalón artificial). Impl per design § 5.4: rolling 31d, comparación de `std` borde vs interior, factor 3.0 por defecto.

**Criterio de done:**
- [ ] Test detecta discontinuidad y emite POST-002 WARN.
- [ ] Caso continuo retorna passed=True.

**Archivos:**
- `src/tempify/validation/post.py`
- `tests/unit/validation/test_post.py`
- `tests/fixtures/series/discontinuous_dec_jan.nc`

### task-2.12: Test + impl POST-003 (physical range)

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.13
**Bloqueada por:** task-2.11

**Descripción:** `test_post_physical_range` con overshoot artificial. Distingue `strict=True` (POST-003 ERROR) vs `strict=False` (POST-003 WARN), per design § 5.5.

**Criterio de done:**
- [ ] Ambos modos cubiertos.
- [ ] `details["overshoot_pct"]` reportado.

**Archivos:**
- `src/tempify/validation/post.py`
- `tests/unit/validation/test_post.py`

### task-2.13: Test + impl POST-004 (NaN integrity)

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.14
**Bloqueada por:** task-2.12

**Descripción:** Test `test_post_nan_integrity`: detecta NaN nuevos en output donde el input era válido. Severidad ERROR (no WARN) por design § 5.6.

**Criterio de done:**
- [ ] Test verde.
- [ ] Caso simétrico (NaN preservado correctamente) retorna passed=True.

**Archivos:**
- `src/tempify/validation/post.py`
- `tests/unit/validation/test_post.py`

### task-2.14: Test + impl `StatisticalReporter`

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.15
**Bloqueada por:** task-2.13

**Descripción:** Tests: `test_statistical_reporter_keys` (6 claves canónicas por banda), `test_statistics_keys_invariant` (property-based). Impl con `xarray` reductions (`skipna=True`), indexado por timestamp ISO 8601.

**Criterio de done:**
- [ ] Salida tipo `dict[str, dict[str, float]]`.
- [ ] Las 6 claves siempre presentes.

**Archivos:**
- `src/tempify/validation/statistics.py`
- `tests/unit/validation/test_statistics.py`

### task-2.15: Política fail-fast pre vs warn-and-continue post

**Tipo:** test+impl
**Estimación:** 1.5h
**Bloquea:** task-3.2
**Bloqueada por:** task-2.6, task-2.14

**Descripción:** `test_fail_fast_pre_vs_warn_post` (REQ-009): un helper `enforce_pre(report)` lanza `PreValidationError(report)` si `not report.pre_passed`; los post-checks producen WARN en `report.warnings` + `logging.warning(...)` sin lanzar.

**Criterio de done:**
- [ ] Test verde.
- [ ] Helper público en `tempify.validation`.

**Archivos:**
- `src/tempify/validation/__init__.py`
- `tests/unit/validation/test_policy.py`

### task-2.16: Property test `test_tolerance_monotonicity`

**Tipo:** test
**Estimación:** 1h
**Bloquea:** —
**Bloqueada por:** task-2.10

**Descripción:** Incrementar `acceptable_mean_error` nunca convierte un PASS en FAIL. Property-based con hypothesis sobre el profile.

**Criterio de done:**
- [ ] Property test pasa con ≥ 100 examples.

**Archivos:**
- `tests/property/validation/test_tolerance_monotonicity.py`

## Fase 3: Documentación e integración

### task-3.1: Docstrings NumPy en todo el paquete

**Tipo:** docs
**Estimación:** 2h
**Bloquea:** task-3.4
**Bloqueada por:** task-2.15

**Descripción:** Completar docstrings NumPy en cada clase y función pública. Incluir Parameters, Returns, Raises, Examples y referencia al REQ correspondiente.

**Criterio de done:**
- [ ] `pydocstyle --convention=numpy` pasa.
- [ ] `interrogate --fail-under=95` pasa.

**Archivos:**
- `src/tempify/validation/*.py`

### task-3.2: Integration test cross-spec (core-interpolation + io-handlers)

**Tipo:** test
**Estimación:** 3h
**Bloquea:** task-3.4
**Bloqueada por:** task-2.6, task-2.8, task-2.13, task-2.4

**Descripción:** `test_end_to_end_pre_then_post`: lee fixture multi-tif vía io-handlers → `GeospatialCoherenceValidator` (pre) → `MethodVariableCompatibilityChecker` → mock-up PCHIP+RM (o impl real si disponible) → `PostInterpolationValidator`. Verifica `pre_passed=True`, `post_passed=True`, statistics no vacíos.

**Criterio de done:**
- [ ] Test corre en CI < 30s.
- [ ] Skipped con razón clara si specs upstream no implementadas.

**Archivos:**
- `tests/integration/test_validation_end_to_end.py`

### task-3.3: Benchmark NFR-003 (performance)

**Tipo:** test
**Estimación:** 2h
**Bloquea:** task-3.4
**Bloqueada por:** task-2.15

**Descripción:** `test_validation_performance_stack_12x3000x500` (NFR-003) asserta `< 10 s` en hardware de referencia. Usa `pytest-benchmark`. Marcado `@pytest.mark.perf` para opt-in en CI.

**Criterio de done:**
- [ ] Benchmark registrado.
- [ ] Memoria peak < 4 GB verificada con `tracemalloc`.

**Archivos:**
- `tests/perf/test_validation_perf.py`

### task-3.4: CHANGELOG + impl-log

**Tipo:** docs
**Estimación:** 0.5h
**Bloquea:** —
**Bloqueada por:** task-3.1, task-3.2, task-3.3

**Descripción:** Añadir entrada `## [Unreleased] - validation` en `CHANGELOG.md` con resumen de capabilities. Actualizar `specs/validation/impl-log.md` con bitácora de implementación, ADRs invocados, métricas finales (coverage, perf).

**Criterio de done:**
- [ ] CHANGELOG actualizado.
- [ ] `impl-log.md` con fecha de cierre y enlace al PR.

**Archivos:**
- `CHANGELOG.md`
- `specs/validation/impl-log.md`

## Resumen

| Fase | # tasks | Estimación total |
|---|---|---|
| Fase 1 | 8 | 8.5h |
| Fase 2 | 16 | 34.5h |
| Fase 3 | 4 | 7.5h |
| **Total** | **28** | **50.5h** |

## Trazabilidad task → REQ

| REQ | Tasks |
|---|---|
| REQ-001 | task-2.5, task-2.6 |
| REQ-002 | task-1.7, task-1.8, task-2.6 |
| REQ-003 | task-2.7, task-2.8 |
| REQ-004 | task-2.9, task-2.10 |
| REQ-005 | task-1.4, task-1.5 |
| REQ-006 | task-2.11 |
| REQ-007 | task-2.12 |
| REQ-008 | task-2.14 |
| REQ-009 | task-2.15 |
| REQ-010 | task-2.7, task-2.8 |
| NFR-001 | task-1.4, task-1.5 |
| NFR-002 | task-1.7 |
| NFR-003 | task-3.3 |
