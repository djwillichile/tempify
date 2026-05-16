# Requirements — pipeline

**Estado:** Draft
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-16
**Última actualización:** 2026-05-16

## 1. Propósito

Definir la capa de orquestación end-to-end de tempify (`tempify.pipeline`): la única capa que conoce a todas las demás y coordina la secuencia `detect → validate_geospatial → validate_compatibility → interpolate → validate_post → write → generate_report`. Su responsabilidad es exclusivamente orquestar y producir un reporte de procesamiento con procedencia completa, sin contener lógica de negocio de las capas inferiores (detection, validation, interpolation, I/O).

## 2. Alcance

### In-scope

- Clase `TempifyPipeline` (PascalCase, conforme a PEP 8 y ADR-0014; el módulo `tempify.pipeline` permanece en lowercase) con método `run(source) -> PipelineResult` (ver Capa 5 en `../../steering/architecture.md`).
- Dataclass `PipelineConfig` (inmutable) que congela todos los parámetros de una ejecución (método, frecuencia destino, opciones de validación, rutas de salida, tolerancias, formato de escritura, semilla, callback de progreso).
- Dataclass `PipelineResult` que expone `outputs: list[Path]`, `report: ProcessingReport`, `detection: DetectionResult`, `validation: ValidationReport`.
- `ReportGenerator` que materializa el reporte de procesamiento en Markdown (formato canónico) con metadata de procedencia: versión de tempify, método e hiperparámetros, timestamp ISO-8601 UTC, hash MD5 de archivos de input y output, hash de configuración, número de iteraciones de Rymes-Myers si aplica.
- Jerarquía de excepciones bajo `TempifyPipelineError` con código de error referenciable en español (mensajes en español, identificadores en inglés).
- Protocol explícito `ProgressCallback` para reporte de progreso por fase y por porcentaje de píxeles.
- Política de manejo de errores por capa: fail-fast en validación pre-proceso, warn-and-continue en validación post-proceso.
- Invariante de no mutación: el `xr.DataArray` recibido del reader no se modifica in-place; toda transformación genera un nuevo array.
- Orden de operaciones determinista y documentado.

### Out-of-scope

- Lógica interna de detección, validación, interpolación o I/O (cada una vive en su propia capa; ver specs vecinas).
- Paralelización a nivel proceso (Dask es interno a la capa de interpolación, ver `../core-interpolation/requirements.md` REQ-010).
- Construcción de la CLI o GUI (la CLI consume el pipeline; ver `../cli/requirements.md`).
- Parsing de argumentos de línea de comandos.
- Selección automática del método (es responsabilidad del usuario o de la CLI con defaults del perfil de variable).

## 3. Actores y casos de uso

### Actor 1: Investigador con script Python

> Como investigador, quiero invocar `TempifyPipeline(config).run(source)` desde un notebook para obtener un `PipelineResult` con outputs persistidos y un reporte completo, sin escribir orquestación a mano.

**Caso de uso típico:** El investigador construye un `PipelineConfig(method="pchip_mp", target_freq="daily", output_dir=Path("out/"), output_format="netcdf")`, llama `run(Path("worldclim_chile/"))`, y recibe un `PipelineResult` cuyo `report` puede imprimir o guardar.

### Actor 2: CLI (cliente programático)

> Como CLI, quiero traducir las flags `tempify convert ...` a un `PipelineConfig` y delegar enteramente la ejecución al pipeline, para no duplicar lógica de negocio.

**Caso de uso típico:** El comando `tempify convert ./worldclim_chile/ --method pchip_mp --output ./out.nc --report report.md` (ver `../cli/requirements.md` REQ-001, REQ-005) construye el `PipelineConfig`, llama `pipeline.run(source)`, formatea el reporte con `rich` y lo escribe a disco si se pidió.

### Actor 3: GUI / orquestador externo (cliente programático futuro)

> Como GUI, quiero suscribirme a un callback de progreso por fase y por porcentaje para actualizar una barra de progreso y un panel de estado sin acoplarme a la implementación interna del pipeline.

**Caso de uso típico:** La GUI registra un `ProgressCallback` en el `PipelineConfig`. El pipeline lo invoca al entrar en cada fase (`"detect"`, `"validate_geospatial"`, `"validate_compatibility"`, `"interpolate"`, `"validate_post"`, `"write"`, `"report"`) y periódicamente durante la interpolación con el porcentaje de píxeles procesados.

## 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL expose `TempifyPipeline(config: PipelineConfig).run(source: Path | list[Path]) -> PipelineResult` as the single public entry point of the pipeline layer, executing the fixed sequence `detect → validate_geospatial → validate_compatibility → interpolate → validate_post → write → generate_report`.

### REQ-002 (Ubiquitous)

THE SYSTEM SHALL execute the seven phases of `run()` in the order defined in REQ-001, without reordering, skipping (except where REQ-005 and REQ-006 explicitly allow), or parallelizing phases.

### REQ-003 (Event-driven)

WHEN a `ProgressCallback` is provided in `PipelineConfig`, THE SYSTEM SHALL invoke it at the start and end of each of the seven phases and, during interpolation, at a configurable frequency with the current phase name and progress fraction. The callback frequency is configurable via `PipelineConfig.progress_frequency_hz` (default `4` Hz). The callback MUST conform to the following `Protocol` (verified by `mypy --strict`):

```python
from typing import Protocol, Literal

class ProgressCallback(Protocol):
    def __call__(
        self,
        phase: Literal[
            "detection",
            "validation_pre",
            "interpolation",
            "validation_post",
            "write",
            "report",
        ],
        progress: float,  # [0.0, 1.0]
        message: str | None = None,
    ) -> None: ...
```

### REQ-004 (Event-driven)

WHEN no `ProgressCallback` is provided, THE SYSTEM SHALL execute silently without emitting progress events, except for log records at INFO level.

### REQ-005 (Unwanted)

IF `GeospatialCoherenceValidator` raises `GeospatialIncoherenceError` or `MethodVariableCompatibilityChecker` raises `MethodVariableIncompatibilityError` during pre-processing validation (see `../validation/requirements.md` REQ-002, REQ-003), THEN THE SYSTEM SHALL abort execution immediately (fail-fast), propagate the original exception wrapped in `TempifyPipelineError` preserving the underlying error code, and skip the remaining phases.

### REQ-006 (Event-driven)

WHEN `PostInterpolationValidator` reports failures (see `../validation/requirements.md` REQ-004), THE SYSTEM SHALL record each failure as a warning in the `ValidationReport`, continue execution to `write` and `generate_report`, and surface the warnings in the final `ProcessingReport` under a dedicated section.

### REQ-007 (Ubiquitous)

THE SYSTEM SHALL produce a `ProcessingReport` containing the following provenance fields: tempify version, ISO-8601 UTC timestamp, fully-resolved `PipelineConfig` (including method, target frequency, all hyperparameters), `DetectionResult` summary (structure mode, temporal frequency, variable profile, confidence scores), MD5 hash of every input file, MD5 hash of every output file, MD5 hash of the serialized `PipelineConfig`, list of post-interpolation validation warnings, and Rymes-Myers iteration count when applicable (see `../core-interpolation/requirements.md` REQ-007). In `dry_run` mode (REQ-011), the report omits the `outputs` block (or sets it to an empty list). The pipeline excludes the report's own timestamp field from any MD5 computation, per ADR-0007.

### REQ-008 (Ubiquitous)

THE SYSTEM SHALL NOT mutate input `xr.DataArray` objects returned by `BaseReader.read()` (see `../io-handlers/requirements.md` REQ-002), including NOT triggering eager evaluation of lazy Dask arrays unless the writer explicitly requires materialization. Any transformation in `interpolate` or `validate_post` produces a new array, and the original reference remains structurally and value-wise unchanged (and equally lazy when applicable).

### REQ-009 (Ubiquitous)

THE SYSTEM SHALL raise typed exceptions from a single hierarchy rooted at `TempifyPipelineError`, each carrying a referenceable error code (string identifier) and a Spanish-language human-readable message; sub-classes include at minimum `PipelinePreValidationError`, `PipelineInterpolationError`, `PipelineWriteError`, `PipelineReportError`.

### REQ-010 (Ubiquitous)

THE SYSTEM SHALL guarantee bit-exact reproducibility: given identical inputs, identical `PipelineConfig`, and identical tempify version, two independent executions of `run()` SHALL produce outputs with identical MD5 hashes (the report timestamp is excluded from this comparison and isolated in a single field).

### REQ-011 (Optional)

WHERE `PipelineConfig.dry_run=True`, THE SYSTEM SHALL execute Detection + pre-Validation (`validate_geospatial`, `validate_compatibility`) + Statistics computation + report generation (formatted as if interpolation had occurred, with `[DRY_RUN]` prefix in the report title and the relevant metadata fields), BUT SHALL SKIP interpolation, post-validation, and write. The returned `PipelineResult` carries `outputs=[]`; the `ProcessingReport.outputs` field is an empty list, while `inputs[i].md5` is computed normally for every input file.

### REQ-012 (Optional)

WHERE the caller provides an optional `frequency_resolver_callback: FrequencyResolverProtocol | None` field in `PipelineConfig`, AND the Detection layer cannot resolve temporal frequency automatically (see `../temporal-frequency-resolver/requirements.md` REQ-004), THE SYSTEM SHALL invoke the callback to obtain a frequency before raising `FrequencyResolutionError`. If no callback is provided OR the callback fails to return a valid frequency, THE SYSTEM SHALL raise `FrequencyResolutionError` wrapped in `TempifyPipelineError`.

## 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Performance | El overhead total del pipeline (detect + validate + report) debe ser <5% del tiempo de interpolación pura sobre el benchmark canónico (WorldClim Chile 2.5min, 12 meses) | Benchmark `tests/benchmark/test_pipeline_overhead.py` que compara `TempifyPipeline.run()` vs `PchipMeanPreservingInterpolator.interpolate()` directo |
| NFR-002 | Reliability | Reproducibilidad bit-exact entre ejecuciones independientes con mismos inputs y config | Test `test_pipeline_md5_reproducible` que ejecuta `run()` dos veces y compara MD5 de outputs |
| NFR-003 | Usability | Frecuencia del callback de progreso configurable; valor por defecto cada 5% de píxeles procesados durante interpolación | Test `test_pipeline_progress_callback_frequency` parametrizado en 1%, 5%, 10% |
| NFR-004 | Memory | El pipeline no debe mantener simultáneamente en memoria dos copias completas del `DataArray` (input y output): la lazy evaluation de xarray/Dask debe preservarse end-to-end hasta el writer | Profiling con memray sobre stack 12×3000×500 verificando pico de memoria <2× del tamaño de un único stack |
| NFR-005 | Maintainability | Cobertura de tests del módulo `tempify.pipeline` ≥85% | `pytest --cov=tempify.pipeline --cov-fail-under=85` |
| NFR-006 | Usability | Mensajes de error en español con código referenciable | Test `test_pipeline_error_messages_spanish` |

## 6. Criterios de aceptación

Lista verificable que define cuándo esta spec está completamente implementada:

- [ ] REQ-001 cubierto por test `test_pipeline_run_returns_pipeline_result`
- [ ] REQ-002 cubierto por test `test_pipeline_phase_order_is_deterministic`
- [ ] REQ-003 cubierto por test `test_pipeline_invokes_progress_callback_per_phase`
- [ ] REQ-004 cubierto por test `test_pipeline_runs_silently_without_callback`
- [ ] REQ-005 cubierto por tests `test_pipeline_fails_fast_on_geospatial_error` y `test_pipeline_fails_fast_on_method_variable_incompat`
- [ ] REQ-006 cubierto por test `test_pipeline_warns_and_continues_on_post_validation_failure`
- [ ] REQ-007 cubierto por test `test_pipeline_report_contains_full_provenance`
- [ ] REQ-008 cubierto por test `test_pipeline_does_not_mutate_input_dataarray`
- [ ] REQ-009 cubierto por test `test_pipeline_error_hierarchy_and_codes`
- [ ] REQ-010 cubierto por test `test_pipeline_bit_exact_reproducibility`
- [ ] REQ-011 cubierto por test `test_pipeline_dry_run_skips_interpolation_and_write`
- [ ] REQ-012 cubierto por test `test_pipeline_invokes_frequency_resolver_callback`
- [ ] NFR-001 medido y dentro del umbral (<5% overhead)
- [ ] NFR-002 verificado con MD5 comparison
- [ ] NFR-003 verificado con tres frecuencias parametrizadas
- [ ] NFR-004 verificado con memray sobre el benchmark canónico
- [ ] NFR-005 verificado en CI
- [ ] NFR-006 verificado con catálogo de errores en español
- [ ] Documentación API completa (docstrings NumPy en `TempifyPipeline`, `PipelineConfig`, `PipelineResult`, `ProcessingReport`, `ProgressCallback`)
- [ ] CHANGELOG actualizado

## 7. Dependencias y supuestos

### Specs relacionadas

- Bloqueada por:
  - [core-interpolation](../core-interpolation/requirements.md) (provee `BaseInterpolator`)
  - [io-handlers](../io-handlers/requirements.md) (provee `BaseReader`, `BaseWriter`)
  - [validation](../validation/requirements.md) (provee `GeospatialCoherenceValidator`, `MethodVariableCompatibilityChecker`, `PostInterpolationValidator`, `ValidationReport`)
  - [structure-detection](../structure-detection/requirements.md) (provee `StructureDetector`, `DetectionResult`)
  - [temporal-frequency-resolver](../temporal-frequency-resolver/requirements.md) (provee `TemporalFrequencyResolver`)
- Bloquea:
  - [cli](../cli/requirements.md)
  - Futuras specs `gui` y `packaging`

### Supuestos

- Las capas inferiores cumplen sus contratos publicados (interfaces y tipos de retorno tal como están declarados en `../../steering/architecture.md`).
- `PipelineConfig` es inmutable durante una ejecución; cualquier cambio requiere construir una nueva instancia.
- La versión de tempify se obtiene a través de `importlib.metadata.version("tempify")` y queda registrada en el reporte.
- El cliente (CLI, GUI, script) es responsable de construir el `PipelineConfig` y de exponer al usuario humano cualquier información del `PipelineResult`.
- El `xr.DataArray` cargado por el reader es perezoso (Dask) y la interpolación preserva esa pereza hasta el writer.

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Acoplamiento accidental entre el pipeline y la CLI (lógica de presentación filtrándose al pipeline) | Media | Alto | La CLI solo construye `PipelineConfig` y consume `PipelineResult`; ninguna referencia a `typer`, `rich` o `sys.stdin` puede importarse desde `tempify.pipeline`. Test de imports prohibidos en CI. |
| Drift entre la firma del `ProgressCallback` y los clientes (CLI, GUI futura) | Media | Medio | Definir un `Protocol` explícito `ProgressCallback` con type hints estrictos verificados por `mypy --strict`; cualquier cambio rompe compilación y obliga a actualizar clientes. |
| Explosión de excepciones tipadas inconsistentes entre capas | Media | Medio | Jerarquía única bajo `TempifyPipelineError`; las excepciones de las capas inferiores se envuelven (`raise PipelinePreValidationError(...) from e`) preservando el código de error original. ADR específico si aparece divergencia. |
| Ambigüedad sobre quién invoca el prompt interactivo de frecuencia temporal (pipeline vs CLI) | Media | Medio | El pipeline NO prompts; recibe un callback opcional `frequency_resolver_callback` en `PipelineConfig`. Si no hay callback y la detección falla, el pipeline propaga `FrequencyResolutionError` (ver `../temporal-frequency-resolver/requirements.md` REQ-004). La CLI provee el callback interactivo. Requiere ADR para fijar el contrato. |
| Pérdida de la pereza de Dask por un colapso accidental (`.values`, `.compute`) en alguna fase | Baja | Alto | Test `test_pipeline_preserves_lazy_evaluation` que verifica que el `DataArray` permanece dask-backed hasta `write`. |
| Drift entre `DetectionResult.confidence` y la información reportada por `temporal-frequency-resolver` y `structure-detection` (formato del dict de confianza no contractualizado) | Media | Bajo | Contractualizar el shape del dict `confidence` en un ADR antes de implementar el reporte. |

## 8. Referencias

- Spec-Driven Development (GitHub spec-kit): https://github.com/github/spec-kit
- EARS notation: https://alistairmavin.com/ears/
- CF Conventions (atributos de procedencia en NetCDF output): https://cfconventions.org/
- ADR-0001 — Por qué xarray como abstracción central (define el contrato del `DataArray` que el pipeline orquesta).
- ADR-0007 — Reproducibility policy: modos `strict`/`parallel`, exclusión del timestamp del MD5 del reporte (ver `docs/adr/0007-reproducibility-policy.md`). Aplica a REQ-007 y REQ-010.
- ADR-0008 — Confidence scoring and `DetectionResult` contract: forma del dict `confidence` consumido por REQ-007 (ver `docs/adr/0008-confidence-scoring-and-detection-result-contract.md`).
- ADR-0010 — Contrato de `frequency_resolver_callback` entre Pipeline y CLI/GUI: aplica a REQ-012 y al riesgo sobre el prompt interactivo.
- ADR-0014 — Corrección de naming `tempifyPipeline` → `TempifyPipeline` (PascalCase para clases por PEP 8). Aplica a REQ-001 y a toda referencia a la clase (ver `docs/adr/0014-tempifypipeline-naming-correction.md`).
- Schema canónico del reporte: `docs/schemas/processing-report.schema.md`.
- Capa 5 (`tempify.pipeline`) en `../../steering/architecture.md`.
- Reglas arquitectónicas duras en `../../steering/architecture.md` (sección "Reglas arquitectónicas duras"), particularmente la regla 1 (capas inferiores no conocen capas superiores) y la regla 5 (errores tipados).
