# Requirements — cli

**Estado:** Approved
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-15
**Última actualización:** 2026-05-16

## 1. Propósito

Proveer una interfaz de línea de comandos ergonómica que invoque las funcionalidades del API sin duplicar lógica de negocio. Soportar prompts interactivos cuando la detección automática falla.

## 2. Alcance

### In-scope

- Comandos: `convert`, `inspect`, `validate`, `profiles`, `version`.
- Prompts interactivos en español para resolver ambigüedades.
- Output formateado con `rich` (tablas, progress bars, color).
- Mensajes de error con código de error referenciable.

### Out-of-scope

- Lógica de negocio (toda en el pipeline / domain layers).
- Interfaz gráfica (cubierta en [specs/gui](../gui/requirements.md)).
- Batch / scheduling de jobs (`cron`, `at`, colas).
- Configuración persistente (`~/.tempifyrc` y similares).
- Autocompletion de shell (bash/zsh/PowerShell), diferido a v0.2.

## 3. Actores y casos de uso

### Actor: Usuario que no programa en Python pero necesita ejecutar conversiones puntuales.

**Caso de uso típico:** Usuario ejecuta `tempify convert ./worldclim_chile/ --method pchip_mp --output ./out.nc` y recibe progress bar + reporte final.

## 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL expose a `tempify` command with subcommands `convert`, `inspect`, `validate`, `profiles`, and `version`.

### REQ-002 (Event-driven)

WHEN `convert` is invoked, THE SYSTEM SHALL display a progress bar showing percentage of pixels processed.

### REQ-003 (State-driven)

WHILE running interactively, THE SYSTEM SHALL prompt the user for any ambiguity that cannot be resolved automatically (e.g., unknown temporal frequency).

### REQ-004 (Event-driven)

WHEN running non-interactively (no TTY), THE SYSTEM SHALL fail with `InteractiveRequiredError` rather than blocking on a prompt.

### REQ-005 (Optional)

WHERE the user passes `--report path.md`, THE SYSTEM SHALL write a processing report following [`docs/schemas/processing-report.schema.md`](../../docs/schemas/processing-report.schema.md) with sections Encabezado, Inputs, Detección, Validación pre, Parámetros, Estadísticas, Validación post, Outputs, Procedencia.

### REQ-006 (Ubiquitous)

THE SYSTEM SHALL exit with code 0 on success, 1 on validation failure, 2 on user cancellation, 3 on internal error, 130 on SIGINT.

### REQ-007 (Event-driven)

WHEN invoked as `tempify inspect <input>`, THE SYSTEM SHALL run only Detection (no validation, no interpolation) and print the `DetectionResult` to stdout, formatted by `rich`.

### REQ-008 (Event-driven)

WHEN invoked as `tempify validate <input>`, THE SYSTEM SHALL run Detection + pre-validation and print the `ValidationReport` to stdout, exit code 0 if all checks PASS, 1 if any ERROR.

### REQ-009 (Event-driven)

WHEN invoked as `tempify profiles list`, THE SYSTEM SHALL list available variable profiles from the `tempify.profiles` package with their `name`, `units`, and `allowed_methods`.

### REQ-010 (Event-driven)

WHEN invoked as `tempify version`, THE SYSTEM SHALL print `tempify <version>` and the versions of its core dependencies (`xarray`, `dask`, `rioxarray`, `numpy`, `scipy`).

### REQ-011 (Optional, override precipitación)

WHERE the user passes `--force-method <m> --i-know-what-i-am-doing` for an incompatible `(variable, method)` pair, THE SYSTEM SHALL prompt for typed confirmation (literal `si entiendo`), log a `WARN`, and pass the override to the pipeline, which stamps `force_method_used=true` in the output dataset `attrs` (per [ADR-0004](../../docs/adr/0004-precipitation-policy.md)).

### REQ-012 (Ubiquitous, regla arquitectónica)

THE SYSTEM SHALL NOT import any module from `tempify.detection`, `tempify.interpolation`, `tempify.io`, or `tempify.validation` directly; only `tempify.pipeline` is allowed as a dependency in `tempify.cli`. Verificable mediante test `test_cli_imports_only_pipeline` que escanea el AST del paquete.

### REQ-013 (Event-driven)

WHEN SIGINT (Ctrl+C) is received during execution, THE SYSTEM SHALL catch it, request cooperative cancellation from the pipeline, clean up temporary files, and exit with code 130.

## 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Reliability | Reporte de procesamiento conforme al schema canónico | Test parsea el Markdown generado contra `docs/schemas/processing-report.schema.md` (secciones obligatorias presentes) |
| NFR-002 | Usability | Mensajes de error en español con código referenciable (`TFY-XXXX`) | Test `test_error_messages_spanish` con asserts sobre código y locale |
| NFR-003 | Performance | Cold start del CLI < 500 ms | Test mide tiempo de `tempify version` end-to-end y exige `<500ms` (p95 sobre 10 corridas) |
| NFR-004 | Maintainability | Cobertura del módulo `tempify.cli` ≥ 85% | Reporte `coverage.py` en CI |

## 6. Criterios de aceptación

Trazabilidad REQ → test (cada REQ tiene al menos un test nombrado):

- [ ] REQ-001 → `test_convert_basic`
- [ ] REQ-002 → `test_progress_bar_shown`
- [ ] REQ-003 → `test_interactive_prompt_for_frequency`
- [ ] REQ-004 → `test_non_tty_raises_interactive_required`
- [ ] REQ-005 → `test_report_flag_writes_markdown`
- [ ] REQ-006 → `test_exit_codes_canonical`
- [ ] REQ-007 → `test_inspect_runs_only_detection`
- [ ] REQ-008 → `test_validate_exits_1_on_error`
- [ ] REQ-009 → `test_profiles_list_outputs`
- [ ] REQ-010 → `test_version_outputs`
- [ ] REQ-011 → `test_force_method_requires_confirmation`
- [ ] REQ-012 → `test_cli_imports_only_pipeline`
- [ ] REQ-013 → `test_sigint_exits_130`
- [ ] Cobertura del módulo ≥ 85% (NFR-004)
- [ ] Documentación API completa (docstrings NumPy)
- [ ] CHANGELOG actualizado

## 7. Dependencias y supuestos

### Specs relacionadas

- Bloqueada por: [pipeline](../pipeline/requirements.md)
- Bloquea: [packaging](../packaging/requirements.md) (packaging empaqueta el entry point CLI)

### ADRs referenciados

- [ADR-0003](../../docs/adr/0003-typer-vs-click-vs-argparse.md) — Typer como framework CLI.
- [ADR-0004](../../docs/adr/0004-precipitation-policy.md) — Política de precipitación y override `--force-method`.

### Supuestos

- Los inputs son archivos legibles por GDAL via `rioxarray`.
- El entry point fuerza `PYTHONIOENCODING=utf-8` para mensajes con acentos en Windows.
- El catálogo de códigos de error (`TFY-XXXX`) vive en `tempify.errors.codes` como única fuente de verdad, consumida por CLI y pipeline.

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| TTY detection inestable en CI Windows (pseudo-TTY) | Media | Medio | Detectar vía `sys.stdout.isatty()` y exponer flag `--non-interactive` explícito; tests fijan ambos modos |
| Filtración de dependencias `typer`/`rich` hacia capas de dominio (pipeline) | Media | Alto | REQ-012 + test `test_cli_imports_only_pipeline` que escanea AST de `tempify.cli` |
| Encoding consola Windows `cp1252` corrompe acentos ES | Alta | Medio | Forzar `PYTHONIOENCODING=utf-8` en entry point; test `test_spanish_accents_render` con captura de stdout |
| Drift entre catálogo CLI de códigos de error y los emitidos por pipeline | Media | Medio | Single source of truth en `tempify.errors.codes`; test contractual de cobertura de códigos |
| Cold start de Typer (~300 ms baseline) inaceptable en scripting | Media | Medio | Imports lazy de capas (`tempify.pipeline` se importa solo cuando se invoca `convert`); compatible con PyInstaller `--onedir` |
| Edge cases en formatos no estándar | Media | Bajo | Fixtures extensivas + manejo robusto de excepciones |

## 8. Referencias

- CF Conventions: https://cfconventions.org/
- EARS notation: https://alistairmavin.com/ears/
- [steering/architecture.md](../../steering/architecture.md) § Capa 6 (CLI)
- [docs/methodology/precipitation.md](../../docs/methodology/precipitation.md)
- [docs/schemas/processing-report.schema.md](../../docs/schemas/processing-report.schema.md)
