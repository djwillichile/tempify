# Tasks — pipeline

**Estado:** Approved
**Design doc:** [design.md](design.md)
**Última actualización:** 2026-05-16

## Reglas para tasks

Cada task debe ser:

- **Atómica:** completable en una sesión (≤4h), un commit.
- **Verificable:** tiene un criterio de done observable.
- **TDD estricto:** task de tipo `test` precede a su `impl`; el test debe fallar (rojo) antes de la implementación.
- **Independiente** en lo posible: dependencias declaradas vía `Bloqueada por`.

Pipeline es la spec más compleja del proyecto: integra Detection, Validation, Interpolation e I/O. Toda task debe respetar las reglas arquitectónicas duras (capa 5 no importa `typer`, `rich`, `sys.stdin`) y los ADRs 0007/0008/0010/0014/0015.

## Fase 1: Fundamentos

### task-1.1: Scaffolding del paquete `tempify.pipeline`

**Tipo:** chore
**Estimación:** 1h
**Bloquea:** task-1.2, task-1.3, task-1.4, task-1.5, task-1.6, task-1.7
**Bloqueada por:** —

**Descripción:** Crear estructura de archivos del módulo `src/tempify/pipeline/` con `__init__.py`, `core.py`, `config.py`, `result.py`, `callbacks.py`, `report.py`, `errors.py`, `runtime.py` (todos como stubs vacíos con docstring de módulo). Registrar el módulo en `pyproject.toml` si corresponde.

**Criterio de done:**
- [ ] 8 archivos creados bajo `src/tempify/pipeline/`
- [ ] `from tempify import pipeline` no rompe
- [ ] `ruff check` pasa sobre el módulo vacío

**Archivos:**
- `src/tempify/pipeline/__init__.py`
- `src/tempify/pipeline/core.py`
- `src/tempify/pipeline/config.py`
- `src/tempify/pipeline/result.py`
- `src/tempify/pipeline/callbacks.py`
- `src/tempify/pipeline/report.py`
- `src/tempify/pipeline/errors.py`
- `src/tempify/pipeline/runtime.py`

### task-1.2: Test de la jerarquía de excepciones `TempifyPipelineError`

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-1.3
**Bloqueada por:** task-1.1

**Descripción:** Escribir `tests/unit/pipeline/test_errors.py` cubriendo: (a) `TempifyPipelineError` como base; (b) subclases `PipelinePreValidationError`, `PipelineInterpolationError`, `PipelineWriteError`, `PipelineReportError`, `InvalidConfigError`; (c) atributos `error_code` y `message` accesibles; (d) preservación de `__cause__` con `raise ... from e`; (e) `EXIT_CODES` mapping con códigos canónicos. Cubre REQ-009.

**Criterio de done:**
- [ ] Test creado y falla en rojo (las clases no existen aún)
- [ ] Cubre los 5 subtipos de excepción + `EXIT_CODES`
- [ ] Verifica mensajes en español (`NFR-006`)

**Archivos:**
- `tests/unit/pipeline/test_errors.py`

### task-1.3: Implementación de `tempify.pipeline.errors`

**Tipo:** impl
**Estimación:** 1.5h
**Bloquea:** task-1.6, task-1.8
**Bloqueada por:** task-1.2

**Descripción:** Implementar `TempifyPipelineError(Exception)` con `error_code: str`, subclases (`PipelinePreValidationError`, `PipelineInterpolationError`, `PipelineWriteError`, `PipelineReportError`, `InvalidConfigError`), y el mapping público `EXIT_CODES: dict[type[TempifyPipelineError], int]` que la CLI consume (ver `specs/cli/design.md`). Mensajes en español, `error_code` en inglés.

**Criterio de done:**
- [ ] Tests de task-1.2 verdes
- [ ] `mypy --strict` pasa
- [ ] Docstrings NumPy completos en cada clase
- [ ] `EXIT_CODES` documentado y exportado en `__init__.py`

**Archivos:**
- `src/tempify/pipeline/errors.py`
- `src/tempify/pipeline/__init__.py`

### task-1.4: Test del `Protocol` `ProgressCallback`

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-1.5
**Bloqueada por:** task-1.1

**Descripción:** Escribir `tests/unit/pipeline/test_callbacks.py` con: (a) un callback dummy que conforma al `Protocol`; (b) verificación `mypy --strict` mediante `reveal_type` o test de tipos en un archivo `tests/typing/test_progress_callback_typing.py`; (c) verificación de que `phase` es un `Literal` cerrado con exactamente las 7 fases canónicas (`detect`, `validate_geospatial`, `validate_compatibility`, `interpolate`, `validate_post`, `write`, `generate_report`); (d) verificación análoga del `Protocol` `FrequencyResolverProtocol`. Cubre REQ-003, REQ-012.

**Criterio de done:**
- [ ] Test creado y rojo
- [ ] Test de typing con mypy ejecutable en CI
- [ ] Cubre los dos Protocols

**Archivos:**
- `tests/unit/pipeline/test_callbacks.py`
- `tests/typing/test_progress_callback_typing.py`

### task-1.5: Implementación de `tempify.pipeline.callbacks`

**Tipo:** impl
**Estimación:** 1h
**Bloquea:** task-1.7
**Bloqueada por:** task-1.4

**Descripción:** Definir `PipelinePhase = Literal[...]` con las 7 fases, `ProgressCallback(Protocol)` con firma exacta de REQ-003, y `FrequencyResolverProtocol(Protocol)` con firma de REQ-012. Re-exportar desde `__init__.py`.

**Criterio de done:**
- [ ] Tests de task-1.4 verdes
- [ ] `mypy --strict` valida los Protocols
- [ ] Docstrings NumPy completos

**Archivos:**
- `src/tempify/pipeline/callbacks.py`

### task-1.6: Test de `PipelineConfig` (todos los campos e invariantes)

**Tipo:** test
**Estimación:** 3h
**Bloquea:** task-1.7
**Bloqueada por:** task-1.3, task-1.5

**Descripción:** Escribir `tests/unit/pipeline/test_config.py` cubriendo:
- Construcción con todos los campos del design (method, target_freq, output_dir, output_format, chunk_size, scheduler, reproducibility_mode, progress_callback, progress_frequency_hz, frequency_resolver_callback, dry_run, force_method, variable_profile_override, seed, method_options, skip_pre_validation, monthly_anchor, custom_time_axis).
- Inmutabilidad (`frozen=True`, `slots=True`): asignación post-construcción levanta `FrozenInstanceError`.
- Invariantes:
  - `skip_pre_validation=True, dry_run=False` → `InvalidConfigError(error_code="PIPELINE_INVALID_CONFIG_SKIP_REQUIRES_DRY_RUN")`.
  - `monthly_anchor="custom", custom_time_axis=None` → `InvalidConfigError(error_code="PIPELINE_INVALID_CONFIG_CUSTOM_ANCHOR_REQUIRES_AXIS")`.
  - `monthly_anchor="midpoint", custom_time_axis=(...)` → `InvalidConfigError(error_code="PIPELINE_INVALID_CONFIG_AXIS_WITHOUT_CUSTOM_ANCHOR")`.
  - `reproducibility_mode="strict"` fuerza `scheduler="synchronous"` (warning si el usuario pasó otro).
  - `progress_frequency_hz <= 0` → `InvalidConfigError`.
  - `method_options` congelado en `MappingProxyType`.

**Criterio de done:**
- [ ] Test creado y rojo
- [ ] ≥18 casos de test (uno por invariante + happy paths)

**Archivos:**
- `tests/unit/pipeline/test_config.py`

### task-1.7: Implementación de `PipelineConfig`

**Tipo:** impl
**Estimación:** 3h
**Bloquea:** task-1.9, task-2.1
**Bloqueada por:** task-1.6

**Descripción:** Implementar `@dataclass(frozen=True, slots=True) class PipelineConfig` con todos los campos del design §3, incluyendo `skip_pre_validation`, `monthly_anchor`, `custom_time_axis`. Implementar `__post_init__` con todas las invariantes (ver task-1.6). Usar `object.__setattr__` para inicializaciones derivadas (e.g., congelar `method_options` con `MappingProxyType`).

**Criterio de done:**
- [ ] Tests de task-1.6 verdes
- [ ] `mypy --strict` pasa
- [ ] Docstring NumPy del dataclass + cada campo no obvio documentado
- [ ] Exportado desde `__init__.py`

**Archivos:**
- `src/tempify/pipeline/config.py`

### task-1.8: Test e impl de `PipelineResult`

**Tipo:** test+impl
**Estimación:** 1h
**Bloquea:** task-2.1
**Bloqueada por:** task-1.3

**Descripción:** Test que verifica `PipelineResult(outputs, report, detection, validation)` como `@dataclass(frozen=True, slots=True)`; inmutabilidad; tipos correctos. Implementar en `result.py`. (Test e impl en la misma task por trivialidad.)

**Criterio de done:**
- [ ] Test verde
- [ ] `mypy --strict` pasa
- [ ] Docstring NumPy completo
- [ ] Exportado desde `__init__.py`

**Archivos:**
- `tests/unit/pipeline/test_result.py`
- `src/tempify/pipeline/result.py`

### task-1.9: Test e impl de `reproducibility_context`

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.1
**Bloqueada por:** task-1.7

**Descripción:** Context manager en `runtime.py` que aplica el scheduler de Dask y semilla NumPy conforme a `reproducibility_mode` (`strict` → `dask.config.set(scheduler="synchronous")`, `parallel` → respeta `scheduler`). Test verifica que al salir del contexto se restaura la config global previa de Dask.

**Criterio de done:**
- [ ] Test verde (entrada/salida del contexto preserva estado global de Dask)
- [ ] `mypy --strict` pasa
- [ ] Docstring NumPy con ejemplo de uso

**Archivos:**
- `tests/unit/pipeline/test_runtime.py`
- `src/tempify/pipeline/runtime.py`

## Fase 2: Implementación incremental del pipeline

### task-2.1: Scaffolding de `TempifyPipeline` + smoke test con mocks

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.2
**Bloqueada por:** task-1.7, task-1.8, task-1.9

**Descripción:** Crear `class TempifyPipeline` en `core.py` con `__init__(self, config: PipelineConfig)` y `run(self, source) -> PipelineResult` lanzando `NotImplementedError`. Smoke test con todas las capas inferiores mockeadas (Detection, Validation, Interpolation, I/O) que verifica instanciación y firma de `run()`. Cubre REQ-001 parcialmente.

**Criterio de done:**
- [ ] Smoke test verde
- [ ] `mypy --strict` pasa
- [ ] Fixture `mocked_pipeline_dependencies` definido en `tests/unit/pipeline/conftest.py`

**Archivos:**
- `src/tempify/pipeline/core.py`
- `tests/unit/pipeline/test_core_smoke.py`
- `tests/unit/pipeline/conftest.py`

### task-2.2: Test e impl de fase `detect`

**Tipo:** test+impl
**Estimación:** 3h
**Bloquea:** task-2.3
**Bloqueada por:** task-2.1

**Descripción:** Implementar `_detect` que invoca `StructureDetector` y `TemporalFrequencyResolver`. Test parametrizado sobre los tres modos de input (A: archivo único stack, B: directorio monocapa, C: lista explícita). Cubre REQ-001 (fase 1), REQ-002 (orden).

**Criterio de done:**
- [ ] Tests verdes para los 3 modos
- [ ] `_detect` no muta `source`
- [ ] Llamadas a `cb("detect", 0.0)` y `cb("detect", 1.0)` verificadas en test
- [ ] `mypy --strict` pasa

**Archivos:**
- `src/tempify/pipeline/core.py`
- `tests/unit/pipeline/test_phase_detect.py`

### task-2.3: Test e impl de fase 1b (ensamblaje de `time_axis`)

**Tipo:** test+impl
**Estimación:** 4h
**Bloquea:** task-2.4
**Bloqueada por:** task-2.2

**Descripción:** Implementar la fase 1b descrita en `design.md` §5: a partir de `detection.resolution_result.time_axis`, materializar `time_axis` final aplicando `monthly_anchor`. Si no hay fechas, caer a año proxy 2026 marcando `calendar_agnostic=True`. Persistir `time_axis_source` en `self._time_axis_source` para inyección posterior en el reporte. Tests cubren los 5 valores del literal (`cf-bounds`, `filename`, `band-descriptions`, `midpoint-proxy`, `user-custom`) y la verificación de longitud (`PIPELINE_CUSTOM_AXIS_LENGTH_MISMATCH`). Cubre ADR-0015, Decisión 8.

**Criterio de done:**
- [ ] `test_pipeline_propagates_time_axis_from_resolver` verde (3 sub-casos parametrizados)
- [ ] `test_pipeline_falls_back_to_proxy_year_when_no_dates` verde
- [ ] `test_pipeline_custom_monthly_anchor_requires_dates` (caso b: longitud mismatch) verde
- [ ] `mypy --strict` pasa

**Archivos:**
- `src/tempify/pipeline/core.py`
- `tests/unit/pipeline/test_phase_time_axis_assembly.py`

### task-2.4: Test e impl de fase `validate_geospatial` (condicional a `skip_pre_validation`)

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.5
**Bloqueada por:** task-2.3

**Descripción:** Implementar invocación de `GeospatialCoherenceValidator` con manejo de `GeospatialIncoherenceError` (fail-fast, envuelve en `PipelinePreValidationError` preservando `error_code`). Si `cfg.skip_pre_validation`, devolver `[]` y emitir progreso con mensaje `"omitida (inspect mode)"`. Cubre REQ-005, REQ-011 (parcial).

**Criterio de done:**
- [ ] `test_pipeline_fails_fast_on_geospatial_error` verde
- [ ] Test con `skip_pre_validation=True` que verifica skip + mensaje en callback
- [ ] `mypy --strict` pasa

**Archivos:**
- `src/tempify/pipeline/core.py`
- `tests/unit/pipeline/test_phase_validate_geospatial.py`

### task-2.5: Test e impl de fase `validate_compatibility`

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.6
**Bloqueada por:** task-2.4

**Descripción:** Invocar `MethodVariableCompatibilityChecker(method=cfg.method, force=cfg.force_method)`. Captura `MethodVariableIncompatibilityError` y envuelve en `PipelinePreValidationError`. Respeta `skip_pre_validation`. Cubre REQ-005.

**Criterio de done:**
- [ ] `test_pipeline_fails_fast_on_method_variable_incompat` verde
- [ ] Test que verifica `force_method=True` deshabilita el rechazo
- [ ] `mypy --strict` pasa

**Archivos:**
- `src/tempify/pipeline/core.py`
- `tests/unit/pipeline/test_phase_validate_compatibility.py`

### task-2.6: Test e impl de fase `interpolate` con dispatcher

**Tipo:** test+impl
**Estimación:** 4h
**Bloquea:** task-2.7
**Bloqueada por:** task-2.5

**Descripción:** Implementar `_select_interpolator(method, method_options)` (factory por método: `linear`, `pchip`, `pchip_mp`, `fourier`) e invocar `.interpolate()` propagando `target_axis` y `progress_hook` con throttling según `progress_frequency_hz`. Capturar excepciones y envolver en `PipelineInterpolationError`. No mutar input. Cubre REQ-008, parte de REQ-001.

**Criterio de done:**
- [ ] Test parametrizado sobre los 4 métodos, mockeados
- [ ] `test_pipeline_does_not_mutate_input_dataarray` verde
- [ ] `test_pipeline_preserves_lazy_evaluation` verde (verifica que el output sigue dask-backed)
- [ ] `mypy --strict` pasa

**Archivos:**
- `src/tempify/pipeline/core.py`
- `tests/unit/pipeline/test_phase_interpolate.py`

### task-2.7: Test e impl de fase `validate_post` (warn-and-continue)

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.8
**Bloqueada por:** task-2.6

**Descripción:** Invocar `PostInterpolationValidator(variable_profile=detection.variable_profile).validate(...)`. NUNCA aborta: las fallas se acumulan en `ValidationReport` como warnings. Cubre REQ-006.

**Criterio de done:**
- [ ] `test_pipeline_warns_and_continues_on_post_validation_failure` verde
- [ ] Verifica que `result.report.validation_post` contiene las fallas como warnings
- [ ] Verifica que `write` y `generate_report` se ejecutan posteriormente
- [ ] `mypy --strict` pasa

**Archivos:**
- `src/tempify/pipeline/core.py`
- `tests/unit/pipeline/test_phase_validate_post.py`

### task-2.8: Test e impl de fase `write` con dispatcher por formato

**Tipo:** test+impl
**Estimación:** 3h
**Bloquea:** task-2.9
**Bloqueada por:** task-2.7

**Descripción:** Implementar `_select_writer(output_format)` (factory para `netcdf`, `geotiff_collection`, `multiband_geotiff`, `zarr`). Captura excepciones y envuelve en `PipelineWriteError`. Cubre parte de REQ-001.

**Criterio de done:**
- [ ] Test parametrizado sobre los 4 formatos, writers mockeados
- [ ] Test que `PipelineWriteError` se levanta y `error_code="PIPELINE_WRITE_FAILED"`
- [ ] `mypy --strict` pasa

**Archivos:**
- `src/tempify/pipeline/core.py`
- `tests/unit/pipeline/test_phase_write.py`

### task-2.9: Test e impl de `ReportGenerator` (fase `generate_report`)

**Tipo:** test+impl
**Estimación:** 4h
**Bloquea:** task-2.10
**Bloqueada por:** task-2.8

**Descripción:** Implementar `ReportGenerator` conforme al schema `docs/schemas/processing-report.schema.md`. Computa MD5 streaming de inputs y outputs, serializa `config` (excluye callbacks, Path→str POSIX), inyecta `monthly_anchor` y `time_axis_source`, pobla `timestamp_utc` al final, excluido del MD5 (ADR-0007). Implementa `build()` y `to_markdown()`. Cubre REQ-007.

**Criterio de done:**
- [ ] `test_pipeline_report_contains_full_provenance` verde
- [ ] `test_pipeline_report_md5_excludes_timestamp` verde
- [ ] `test_processing_report_includes_time_axis_source` verde (los 5 valores)
- [ ] `mypy --strict` pasa
- [ ] Docstring NumPy completo

**Archivos:**
- `src/tempify/pipeline/report.py`
- `tests/unit/pipeline/test_report_generator.py`

### task-2.10: Test e impl del modo `dry_run`

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.11
**Bloqueada por:** task-2.9

**Descripción:** Implementar `_build_dry_run_result` que ejecuta solo `detect` + pre-validation + statistics + `generate_report` (con prefijo `[DRY_RUN]` en título y `tempify_version`). `outputs=[]`, `report.outputs=[]`. `inputs[i].md5` computado normalmente. Cubre REQ-011.

**Criterio de done:**
- [ ] `test_pipeline_dry_run_skips_interpolation_and_write` verde
- [ ] Verifica prefijo `[DRY_RUN]` en `to_markdown()`
- [ ] `mypy --strict` pasa

**Archivos:**
- `src/tempify/pipeline/core.py`
- `tests/unit/pipeline/test_dry_run.py`

### task-2.11: Test e impl de modo `inspect` (`skip_pre_validation`)

**Tipo:** test+impl
**Estimación:** 1.5h
**Bloquea:** task-2.12
**Bloqueada por:** task-2.10

**Descripción:** Ejercita el modo combinado `dry_run=True, skip_pre_validation=True`. Verifica que la fase `detect` se ejecuta, las dos fases de pre-validation se skipean limpiamente, y el reporte resultante tiene `validation_pre=[]`. También verifica la invariante de que `skip_pre_validation=True, dry_run=False` levanta `InvalidConfigError` en construcción del config. Cubre REQ-011 ampliado (design Decisión 7).

**Criterio de done:**
- [ ] `test_pipeline_inspect_mode_skips_pre_validation` verde (sobre fixture con CRS inconsistente)
- [ ] `test_pipeline_skip_pre_validation_without_dry_run_raises` verde
- [ ] `mypy --strict` pasa

**Archivos:**
- `tests/unit/pipeline/test_inspect_mode.py`

### task-2.12: Test e impl de reproducibilidad `strict` (bit-exact)

**Tipo:** test+impl
**Estimación:** 3h
**Bloquea:** task-2.13
**Bloqueada por:** task-2.11

**Descripción:** Ejecutar `run()` dos veces con `reproducibility_mode="strict"`, scheduler `synchronous`, mismos inputs y config, y comparar MD5 de outputs. El timestamp se excluye del MD5 del reporte. Cubre REQ-010, NFR-002.

**Criterio de done:**
- [ ] `test_pipeline_bit_exact_reproducibility` verde
- [ ] Fixture `synthetic_3x3_monthly.nc` consumido
- [ ] `mypy --strict` pasa

**Archivos:**
- `tests/integration/pipeline/test_reproducibility_strict.py`

### task-2.13: Test de reproducibilidad `parallel` (allclose)

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.14
**Bloqueada por:** task-2.12

**Descripción:** Ejecutar dos veces en modo `parallel`, scheduler `threaded`. Comparar con `xr.testing.assert_allclose(rtol=1e-12, atol=1e-15)` sobre los `DataArray` leídos desde outputs. Cubre NFR-002, ADR-0007.

**Criterio de done:**
- [ ] `test_pipeline_allclose_reproducibility_parallel` verde
- [ ] `mypy --strict` pasa

**Archivos:**
- `tests/integration/pipeline/test_reproducibility_parallel.py`

### task-2.14: Test e impl de `frequency_resolver_callback`

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.15
**Bloqueada por:** task-2.13

**Descripción:** El pipeline invoca `cfg.frequency_resolver_callback` cuando la Capa 2 no logra resolver frecuencia, propagando `ResolverEvidence`. Si el callback devuelve `None` o no se proporcionó, levanta `FrequencyResolutionError` envuelto en `PipelinePreValidationError`. Cubre REQ-012.

**Criterio de done:**
- [ ] `test_pipeline_invokes_frequency_resolver_callback` verde
- [ ] `test_pipeline_raises_when_callback_returns_none` verde
- [ ] Fixture `dummy_frequency_resolver` definido en `conftest.py`
- [ ] `mypy --strict` pasa

**Archivos:**
- `tests/unit/pipeline/test_frequency_resolver_callback.py`
- `tests/unit/pipeline/conftest.py`

### task-2.15: Tests de orden determinista y progreso por fase

**Tipo:** test
**Estimación:** 2h
**Bloquea:** task-2.16
**Bloqueada por:** task-2.14

**Descripción:** Tests que verifican (a) orden exacto de las 7 fases en `cb` invocations (REQ-002); (b) callback invocado al inicio y al fin de cada fase (REQ-003); (c) `progress` monotónicamente no decreciente por fase (property-based con hypothesis); (d) ejecución silenciosa sin callback (REQ-004); (e) frecuencia parametrizada 1/4/10 Hz (NFR-003).

**Criterio de done:**
- [ ] `test_pipeline_phase_order_is_deterministic` verde
- [ ] `test_pipeline_invokes_progress_callback_per_phase` verde
- [ ] `test_pipeline_runs_silently_without_callback` verde
- [ ] `test_pipeline_progress_callback_frequency` parametrizado en 1/4/10 Hz verde
- [ ] `test_progress_fraction_monotonic_per_phase` (hypothesis) verde
- [ ] Fixture `recording_progress_callback` definido

**Archivos:**
- `tests/unit/pipeline/test_progress_callback.py`
- `tests/unit/pipeline/test_phase_order.py`

### task-2.16: Tests de imports prohibidos

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-2.17
**Bloqueada por:** task-2.15

**Descripción:** Tres tests AST que recorren todos los `.py` bajo `src/tempify/pipeline/` y verifican que ningún archivo importa `typer`, `rich`, ni referencia `sys.stdin`. Cuarto test: tras `import tempify.pipeline`, `typer` y `rich` no aparecen en `sys.modules`. Quinto test: todos los loggers definidos están bajo `tempify.pipeline.*`. Cubre riesgo arquitectónico de design §2.

**Criterio de done:**
- [ ] `test_pipeline_no_typer_import` verde
- [ ] `test_pipeline_no_rich_import` verde
- [ ] `test_pipeline_no_sys_stdin_import` verde
- [ ] `test_pipeline_logger_namespace` verde

**Archivos:**
- `tests/unit/pipeline/test_forbidden_imports.py`

### task-2.17: Errores en español y catálogo `EXIT_CODES`

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-3.1
**Bloqueada por:** task-2.16

**Descripción:** Test que recorre todas las subclases de `TempifyPipelineError`, instancia cada una con `error_code` canónico, y verifica que `str(exc)` contiene texto en español (heurística: presencia de caracteres `áéíóúñ` o palabras clave en español); test de jerarquía completa con `__cause__` preservado; test que `EXIT_CODES` mapea cada subclase a un entero único. Cubre REQ-009, NFR-006.

**Criterio de done:**
- [ ] `test_pipeline_error_hierarchy_and_codes` verde
- [ ] `test_pipeline_error_messages_spanish` verde
- [ ] `test_pipeline_exit_codes_unique_and_covering` verde

**Archivos:**
- `tests/unit/pipeline/test_errors_es.py`

## Fase 3: Documentación e integración

### task-3.1: Docstrings NumPy en superficie pública

**Tipo:** docs
**Estimación:** 2h
**Bloquea:** task-3.2
**Bloqueada por:** task-2.17

**Descripción:** Completar docstrings NumPy en `TempifyPipeline`, `PipelineConfig`, `PipelineResult`, `ProcessingReport`, `ProgressCallback`, `FrequencyResolverProtocol`, `ReportGenerator`, y todas las excepciones. Verificar con `pydocstyle` o `ruff` configurado para enforcement.

**Criterio de done:**
- [ ] `ruff check --select D` pasa sobre `src/tempify/pipeline/`
- [ ] Cada función pública tiene secciones `Parameters`, `Returns`, `Raises`
- [ ] Ejemplos `Examples` en `TempifyPipeline.run` y `PipelineConfig`

**Archivos:**
- `src/tempify/pipeline/*.py`

### task-3.2: Test end-to-end con fixture pequeño

**Tipo:** test
**Estimación:** 3h
**Bloquea:** task-3.3
**Bloqueada por:** task-3.1

**Descripción:** Test integración real (sin mocks) sobre `synthetic_3x3_monthly.nc`: ejecuta `TempifyPipeline(config).run(source)` con `method="pchip_mp"`, `target_freq="daily"`, `output_format="netcdf"`. Verifica `len(result.outputs) == 1`, `result.report.tempify_version` poblado, `result.report.outputs[0].md5` no vacío, `result.detection.frequency == "monthly"`, conservación de media mensual dentro de tolerancia (delegado a Validation post).

**Criterio de done:**
- [ ] Test verde sin mocks
- [ ] Tiempo total <30s

**Archivos:**
- `tests/integration/pipeline/test_end_to_end_synthetic.py`

### task-3.3: Benchmark NFR-001 (overhead <5%)

**Tipo:** test
**Estimación:** 3h
**Bloquea:** task-3.4
**Bloqueada por:** task-3.2

**Descripción:** Benchmark `pytest-benchmark` que mide `TempifyPipeline.run()` vs `PchipMeanPreservingInterpolator.interpolate()` directo sobre fixture WorldClim Chile 2.5min, 12 meses. Falla si overhead >5%. Cachea el fixture en `tests/benchmark/cache/`.

**Criterio de done:**
- [ ] Benchmark ejecuta en CI con `--benchmark-only`
- [ ] Asserción `overhead_ratio < 0.05`
- [ ] Reporte de benchmark publicado como artifact

**Archivos:**
- `tests/benchmark/test_pipeline_overhead.py`

### task-3.4: Profiling NFR-004 (memoria <2× stack)

**Tipo:** test
**Estimación:** 3h
**Bloquea:** task-3.5
**Bloqueada por:** task-3.3

**Descripción:** Test con `memray` que mide pico de memoria sobre stack 12×3000×500 durante `run()`. Falla si pico > 2× tamaño en bytes de un único stack. Verifica preservación de pereza de Dask (REQ-008, NFR-004).

**Criterio de done:**
- [ ] `test_pipeline_memory_peak` verde
- [ ] Reporte memray publicado como artifact
- [ ] Conditional skip si memray no disponible en plataforma

**Archivos:**
- `tests/benchmark/test_pipeline_memory_peak.py`

### task-3.5: Validación de schema JSON del reporte

**Tipo:** test
**Estimación:** 2h
**Bloquea:** task-3.6
**Bloqueada por:** task-3.4

**Descripción:** Test que parsea el bloque YAML de procedencia del Markdown emitido por `ReportGenerator.to_markdown()` y lo valida con `jsonschema` contra una representación JSON-Schema generada desde `docs/schemas/processing-report.schema.md` (script auxiliar en `tests/schemas/build_schema.py`). Cubre REQ-007 + design §7 schema tests.

**Criterio de done:**
- [ ] `test_report_yaml_block_validates_against_schema` verde
- [ ] Script de build del JSON-Schema commiteado
- [ ] `tests/schemas/processing-report.schema.json` generado

**Archivos:**
- `tests/schemas/test_report_schema_validation.py`
- `tests/schemas/build_schema.py`
- `tests/schemas/processing-report.schema.json`

### task-3.6: CHANGELOG + impl-log

**Tipo:** docs
**Estimación:** 1h
**Bloquea:** —
**Bloqueada por:** task-3.5

**Descripción:** Añadir entrada `## [unreleased] — pipeline layer` en `CHANGELOG.md` describiendo: nueva capa 5, `TempifyPipeline`, soporte `dry_run`/`inspect`, reproducibilidad `strict`/`parallel`, ensamblaje de `time_axis` end-to-end. Cerrar `specs/pipeline/impl-log.md` con resumen cronológico y referencias a commits.

**Criterio de done:**
- [ ] `CHANGELOG.md` actualizado
- [ ] `specs/pipeline/impl-log.md` con cronología completa
- [ ] Spec marcada como `Complete` en su header

**Archivos:**
- `CHANGELOG.md`
- `specs/pipeline/impl-log.md`
- `specs/pipeline/requirements.md` (header solo)
- `specs/pipeline/design.md` (header solo)

## Resumen

| Fase | # tasks | Estimación total |
|---|---|---|
| Fase 1 | 9 | 16h |
| Fase 2 | 17 | 41h |
| Fase 3 | 6 | 14h |
| **Total** | **32** | **71h** |
