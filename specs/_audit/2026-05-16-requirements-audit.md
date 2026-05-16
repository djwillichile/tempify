# Auditoría de requirements — Fase 1, Sub-fase 1.B

**Fecha:** 2026-05-16
**Auditor:** 9 agentes Evaluador independientes (uno por spec) + Jefe de proyecto (consolidación)
**Específicos auditados:** 9 specs (6 originales en Draft + 3 nuevas creadas en Sub-fase 1.A)
**Rúbrica:** 10 criterios estándar (completitud, EARS, trazabilidad REQ→test, NFR verificable, out-of-scope ≥3, dependencias bidireccionales, riesgos accionables, coherencia con steering, decisiones no documentadas, idioma) + checks específicos por spec.

## Tabla resumen de veredictos

| # | Spec | Veredicto | REQs | NFRs | Enmiendas | ADRs sugeridos |
|---|---|---|---|---|---|---|
| 1 | `core-interpolation` | PASS_WITH_NOTES | 10 | 5 | 10 | 5 (PCHIP family, RM tolerancia, Fourier harmónicos, extrapolación, bit-exact policy) |
| 2 | `io-handlers` | REVISAR | 6 | 1 | 9 | 4 (compresión NetCDF, serialización procedencia, filename template, hash algorithm) |
| 3 | `validation` | REVISAR | 5 | 2 | 9 | 4 (tolerancias geo, override precip, ValidationReport shape, tolerancia canónica media) |
| 4 | `structure-detection` | REVISAR | 6 | 2 | 9 | 4 (confidence scoring, tolerancias homogeneidad, contrato confidence dict, orden canónico) |
| 5 | `temporal-frequency-resolver` | REVISAR | 6 | 2 | 10 | 4 (política empate tiers, registry parsers, calendarios CF no-estándar, jerarquía errores) |
| 6 | `cli` | REVISAR | 6 | 2 | 10 | 4 (ADR-0003 Typer, exit codes, i18n, override precip) |
| 7 | `pipeline` | PASS_WITH_NOTES | 11 | 6 | 6 | 5 (ProgressCallback, frequency callback, confidence shape, timestamp policy, dry_run semantics) |
| 8 | `gui` | PASS_WITH_NOTES | 13 | 8 | 6 | 4 (PySide6 ADR-0005, threading pattern, Markdown renderer, callback Qt) |
| 9 | `packaging` | PASS_WITH_NOTES | 10 | 6 | 8 | 4 (ADR-0006 PyInstaller+Inno, signing diferred, per-user vs per-machine, CI runner pin) |

**Bloque global:** 0 specs en PASS limpio. 4 en PASS_WITH_NOTES (`core-interpolation`, `pipeline`, `gui`, `packaging`). 5 en REVISAR (`io-handlers`, `validation`, `structure-detection`, `temporal-frequency-resolver`, `cli`).

**Causa raíz dominante de REVISAR**: los 5 borradores originales heredaron secciones boilerplate (NFR genéricos, riesgo único genérico, sin trazabilidad REQ→test nombrada, dependencias copy-paste del template). Las 3 specs nuevas (`pipeline`, `gui`, `packaging`) escritas en Sub-fase 1.A no presentan ese problema porque se redactaron con contexto completo y rúbrica en mente.

## Hallazgos transversales (afectan a ≥2 specs)

### H1 — Dependencias incorrectas heredadas del template
**Specs afectadas:** `io-handlers`, `validation`, `structure-detection`, `temporal-frequency-resolver`, `cli` (las 5 en REVISAR).
**Descripción:** todas declaran `Bloqueada por: core-interpolation` o `Bloquea: cli (transitivamente)` como copia ciega del ejemplo del template, sin reflejar el grafo real de la arquitectura.
**Realidad arquitectónica** (per `steering/architecture.md`):
- I/O (Capa 1) no depende de Interpolation (Capa 4); bloquea Pipeline (Capa 5).
- Detection (Capa 2) no depende de Interpolation; bloquea Pipeline.
- Validation (Capa 3) depende de tolerancias documentadas en `core-interpolation`; bloquea Pipeline.
- CLI (Capa 6) NO debe depender directo de Interpolation; depende de Pipeline (regla arquitectónica dura nº 1).

### H2 — Trazabilidad REQ → test ausente
**Specs afectadas:** las mismas 5 en REVISAR.
**Descripción:** sección 6 contiene "Todos los REQ cubiertos por tests específicos" sin nombrar tests por REQ. Las 3 specs nuevas y `core-interpolation` sí mapean explícitamente.

### H3 — NFR boilerplate sin criterio verificable
**Specs afectadas:** `io-handlers`, `validation`, `structure-detection`, `temporal-frequency-resolver`, `cli`.
**Descripción:** NFR-001 con "Inspección manual" no es automatizable. Faltan NFR de performance/coverage con umbrales numéricos.

### H4 — Decisiones implícitas sin ADR
**Specs afectadas:** todas.
**Descripción:** decisiones técnicas afirmadas sin documento. Lista consolidada de ADRs propuestos (ver §3).

### H5 — Contrato `DetectionResult.confidence` ambiguo
**Specs afectadas:** `structure-detection`, `temporal-frequency-resolver`, `pipeline`, `gui`.
**Descripción:** `architecture.md` declara `confidence: dict[str, float]` pero `structure-detection` REQ-006 lo expone como `float` escalar. `pipeline` y `gui` lo consumen sin contrato fijo. Requiere ADR canónico de claves.

### H6 — Política de override de precipitación (`--force-method`)
**Specs afectadas:** `cli`, `validation`, `core-interpolation`.
**Descripción:** documentado en `docs/methodology/precipitation.md` pero no en ninguna spec. Requiere REQ explícito en CLI y `validation`, y ADR sobre el mecanismo.

### H7 — Naming `TempifyPipeline` (minúscula inicial)
**Specs afectadas:** `pipeline`, `gui`, `cli`.
**Descripción:** Viola `conventions.md §Naming` que exige PascalCase para clases. `architecture.md` la introdujo con esa minúscula. Decisión: renombrar a `TempifyPipeline` en todas las specs (fix transversal) o documentar excepción con ADR. **Recomendación: renombrar.**

### H8 — Reproducibilidad bit-exact vs paralelización
**Specs afectadas:** `core-interpolation` (NFR-003), `pipeline` (REQ-010, NFR-002).
**Descripción:** "bit-exact" con Dask paralelizado + Fourier FFT + BLAS por plataforma es probablemente inalcanzable. Reformular como `allclose(rtol, atol)` documentado, o restringir bit-exact al modo single-thread con seed fija.

## Enmiendas requeridas, agregadas por spec

### core-interpolation (PASS_WITH_NOTES → necesita 10 enmiendas para PASS limpio)
1. Justificar numéricamente tolerancia `1e-6` de Rymes-Myers; hacerla por-variable o relativa.
2. Comportamiento ante calendarios CF no-gregorianos (`noleap`, `360_day`): error o soporte.
3. REQ para stacks con coord `month` no contigua o duplicada.
4. REQ explícito de rechazo de precipitación (o referenciar `validation`).
5. Declarar dependencia (o ausencia justificada) con `detection`.
6. NFR-001: especificar scheduler de Dask.
7. NFR-003: reformular bit-exact (ver H8).
8. REQ-005: separar comportamientos de extrapolación en sub-requisitos.
9. REQ-010: referenciar constante canónica `DEFAULT_CHUNK_SIZE`.
10. Cubrir NaN parcial (algunos meses NaN, otros válidos) — REQ-008 actual asume todos NaN.

### io-handlers (REVISAR → 9 enmiendas)
1. Corregir dependencias: quitar "Bloqueada por core-interpolation"; agregar "Bloquea: pipeline, cli".
2. REQ Event-driven sobre metadata CF en escritura NetCDF (`units`, `calendar`, `_FillValue`, `standard_name`, `long_name`).
3. REQ Ubiquitous sobre preservación de CRS en concat multi-archivo y en escritura.
4. REQ `WHERE` para Zarr con extra opcional.
5. REQ sobre serialización de procedencia (attrs NetCDF/Zarr vs sidecar JSON GeoTIFF).
6. Mapear cada REQ a `test_xxx` nombrado.
7. Reemplazar NFR-001 (inspección manual) por NFR verificable; agregar roundtrip bit-exact.
8. Ampliar riesgos (pérdida CRS en concat, encoding NetCDF, costo MD5 en GB).
9. Completar firma del Protocol incluyendo `metadata() -> dict`.

### validation (REVISAR → 9 enmiendas)
1. REQs explícitos para continuidad cíclica (post), rango físico (post), estadísticos enumerados, política fail-fast vs warn, y override `--force-method`.
2. Especificar shape de `ValidationReport` (campos: `checks`, `severity`, `passed`, `warnings`, `errors`).
3. Mapear REQ a tests.
4. Reconciliar tolerancia conservación de media (1e-4 vs 1e-6 entre specs).
5. Dependencias bidireccionales con `io-handlers`, `structure-detection`, `pipeline`.
6. Out-of-scope ≥3: cross-variable, calendarios CF, generación de variable profiles.
7. Ampliar riesgos (float-imprecision, NaN vs sentinel, schema YAML ausente).
8. Referenciar `docs/schemas/variable-profile.schema.yaml` como dependencia.
9. NFR-001 automatizable.

### structure-detection (REVISAR → 9 enmiendas)
1. REQ-006 alineado con `DetectionResult` completo (incluir `temporal_frequency`, `variable_profile`, `confidence: dict[str, float]`).
2. REQ con tolerancias numéricas para homogeneidad (CRS EPSG, extent rtol 1e-6, resolución rtol 1e-6) o diferir a ADR.
3. REQ Optional para modo C que declare bypass de detección estructural.
4. REQ para modo A GeoTIFF multi-banda (distinto de NetCDF time-dim).
5. Separar REQ-005 en detección de heterogeneidad (raise) y disambiguación (callback).
6. Reemplazar NFRs boilerplate por: tiempo de detección <1s/100 archivos; cobertura ≥85%.
7. Corregir §7 dependencias.
8. Nombrar tests por REQ en §6.
9. Definir clase `StructureDetector` y jerarquía `StructureDetectionError → AmbiguousStructureError`.

### temporal-frequency-resolver (REVISAR → 10 enmiendas)
1. Declarar enum `TemporalFrequency` con valores soportados.
2. Definir output explícito: `ResolutionResult(frequency, tier_used, confidence, source_evidence)`.
3. Separar REQ-004 en CLI (callback) y API (`FrequencyResolutionError`), alinear nombre con `UnknownFrequencyError`.
4. REQ "Unwanted" para conflicto entre tiers.
5. Corregir dependencias (quitar core-interpolation; añadir io-handlers y pipeline).
6. NFRs verificables (resolución <100ms para 366 archivos, cobertura, extensibilidad).
7. Out-of-scope ampliado (calendarios CF no-estándar, timezones, detección espacial).
8. Tests específicos por REQ.
9. Especificar registry pattern (entry points `tempify.parsers` o subclass).
10. Tabla de parsers nombrados como REQ con regex por cada uno.

### cli (REVISAR → 10 enmiendas)
1. Reemplazar dependencia "Bloqueada por core-interpolation" por "Bloqueada por pipeline".
2. REQs EARS para `inspect`, `validate`, `profiles list`, `version`.
3. REQ Optional para `--force-method --i-know-what-i-am-doing`.
4. Detallar REQ-005 con estructura del reporte Markdown.
5. REQ: "CLI SHALL NOT import any module from detection/interpolation/io directly; only pipeline".
6. REQ para SIGINT/Ctrl+C → exit code 130 (o ampliar exit 2).
7. Trazar REQ a tests.
8. Reemplazar NFR-001 (inspección manual) por criterio automatizable.
9. Ampliar out-of-scope a ≥4.
10. Reescribir riesgos con ≥4 accionables (TTY en CI, rich/typer leak, i18n, code pages Windows).

### pipeline (PASS_WITH_NOTES → 6 enmiendas)
1. Formalizar en §8 los ADRs sugeridos en lugar de mencionarlos en mitigaciones.
2. Anclar firma del Protocol `ProgressCallback` en REQ-003 (tipos exactos).
3. Aclarar en REQ-008 si la no-mutación aplica al `DataArray` lazy.
4. REQ-011 (dry_run): declarar fases excluidas y comportamiento de `generate_report`.
5. REQ-007: comportamiento de campo MD5 en modo dry_run.
6. Promover `frequency_resolver_callback` de riesgo a campo explícito de `PipelineConfig`.

### gui (PASS_WITH_NOTES → 6 enmiendas)
1. REQ con decisión locked sobre renderer Markdown (QTextBrowser vs QWebEngineView).
2. REQ para selector visual de método con bloqueo de métodos suaves para precipitación.
3. NFR-004 (Portability): definir "best-effort" o cuantificar.
4. Cita explícita de la excepción a `conventions.md` para cobertura ≥70%.
5. Estandarizar threading: QThread vs QRunnable+QThreadPool (decisión o ADR).
6. Clarificar conflicto `tempify[gui]` opcional pip vs Qt obligatorio en bundle.

### packaging (PASS_WITH_NOTES → 8 enmiendas)
1. PyInstaller >=6.3 e Inno Setup >=6.2 como REQ (no solo supuesto); pin en pyproject `[packaging]` extra.
2. REQ que exija PySide6 declarada antes del build.
3. NFR-005 con criterio: hash SHA256 reproducible entre builds del mismo tag.
4. REQ para publicación de SHA256SUMS en GitHub Release (compensa ausencia de firma).
5. Aclarar modo de instalación (per-user vs per-machine) e impacto en REQ-007.
6. Crear `docs/adr/0006-pyinstaller-inno-setup.md` antes de aprobar.
7. Pin del runner CI (`windows-2022`) en lugar de `windows-latest`.
8. Criterio de aceptación medible para REQ-010 (matriz de coexistencia pip × instalador).

## ADRs requeridos antes de cerrar Fase 1

Numeración consolidada desde ADR-0001 (existente):

| ADR | Tema | Origen |
|---|---|---|
| 0002 | Dask vs multiprocessing como mecanismo de paralelismo | architecture.md §ADRs pendientes |
| 0003 | Typer vs Click vs argparse para CLI | architecture.md §ADRs pendientes |
| 0004 | Política de precipitación (rechazo + override `--force-method`) | architecture.md + methodology/precipitation.md |
| 0005 | PySide6 como framework GUI (vs PyQt6, Tkinter, Toga) | spec gui |
| 0006 | PyInstaller `--onedir` + Inno Setup 6.x para empaquetado Windows | spec packaging |
| 0007 | Política de reproducibilidad: bit-exact (single-thread/seeded) vs allclose (paralelo) | core-interpolation NFR-003 + pipeline NFR-002 |
| 0008 | Algoritmo de confidence scoring y contrato del dict `confidence` canónico | structure-detection + temporal-frequency-resolver + pipeline + gui |
| 0009 | Tolerancias canónicas de homogeneidad geoespacial (CRS, extent, resolución) | structure-detection + validation |
| 0010 | Tolerancia canónica de conservación de media mensual (1e-4 vs 1e-6) | core-interpolation + validation |
| 0011 | Patrón de threading GUI (QThread vs QRunnable+QThreadPool) y aislamiento Dask | gui |
| 0012 | Renderer Markdown del ReportViewer (QTextBrowser vs QWebEngineView) | gui (impacta bundle packaging) |
| 0013 | Política de signing del instalador Windows (diferida v0.2.0) y mitigación SmartScreen | packaging |
| 0014 | Naming `TempifyPipeline` (corregir minúscula inicial declarada en architecture.md) | pipeline + transversal |

**De estos 13 ADRs, los críticos para desbloquear Fase 2 son:** 0002, 0003, 0004, 0005, 0006, 0007, 0008, 0009, 0010, 0014. Los restantes (0011, 0012, 0013) pueden diferirse a `design.md` de la spec correspondiente.

## Schemas auxiliares a crear

| Archivo | Necesidad | Specs que lo consumen |
|---|---|---|
| `docs/schemas/variable-profile.schema.yaml` | Define estructura YAML de perfiles de variable consumidos por `VariableProfileMatcher` | validation, structure-detection |
| `docs/schemas/processing-report.schema.md` | Define estructura del reporte Markdown (`--report path.md`) | cli, pipeline, gui |
| `docs/schemas/detection-result.schema.md` | Documenta claves canónicas del `confidence: dict[str, float]` y el shape de `DetectionResult` | structure-detection, temporal-frequency-resolver, pipeline, gui |
| `docs/schemas/validation-report.schema.md` | Documenta el shape de `ValidationReport` | validation, pipeline |

## Plan de acción para Sub-fase 1.C

1. Redactar los 10 ADRs críticos en `docs/adr/0002-*.md` a `0010-*.md` y `0014-*.md` en una tanda.
2. Crear los 4 schemas auxiliares en `docs/schemas/`.
3. Corregir el naming `TempifyPipeline` → `TempifyPipeline` en `steering/architecture.md` y en todas las specs que lo referencian (transversal).
4. Aplicar las enmiendas listadas a los 9 `requirements.md` (uno por uno; la mayoría son pequeñas).
5. Lanzar segunda pasada de Evaluador (9 agentes) verificando que cada hallazgo está cerrado.
6. Si segunda pasada pasa: proceder a Sub-fase 1.D (gate humano spec por spec).
