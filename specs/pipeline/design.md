# Design — pipeline

**Estado:** Draft
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-16

## 1. Visión técnica

El módulo `tempify.pipeline` materializa la Capa 5 de la arquitectura: la única capa que conoce a todas las inferiores (detection, validation, interpolation, I/O) y coordina su ejecución end-to-end. No contiene lógica de negocio; orquesta, registra procedencia y emite un `ProcessingReport` reproducible.

Su diseño se rige por cuatro principios duros: (i) inmutabilidad de la configuración (`PipelineConfig` es un `@dataclass(frozen=True, slots=True)`); (ii) preservación de la pereza de Dask hasta el writer (REQ-008, NFR-004); (iii) reproducibilidad bit-exact controlada por modo (ADR-0007); (iv) aislamiento absoluto frente a capas superiores: el pipeline no importa `typer`, `rich`, `sys.stdin`, ni ningún módulo de presentación. Ese aislamiento se enforza con tests de imports prohibidos (REQ-001..009 del riesgo "acoplamiento accidental con CLI").

La orquestación es lineal y determinista: siete fases canónicas en el orden fijado por REQ-001/REQ-002, con un único callback de progreso (`ProgressCallback`) opcional que recibe el nombre de fase como `Literal` cerrado. El reporte se construye al final con `ReportGenerator`, consume el schema canónico `docs/schemas/processing-report.schema.md` y excluye el timestamp del cómputo MD5 conforme a ADR-0007.

## 2. Arquitectura propuesta

### Diagrama de componentes

```
                  ┌──────────────────────────────────┐
                  │  Cliente (CLI / GUI / script)    │
                  │  construye PipelineConfig        │
                  └────────────────┬─────────────────┘
                                   │ run(source)
                                   ▼
                  ┌──────────────────────────────────┐
                  │  TempifyPipeline.run()           │
                  │  ─ 7 fases canónicas             │
                  │  ─ emite ProgressCallback        │
                  │  ─ envuelve excepciones          │
                  └──┬───────────────────────────────┘
                     │
   ┌─────────────────┼──────────────────────────────────────────┐
   │                 │                                          │
   ▼                 ▼                                          ▼
┌──────────┐  ┌──────────────┐  ┌────────────┐  ┌──────────┐  ┌──────────────────┐
│Detection │→ │ pre-Validation│→│Interpolation│→│ post-Val │→│ I/O Writer       │
│ Layer    │  │ (geo + compat)│  │  Layer     │  │  Layer   │  │  + ReportGenerator│
└──────────┘  └──────────────┘  └────────────┘  └──────────┘  └──────────────────┘
                                                                       │
                                                                       ▼
                                                            PipelineResult
                                                            (outputs, report,
                                                             detection, validation)
```

### Componentes nuevos

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| `TempifyPipeline` | `src/tempify/pipeline/core.py` | Clase orquestadora; método `run()`. |
| `PipelineConfig` | `src/tempify/pipeline/config.py` | Dataclass frozen con todos los parámetros de ejecución. |
| `PipelineResult` | `src/tempify/pipeline/result.py` | Dataclass de retorno (`outputs`, `report`, `detection`, `validation`). |
| `ProgressCallback` | `src/tempify/pipeline/callbacks.py` | `Protocol` con `Literal` cerrado de 7 fases. |
| `FrequencyResolverProtocol` | `src/tempify/pipeline/callbacks.py` | `Protocol` para resolución interactiva de frecuencia. |
| `ReportGenerator` | `src/tempify/pipeline/report.py` | Construcción del `ProcessingReport` conforme al schema. |
| `TempifyPipelineError` y subclases | `src/tempify/pipeline/errors.py` | Jerarquía única de excepciones tipadas. |
| `reproducibility_context` | `src/tempify/pipeline/runtime.py` | Context manager que aplica el scheduler de Dask por modo. |

### Componentes modificados

Ninguno: las capas 1-4 ya exponen sus contratos. El pipeline solo los consume.

## 3. Contratos públicos (APIs)

### `TempifyPipeline`

```python
class TempifyPipeline:
    """Orquestador end-to-end de la Capa 5 (ver ADR-0014)."""

    def __init__(self, config: PipelineConfig) -> None: ...

    def run(self, source: Path | list[Path]) -> PipelineResult:
        """Ejecuta las siete fases canónicas en orden fijo.

        Parameters
        ----------
        source : Path | list[Path]
            Ruta única (modo A o B con directorio) o lista explícita (modo C).

        Returns
        -------
        PipelineResult
            outputs, report, detection, validation.

        Raises
        ------
        PipelinePreValidationError
            Validación geoespacial o de compatibilidad método/variable falla.
        PipelineInterpolationError
            Falla durante la fase de interpolación.
        PipelineWriteError
            Falla durante la escritura.
        PipelineReportError
            Falla durante la generación del reporte.
        TempifyPipelineError
            Cualquier otra falla orquestada (incluye `FrequencyResolutionError`
            no resuelto por callback).
        """
```

**Pre-condiciones:**
- `source` existe en el sistema de archivos.
- Las capas inferiores cumplen sus contratos publicados.

**Post-condiciones:**
- En éxito normal: `len(result.outputs) >= 1`; cada archivo tiene MD5 reportado.
- En `dry_run=True`: `result.outputs == []`; `result.report.outputs == []`; resto del reporte poblado.
- El `xr.DataArray` original del reader no fue mutado ni eagerly evaluado salvo si el writer lo exigió (REQ-008).
- En modo `strict`: dos ejecuciones independientes en la misma plataforma producen MD5 idéntico de outputs.

**Excepciones lanzadas:** ver above. Toda excepción originada en capas inferiores se envuelve con `raise PipelinePreValidationError(...) from e` (o la subclase correspondiente), preservando el `error_code` original en `__cause__` y exponiéndolo como atributo público.

### `PipelineConfig`

```python
@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Configuración inmutable de una ejecución del pipeline."""

    method: Literal["linear", "pchip", "pchip_mp", "fourier"]
    target_freq: Literal["daily"]
    output_dir: Path
    output_format: Literal["netcdf", "geotiff_collection", "multiband_geotiff", "zarr"] = "netcdf"
    chunk_size: int = 512
    scheduler: Literal["threaded", "synchronous"] = "threaded"
    reproducibility_mode: Literal["strict", "parallel"] = "parallel"
    progress_callback: ProgressCallback | None = None
    progress_frequency_hz: float = 4.0
    frequency_resolver_callback: FrequencyResolverProtocol | None = None
    dry_run: bool = False
    force_method: bool = False
    variable_profile_override: str | None = None
    seed: int = 42
    method_options: Mapping[str, Any] = field(default_factory=dict)
```

**Invariantes verificadas en `__post_init__`:**
- `output_dir` es absoluto o resoluble; si no existe, se intenta crear (no en `dry_run`).
- Si `reproducibility_mode == "strict"`, `scheduler` se fuerza a `"synchronous"` (warning si el usuario pasó `"threaded"` explícito).
- `progress_frequency_hz > 0`.
- `method_options` se congela mediante `MappingProxyType` para preservar la inmutabilidad del dataclass.

### `PipelineResult`

```python
@dataclass(frozen=True, slots=True)
class PipelineResult:
    outputs: list[Path]
    report: ProcessingReport
    detection: DetectionResult
    validation: ValidationReport
```

### `ProgressCallback`

```python
from typing import Protocol, Literal

PipelinePhase = Literal[
    "detect",
    "validate_geospatial",
    "validate_compatibility",
    "interpolate",
    "validate_post",
    "write",
    "generate_report",
]

class ProgressCallback(Protocol):
    def __call__(
        self,
        phase: PipelinePhase,
        progress: float,  # [0.0, 1.0]
        message: str | None = None,
    ) -> None: ...
```

### `FrequencyResolverProtocol`

```python
class FrequencyResolverProtocol(Protocol):
    """Callback que el pipeline invoca cuando la Capa 2 no resuelve frecuencia.

    Devuelve una frecuencia válida (string canónico CF: 'monthly', 'weekly',
    'daily', etc.) o `None` para indicar abandono.
    """

    def __call__(
        self,
        evidence: ResolverEvidence,
    ) -> str | None: ...
```

`ResolverEvidence` es el dataclass que la Capa 2 ya expone (ver `specs/temporal-frequency-resolver/requirements.md` REQ-007); el pipeline lo propaga sin transformarlo.

### `ReportGenerator`

```python
class ReportGenerator:
    """Construye el ProcessingReport conforme al schema canónico."""

    def __init__(
        self,
        config: PipelineConfig,
        detection: DetectionResult,
        validation: ValidationReport,
        inputs: list[Path],
        outputs: list[Path],
        rymes_myers_iterations: int | None = None,
        dry_run: bool = False,
    ) -> None: ...

    def build(self) -> ProcessingReport: ...
    def to_markdown(self) -> str: ...
```

**Post-condición clave:** el campo `timestamp_utc` se rellena al final, y el cómputo MD5 de outputs ya está congelado antes de poblarlo (ADR-0007).

### `TempifyPipelineError` y subclases

```python
class TempifyPipelineError(Exception):
    """Base de la jerarquía de errores del pipeline."""
    error_code: str  # identificador en inglés, e.g. "PIPELINE_PRE_VALIDATION_FAILED"
    def __init__(self, message: str, *, error_code: str, cause: Exception | None = None) -> None: ...

class PipelinePreValidationError(TempifyPipelineError): ...
class PipelineInterpolationError(TempifyPipelineError): ...
class PipelineWriteError(TempifyPipelineError): ...
class PipelineReportError(TempifyPipelineError): ...
```

Mensajes humanos en español; identificadores `error_code` en inglés (REQ-009, NFR-006).

## 4. Modelos de datos

### `ProcessingReport`

```python
@dataclass(frozen=True, slots=True)
class ProcessingReport:
    tempify_version: str
    timestamp_utc: str  # ISO-8601, excluido del MD5
    platform: str
    python_version: str
    reproducibility_mode: Literal["strict", "parallel"]
    dask_scheduler: Literal["threaded", "synchronous"]
    config: Mapping[str, Any]
    inputs: list[FileFingerprint]
    outputs: list[FileFingerprint]
    detection_confidence: Mapping[str, float]  # TypedDict de ADR-0008
    validation_pre: list[ValidationCheck]
    validation_post: list[ValidationCheck]
    statistics_pre: Mapping[str, BandStats]
    statistics_post: Mapping[str, BandStats]
    warnings: list[str]
    errors: list[str]
    rymes_myers_iterations: int | None
    dry_run: bool

@dataclass(frozen=True, slots=True)
class FileFingerprint:
    path: Path
    md5: str
    bytes: int
    format: str
```

### Stamping de procedencia

Los `attrs` del `xr.DataArray` de salida llevan (ADR-0007):
- `reproducibility_mode`, `tempify_version`, `md5_inputs`, `md5_outputs`, `scheduler`, `platform`.

## 5. Algoritmos clave

### Orquestación de `run()` (siete fases canónicas)

Pseudocódigo de referencia. Cada fase emite progreso al entrar y al salir; la interpolación emite además progreso intermedio según `progress_frequency_hz`.

```python
def run(self, source: Path | list[Path]) -> PipelineResult:
    cfg = self._config
    cb = cfg.progress_callback or _noop
    log = logging.getLogger("tempify.pipeline.core")

    inputs = _normalize_source(source)

    with reproducibility_context(cfg.reproducibility_mode, cfg.scheduler, cfg.seed):
        # 1. detect
        cb("detect", 0.0)
        try:
            detection = self._detect(inputs)  # may invoke frequency_resolver_callback
        except FrequencyResolutionError as e:
            raise PipelinePreValidationError(
                _msg_es("PIPELINE_FREQUENCY_UNRESOLVED", e),
                error_code="PIPELINE_FREQUENCY_UNRESOLVED",
            ) from e
        cb("detect", 1.0)

        # 2. validate_geospatial
        cb("validate_geospatial", 0.0)
        try:
            geo_checks = GeospatialCoherenceValidator().validate(detection)
        except GeospatialIncoherenceError as e:
            raise PipelinePreValidationError(
                _msg_es("PIPELINE_GEOSPATIAL_INCOHERENT", e),
                error_code=e.error_code,
            ) from e
        cb("validate_geospatial", 1.0)

        # 3. validate_compatibility
        cb("validate_compatibility", 0.0)
        try:
            compat_checks = MethodVariableCompatibilityChecker(
                method=cfg.method, force=cfg.force_method
            ).check(detection.variable_profile)
        except MethodVariableIncompatibilityError as e:
            raise PipelinePreValidationError(
                _msg_es("PIPELINE_METHOD_VARIABLE_INCOMPATIBLE", e),
                error_code=e.error_code,
            ) from e
        cb("validate_compatibility", 1.0)

        # Statistics pre (computadas lazy)
        stats_pre = StatisticalReporter().describe(detection.dataarray)

        if cfg.dry_run:
            return self._build_dry_run_result(
                detection, geo_checks, compat_checks, stats_pre, inputs
            )

        # 4. interpolate (lazy; preserva Dask)
        cb("interpolate", 0.0)
        try:
            interpolator = _select_interpolator(cfg.method, cfg.method_options)
            result_array, rm_iterations = interpolator.interpolate(
                detection.dataarray,
                target_axis=_target_axis(detection, cfg.target_freq),
                progress_hook=_make_throttled_hook(cb, cfg.progress_frequency_hz),
            )
        except Exception as e:
            raise PipelineInterpolationError(
                _msg_es("PIPELINE_INTERPOLATION_FAILED", e),
                error_code="PIPELINE_INTERPOLATION_FAILED",
            ) from e
        cb("interpolate", 1.0)

        # 5. validate_post (warn-and-continue, REQ-006)
        cb("validate_post", 0.0)
        post_checks = PostInterpolationValidator(
            variable_profile=detection.variable_profile
        ).validate(detection.dataarray, result_array)
        stats_post = StatisticalReporter().describe(result_array)
        cb("validate_post", 1.0)

        # 6. write
        cb("write", 0.0)
        try:
            writer = _select_writer(cfg.output_format)
            outputs = writer.write(result_array, cfg.output_dir)
        except Exception as e:
            raise PipelineWriteError(
                _msg_es("PIPELINE_WRITE_FAILED", e),
                error_code="PIPELINE_WRITE_FAILED",
            ) from e
        cb("write", 1.0)

        # 7. generate_report
        cb("generate_report", 0.0)
        try:
            report = ReportGenerator(
                config=cfg,
                detection=detection,
                validation=ValidationReport(
                    checks=geo_checks + compat_checks + post_checks,
                    statistics={"pre": stats_pre, "post": stats_post},
                ),
                inputs=inputs,
                outputs=outputs,
                rymes_myers_iterations=rm_iterations,
                dry_run=False,
            ).build()
        except Exception as e:
            raise PipelineReportError(
                _msg_es("PIPELINE_REPORT_FAILED", e),
                error_code="PIPELINE_REPORT_FAILED",
            ) from e
        cb("generate_report", 1.0)

    return PipelineResult(
        outputs=outputs,
        report=report,
        detection=detection,
        validation=ValidationReport(...),
    )
```

**Complejidad:** O(orquestación) constante por fase; el coste real lo domina la interpolación (capa 4). El overhead total del pipeline está acotado por NFR-001 a < 5 %.

**Trade-offs considerados:**
- Una alternativa era ejecutar `validate_geospatial` y `validate_compatibility` en paralelo: rechazada porque viola REQ-002 (orden determinista) y el ahorro es marginal (ambas son sub-segundo).
- Otra alternativa era poblar `timestamp_utc` antes de los hashes: rechazada por ADR-0007 (el timestamp debe quedar fuera del cómputo MD5; se rellena al final como campo aislado).

### Modo `dry_run`

```python
def _build_dry_run_result(self, detection, geo_checks, compat_checks, stats_pre, inputs):
    report = ReportGenerator(
        config=self._config,
        detection=detection,
        validation=ValidationReport(
            checks=geo_checks + compat_checks,
            statistics={"pre": stats_pre, "post": {}},
        ),
        inputs=inputs,
        outputs=[],
        rymes_myers_iterations=None,
        dry_run=True,
    ).build()
    # ReportGenerator antepone "[DRY_RUN]" al título del reporte y al campo
    # `tempify_version` en el bloque de procedencia para señalización clara.
    return PipelineResult(outputs=[], report=report, detection=detection, validation=...)
```

`inputs[i].md5` se computa normalmente (REQ-011). Se omiten las fases `interpolate`, `validate_post` y `write`.

### Construcción del `ProcessingReport`

`ReportGenerator.build()`:

1. Computa `md5_inputs` para cada archivo (streaming hashlib).
2. Computa `md5_outputs` para cada output ya escrito (streaming hashlib sobre bytes en disco).
3. Serializa `config` excluyendo callbacks (no son hash-estables) y sustituye `Path` por `str` POSIX.
4. Resuelve `detection_confidence` desde `detection.confidence` (TypedDict ADR-0008).
5. Construye `warnings` y `errors` a partir de `validation.checks` (FAIL → error, WARN → warning).
6. Establece `timestamp_utc = datetime.now(tz=UTC).isoformat()` **al final**, después de que cualquier hash haya quedado congelado.

## 6. Decisiones de diseño

### Decisión 1: Naming `TempifyPipeline`

PascalCase per PEP 8. Registrada en ADR-0014. El módulo (`tempify.pipeline`) permanece lowercase.

### Decisión 2: `frequency_resolver_callback` como campo de `PipelineConfig`

Opciones consideradas:
1. Parámetro de `run()`. Rechazada: contamina la firma del entry point y rompe la simetría con los demás callbacks.
2. Setter mutable en `TempifyPipeline`. Rechazada: viola la inmutabilidad de la configuración.
3. **Campo de `PipelineConfig`** (elegida). Centraliza toda la configuración de ejecución en un objeto inmutable, alineado con ADR-0010 sobre el contrato Pipeline ↔ CLI/GUI.

### Decisión 3: El pipeline NO importa `typer`, `rich` ni `sys.stdin`

Regla arquitectónica dura #1. Enforzada por test de imports prohibidos (`test_pipeline_no_typer_import`, `test_pipeline_no_rich_import`, `test_pipeline_no_sys_stdin`). Cualquier interacción humana viaja exclusivamente por `progress_callback` y `frequency_resolver_callback`.

### Decisión 4: Logging namespace canónico

Todos los loggers del módulo viven bajo `tempify.pipeline.*` (e.g. `tempify.pipeline.core`, `tempify.pipeline.report`, `tempify.pipeline.runtime`). El cliente configura el nivel desde fuera; el pipeline nunca llama a `basicConfig`.

### Decisión 5: Excepciones envueltas con `raise ... from e`

Preserva el traceback original y el `error_code` de la capa inferior (REQ-009). El consumidor accede a `e.__cause__.error_code` si necesita el código original; `error_code` en la excepción wrapper queda en el namespace `PIPELINE_*` para facilitar matching.

### Decisión 6: Exclusión del timestamp del MD5 del reporte

Per ADR-0007. El campo `timestamp_utc` se inyecta al final de `build()`, después de congelar los hashes; tests de reproducibilidad comparan MD5 ignorando ese campo.

## 7. Estrategia de testing

### Tests unitarios y de integración (uno por REQ)

| Test | REQ cubierto |
|---|---|
| `test_pipeline_run_returns_pipeline_result` | REQ-001 |
| `test_pipeline_phase_order_is_deterministic` | REQ-002 |
| `test_pipeline_invokes_progress_callback_per_phase` | REQ-003 |
| `test_pipeline_progress_callback_frequency` (parametrizado 1/4/10 Hz) | REQ-003, NFR-003 |
| `test_pipeline_runs_silently_without_callback` | REQ-004 |
| `test_pipeline_fails_fast_on_geospatial_error` | REQ-005 |
| `test_pipeline_fails_fast_on_method_variable_incompat` | REQ-005 |
| `test_pipeline_warns_and_continues_on_post_validation_failure` | REQ-006 |
| `test_pipeline_report_contains_full_provenance` | REQ-007 |
| `test_pipeline_report_md5_excludes_timestamp` | REQ-007, ADR-0007 |
| `test_pipeline_does_not_mutate_input_dataarray` | REQ-008 |
| `test_pipeline_preserves_lazy_evaluation` | REQ-008, NFR-004 |
| `test_pipeline_error_hierarchy_and_codes` | REQ-009 |
| `test_pipeline_error_messages_spanish` | REQ-009, NFR-006 |
| `test_pipeline_bit_exact_reproducibility` (strict mode) | REQ-010, NFR-002 |
| `test_pipeline_dry_run_skips_interpolation_and_write` | REQ-011 |
| `test_pipeline_invokes_frequency_resolver_callback` | REQ-012 |
| `test_pipeline_raises_when_callback_returns_none` | REQ-012 |

### Tests de imports prohibidos

| Test | Verifica |
|---|---|
| `test_pipeline_no_typer_import` | `typer` no aparece en `sys.modules` tras `import tempify.pipeline`. |
| `test_pipeline_no_rich_import` | `rich` no aparece tras importar el módulo. |
| `test_pipeline_no_sys_stdin` | Análisis AST: ningún archivo bajo `src/tempify/pipeline/` referencia `sys.stdin`. |
| `test_pipeline_logger_namespace` | Todos los loggers definidos están bajo `tempify.pipeline.*`. |

### Tests property-based (hypothesis)

- `test_progress_fraction_monotonic_per_phase` — propiedad: `progress` emitido es monótono no decreciente dentro de cada fase.
- `test_md5_stability_under_config_reordering` — propiedad: serialización del config produce el mismo hash sin importar el orden interno de `method_options` (`sorted` keys).

### Tests de schema (jsonschema)

- `test_report_yaml_block_validates_against_schema` — parsea el bloque YAML de procedencia del Markdown emitido por `ReportGenerator.to_markdown()` y lo valida contra `docs/schemas/processing-report.schema.md` (representación JSON-Schema generada en `tests/schemas/processing-report.schema.json`).

### Benchmark

- `tests/benchmark/test_pipeline_overhead.py` — compara `TempifyPipeline.run()` con `PchipMeanPreservingInterpolator.interpolate()` directo sobre WorldClim Chile 2.5 min, 12 meses. Falla si overhead > 5 % (NFR-001).
- `tests/benchmark/test_pipeline_memory_peak.py` — memray sobre stack 12×3000×500; falla si pico > 2× tamaño de un único stack (NFR-004).

### Fixtures necesarios

- `synthetic_3x3_monthly.nc` — ya existe; usado para tests rápidos.
- `worldclim_chile_25min.tif` — benchmark canónico (descargado por `conftest.py` y cacheado).
- `recording_progress_callback` — fixture nuevo: callback que registra todas las llamadas para inspección posterior.
- `dummy_frequency_resolver` — fixture nuevo: callback configurable que devuelve frecuencia fija o `None`.

## 8. Plan de migración

No aplica: módulo nuevo, sin código previo en producción.

## 9. Métricas de calidad

| Métrica | Umbral |
|---|---|
| Coverage del módulo `tempify.pipeline` | ≥ 85 % (NFR-005) |
| Overhead pipeline vs. interpolación directa | < 5 % (NFR-001) |
| Memoria peak benchmark canónico | < 2× tamaño de stack único (NFR-004) |
| MD5 de outputs idempotente en `strict` | 100 % de runs (NFR-002) |
| Mensajes de error en español con código | 100 % de subclases de `TempifyPipelineError` (NFR-006) |

## 10. Trazabilidad requirements → componente → test

| Requirement | Componente | Test |
|---|---|---|
| REQ-001 | `TempifyPipeline.run` | `test_pipeline_run_returns_pipeline_result` |
| REQ-002 | `TempifyPipeline.run` (orquestación) | `test_pipeline_phase_order_is_deterministic` |
| REQ-003 | `TempifyPipeline._emit_progress` + `ProgressCallback` | `test_pipeline_invokes_progress_callback_per_phase`, `test_pipeline_progress_callback_frequency` |
| REQ-004 | `TempifyPipeline.run` (default `_noop` callback) | `test_pipeline_runs_silently_without_callback` |
| REQ-005 | `TempifyPipeline._validate_geospatial`, `_validate_compatibility`, wrappers de error | `test_pipeline_fails_fast_on_geospatial_error`, `test_pipeline_fails_fast_on_method_variable_incompat` |
| REQ-006 | `TempifyPipeline._validate_post` + `ValidationReport` | `test_pipeline_warns_and_continues_on_post_validation_failure` |
| REQ-007 | `ReportGenerator.build` | `test_pipeline_report_contains_full_provenance`, `test_pipeline_report_md5_excludes_timestamp` |
| REQ-008 | `TempifyPipeline.run` (no mutación) | `test_pipeline_does_not_mutate_input_dataarray`, `test_pipeline_preserves_lazy_evaluation` |
| REQ-009 | `tempify.pipeline.errors.*` | `test_pipeline_error_hierarchy_and_codes`, `test_pipeline_error_messages_spanish` |
| REQ-010 | `reproducibility_context` + `ReportGenerator` | `test_pipeline_bit_exact_reproducibility` |
| REQ-011 | `TempifyPipeline._build_dry_run_result` | `test_pipeline_dry_run_skips_interpolation_and_write` |
| REQ-012 | `TempifyPipeline._detect` + `FrequencyResolverProtocol` | `test_pipeline_invokes_frequency_resolver_callback`, `test_pipeline_raises_when_callback_returns_none` |
| NFR-001 | Benchmark | `tests/benchmark/test_pipeline_overhead.py` |
| NFR-002 | `reproducibility_context` | `test_pipeline_bit_exact_reproducibility` |
| NFR-003 | `_make_throttled_hook` | `test_pipeline_progress_callback_frequency` |
| NFR-004 | Preservación de pereza Dask | `test_pipeline_preserves_lazy_evaluation`, `test_pipeline_memory_peak` |
| NFR-005 | Cobertura general | CI: `pytest --cov=tempify.pipeline --cov-fail-under=85` |
| NFR-006 | `tempify.pipeline.errors.*` | `test_pipeline_error_messages_spanish` |

## 11. Referencias

- ADR-0007 — Política de reproducibilidad (modos `strict` / `parallel`, exclusión del timestamp del MD5).
- ADR-0008 — Confidence scoring and `DetectionResult` contract (shape del dict consumido por REQ-007).
- ADR-0010 — Política unificada de tolerancia para conservación de la media mensual.
- ADR-0014 — Corrección de naming `TempifyPipeline` (PascalCase).
- `docs/schemas/processing-report.schema.md` — schema canónico del reporte.
- `steering/architecture.md` § Capa 5 y reglas arquitectónicas duras.
- Specs vecinas consumidas (todas Approved/Draft): `core-interpolation`, `io-handlers`, `validation`, `structure-detection`, `temporal-frequency-resolver`, `cli`.
- PEP 589 (TypedDict): https://peps.python.org/pep-0589/
- PEP 8 (Naming): https://peps.python.org/pep-0008/#naming-conventions
