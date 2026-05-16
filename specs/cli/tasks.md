# Tasks — cli

**Estado:** Approved
**Design doc:** [design.md](design.md)
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-15

## Reglas para tasks

Cada task es atómica (≤4h, un commit), verificable (criterio de done observable), TDD estricto (test primero, luego impl), e independiente cuando es posible. Tres fases: Fundamentos → Incremental → Docs+Integración.

Convención de archivos:
- Código: `src/tempify/cli/...`
- Tests: `tests/unit/cli/...` y `tests/integration/cli/...`

## Fase 1: Fundamentos

### task-1.1: Scaffolding del paquete `tempify.cli`

**Tipo:** chore
**Estimación:** 1h
**Bloquea:** task-1.2, task-1.3, task-1.4, task-1.5, task-1.6, task-1.7
**Bloqueada por:** —

**Descripción:** Crear estructura de archivos vacíos (con TODO) según design.md §2:
`src/tempify/cli/{__init__.py, app.py, errors.py, i18n.py, interactive.py, progress.py}`
y `src/tempify/cli/commands/{__init__.py, convert.py, inspect.py, validate.py, profiles.py, version.py}`.

**Criterio de done:**
- [ ] Todos los archivos creados con stubs (funciones con `raise NotImplementedError`)
- [ ] `from tempify.cli import app` importa sin error
- [ ] `__all__ = ["app"]` exportado en `__init__.py`
- [ ] Entry point de `pyproject.toml` (`tempify = "tempify.cli:app"`) ya resuelve al objeto

**Archivos:**
- `src/tempify/cli/__init__.py`
- `src/tempify/cli/app.py`
- `src/tempify/cli/errors.py`
- `src/tempify/cli/i18n.py`
- `src/tempify/cli/interactive.py`
- `src/tempify/cli/progress.py`
- `src/tempify/cli/commands/__init__.py`
- `src/tempify/cli/commands/{convert,inspect,validate,profiles,version}.py`

### task-1.2: Catálogo de exit codes y `CliError`

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-1.3, task-2.10 (exit_codes_canonical), task-2.6 (force-method)
**Bloqueada por:** task-1.1

**Descripción:** Implementar `tempify.cli.errors.EXIT_CODES`, dataclass `CliError`, mapeo `TempifyPipelineError → exit_code`, y helper `errors.handle(exc) -> int`. Definir TDD-style con test que valida los 5 códigos canónicos.

**Criterio de done:**
- [ ] Test `test_exit_codes_dict_canonical` valida claves y valores (SUCCESS=0, VALIDATION_FAILURE=1, USER_CANCEL=2, INTERNAL_ERROR=3, SIGINT=130)
- [ ] Test `test_handle_pipeline_pre_validation_returns_1`
- [ ] Test `test_handle_interactive_required_returns_2`
- [ ] Test `test_handle_unexpected_returns_3`
- [ ] `EXIT_CODES: Final[dict[str, int]]` con `typing.Final`
- [ ] `CliError` con `code`, `message_key`, `context`, `exit_code`; frozen dataclass
- [ ] mypy --strict + ruff verde

**Archivos:**
- `src/tempify/cli/errors.py`
- `tests/unit/cli/test_errors.py`

### task-1.3: Módulo `i18n` con catálogo ES/EN

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-1.6, task-2.x (todos los comandos)
**Bloqueada por:** task-1.1

**Descripción:** Implementar `MESSAGES: dict[str, dict[str, str]]` (locales `es`, `en`), función `t(key: str, **kwargs) -> str`, resolución de locale desde `TEMPIFY_LANG` (default `es`).

**Criterio de done:**
- [ ] Test `test_t_returns_spanish_by_default`
- [ ] Test `test_t_returns_english_when_env_var_en`
- [ ] Test `test_t_falls_back_to_key_if_missing`
- [ ] Test `test_t_interpolates_kwargs` (`"hola {name}"` → `"hola Mundo"`)
- [ ] Catálogo cubre al menos las claves usadas en errors.py + prompts de interactive.py
- [ ] mypy --strict + ruff verde

**Archivos:**
- `src/tempify/cli/i18n.py`
- `tests/unit/cli/test_i18n.py`

### task-1.4: `_build_pipeline_config` (única función CLI→pipeline)

**Tipo:** test+impl
**Estimación:** 3h
**Bloquea:** task-2.1, task-2.2, task-2.3
**Bloqueada por:** task-1.1

**Descripción:** Implementar `_build_pipeline_config(...)` según design.md §3. Función pura que traduce flags a `PipelineConfig` inmutable. Acepta `dry_run`, `skip_pre_validation`, callbacks. Lazy import de `tempify.pipeline.PipelineConfig` dentro de la función.

**Criterio de done:**
- [ ] Test `test_build_config_returns_pipeline_config`
- [ ] Test `test_build_config_dry_run_true_skip_pre_validation_true_for_inspect`
- [ ] Test `test_build_config_dry_run_true_skip_pre_validation_false_for_validate`
- [ ] Test `test_build_config_skip_pre_validation_requires_dry_run` (ValueError si `skip_pre_validation=True` con `dry_run=False`)
- [ ] Test `test_build_config_invalid_method_raises_cli_error`
- [ ] Signature exacta de design.md §3
- [ ] Docstring NumPy completo
- [ ] mypy --strict + ruff verde

**Archivos:**
- `src/tempify/cli/_config.py` (función privada, separada de `app.py` para testeo)
- `tests/unit/cli/test_build_pipeline_config.py`

### task-1.5: `_make_progress_callback` (Rich → ProgressCallback)

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.1
**Bloqueada por:** task-1.1

**Descripción:** Implementar fábrica que adapta `rich.progress.Progress` al `Protocol` `ProgressCallback` definido en `specs/pipeline/requirements.md` REQ-003. Mapea 7 fases a updates de la barra.

**Criterio de done:**
- [ ] Test `test_callback_satisfies_progress_protocol` (runtime `isinstance` con `@runtime_checkable`)
- [ ] Test `test_callback_updates_task_description_per_phase`
- [ ] Test `test_callback_updates_completed_percentage`
- [ ] Test `test_progress_bar_shown` (REQ-002) — verifica al menos 1 invocación por fase del pipeline mockeado
- [ ] mypy --strict + ruff verde

**Archivos:**
- `src/tempify/cli/progress.py`
- `tests/unit/cli/test_progress.py`

### task-1.6: `app.py` con Typer, locale ES, UTF-8 enforcement

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-1.7, task-2.x
**Bloqueada por:** task-1.2, task-1.3

**Descripción:** Instanciar `app = typer.Typer(...)` con configuración de design.md §3. Resolver locale al startup (`TEMPIFY_LANG` → default `es`). Verificar `PYTHONIOENCODING` o `sys.stdout.encoding`; emitir warning si no es UTF-8 y setear `errors="replace"`.

**Criterio de done:**
- [ ] Test `test_app_is_typer_instance`
- [ ] Test `test_locale_defaults_to_es`
- [ ] Test `test_locale_respects_tempify_lang_env_var`
- [ ] Test `test_warn_on_non_utf8_stdout_encoding` (monkeypatch `sys.stdout.encoding="cp1252"`)
- [ ] Test `test_spanish_accents_render` (REQ encoding, captura stdout con acentos)
- [ ] `pretty_exceptions_enable=False`, `add_completion=False`, `no_args_is_help=True`
- [ ] mypy --strict + ruff verde

**Archivos:**
- `src/tempify/cli/app.py`
- `tests/unit/cli/test_app.py`

### task-1.7: SIGINT handler con cleanup + exit 130

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.9 (test_sigint_exits_130)
**Bloqueada por:** task-1.2, task-1.6

**Descripción:** Implementar `_sigint_handler` en `app.py`, registrarlo via `signal.signal(signal.SIGINT, ...)` al inicializar el módulo. Llama `cleanup_tmp_files()` (stub que delega a un registry de tmp files) y `sys.exit(130)`. Idempotente.

**Criterio de done:**
- [ ] Test `test_sigint_handler_calls_cleanup`
- [ ] Test `test_sigint_handler_exits_130`
- [ ] Test `test_sigint_handler_idempotent` (registrar 2x no rompe)
- [ ] Test `test_sigint_exits_130` (REQ-013, integración con `os.kill(os.getpid(), SIGINT)` en subprocess)
- [ ] Registry de tmp files (set módulo-level con `register_tmp(path)` / `cleanup_tmp_files()`)
- [ ] mypy --strict + ruff verde

**Archivos:**
- `src/tempify/cli/app.py` (extensión)
- `src/tempify/cli/_cleanup.py`
- `tests/unit/cli/test_sigint.py`

## Fase 2: Subcomandos y flujos

### task-2.1: Subcomando `convert` — test esqueleto

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.2
**Bloqueada por:** task-1.4, task-1.5

**Descripción:** Escribir `test_convert_basic` (REQ-001) con `CliRunner` y `mock_pipeline` fixture: invoca `convert source.nc -o out.nc -m pchip_mp`, verifica exit 0, verifica que `TempifyPipeline.run` fue llamado con `PipelineConfig` correcto.

**Criterio de done:**
- [ ] Test creado y falla con `NotImplementedError`
- [ ] Fixture `mock_pipeline` definido en `tests/conftest.py`
- [ ] Fixture `tiny_input.nc` o stub equivalente

**Archivos:**
- `tests/unit/cli/test_convert.py`
- `tests/conftest.py` (extensión)

### task-2.2: Subcomando `convert` — implementación + progress bar

**Tipo:** impl
**Estimación:** 3h
**Bloquea:** task-2.3
**Bloqueada por:** task-2.1

**Descripción:** Implementar `convert` siguiendo el pseudo-código de design.md §5. Lazy import de `tempify.pipeline`, construcción de `Progress` rich, adapter via `_make_progress_callback`, llamada a `_build_pipeline_config`, render con `rich.Table`, soporte `--report` (REQ-005).

**Criterio de done:**
- [ ] `test_convert_basic` pasa
- [ ] `test_progress_bar_shown` pasa
- [ ] `test_report_flag_writes_markdown_conformant` pasa (parsea con `jsonschema` o regex sobre las 9 secciones del schema)
- [ ] Manejo de excepciones via `errors.handle()` → exit code correcto
- [ ] Docstring NumPy completo
- [ ] mypy --strict + ruff verde

**Archivos:**
- `src/tempify/cli/commands/convert.py`
- `tests/unit/cli/test_convert.py` (extensión)

### task-2.3: Subcomando `inspect` (dry_run + skip_pre_validation=True)

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.4
**Bloqueada por:** task-2.2

**Descripción:** Implementar `inspect` que construye `PipelineConfig(dry_run=True, skip_pre_validation=True)` y renderiza `result.detection` con `rich.Table`. Test `test_inspect_runs_only_detection` (REQ-007) verifica que `PipelineConfig` recibido tiene ambos flags True.

**Criterio de done:**
- [ ] Test `test_inspect_runs_only_detection` pasa
- [ ] Test `test_inspect_renders_detection_result_as_table`
- [ ] Test `test_inspect_exit_0_on_success`
- [ ] Sin imports directos de `tempify.detection`
- [ ] mypy --strict + ruff verde

**Archivos:**
- `src/tempify/cli/commands/inspect.py`
- `tests/unit/cli/test_inspect.py`

### task-2.4: Subcomando `validate` (dry_run, sin skip_pre_validation)

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.5
**Bloqueada por:** task-2.3

**Descripción:** Implementar `validate` que ejecuta pipeline con `dry_run=True` y renderiza `result.validation`. Exit 0 si todos los checks PASS, 1 si algún ERROR.

**Criterio de done:**
- [ ] Test `test_validate_exits_0_on_all_pass`
- [ ] Test `test_validate_exits_1_on_error` (REQ-008) con fixture CRS incoherente
- [ ] Test `test_validate_renders_validation_report_as_table`
- [ ] Mensajes en ES
- [ ] mypy --strict + ruff verde

**Archivos:**
- `src/tempify/cli/commands/validate.py`
- `tests/unit/cli/test_validate.py`

### task-2.5: Subcomando `profiles list`

**Tipo:** test+impl
**Estimación:** 1.5h
**Bloquea:** task-2.6
**Bloqueada por:** task-2.4

**Descripción:** Implementar subapp `profiles_app` con subcomando `list`. Itera `tempify.profiles.iter_profiles()` y renderiza tabla rich con name, units, allowed_methods.

**Criterio de done:**
- [ ] Test `test_profiles_list_outputs` (REQ-009) — todos los perfiles del paquete aparecen
- [ ] Test `test_profiles_list_columns_present`
- [ ] mypy --strict + ruff verde

**Archivos:**
- `src/tempify/cli/commands/profiles.py`
- `tests/unit/cli/test_profiles.py`

### task-2.6: Subcomando `version` con dependency versions

**Tipo:** test+impl
**Estimación:** 1h
**Bloquea:** task-2.7
**Bloqueada por:** task-2.5

**Descripción:** Implementar `version` usando `importlib.metadata.version()` para `tempify`, `xarray`, `dask`, `rioxarray`, `numpy`, `scipy`, `typer`. **Sin imports de pipeline** (camino crítico de cold start).

**Criterio de done:**
- [ ] Test `test_version_outputs` (REQ-010) — todas las deps aparecen
- [ ] Test `test_version_no_pipeline_import` (AST sobre el módulo: no debe haber `import tempify.pipeline`)
- [ ] mypy --strict + ruff verde

**Archivos:**
- `src/tempify/cli/commands/version.py`
- `tests/unit/cli/test_version.py`

### task-2.7: Flujo `--force-method` con confirmación tipada

**Tipo:** test+impl
**Estimación:** 3h
**Bloquea:** task-2.8
**Bloqueada por:** task-2.6, task-1.2, task-1.3

**Descripción:** Implementar `interactive.prompt_typed_confirmation(prompt, literal="si entiendo")` y wiring en `convert`. Tres escenarios cubiertos por tests (a, b, c de design.md §7 test_force_method_requires_confirmation).

**Criterio de done:**
- [ ] Test `test_force_method_without_i_know_flag_exits_3_TFY_CLI_0011`
- [ ] Test `test_force_method_wrong_confirmation_exits_2`
- [ ] Test `test_force_method_correct_confirmation_propagates_to_config` (REQ-011)
- [ ] Test `test_prompt_typed_confirmation_rejects_case_variants` ("Si Entiendo" no es válido)
- [ ] Log warning emitido cuando override es aplicado
- [ ] Código de error `TFY-CLI-0011` agregado a catálogo
- [ ] mypy --strict + ruff verde

**Archivos:**
- `src/tempify/cli/interactive.py` (extensión)
- `src/tempify/cli/commands/convert.py` (extensión)
- `tests/unit/cli/test_force_method.py`

### task-2.8: Detección Non-TTY → InteractiveRequiredError

**Tipo:** test+impl
**Estimación:** 1.5h
**Bloquea:** task-2.9
**Bloqueada por:** task-2.7

**Descripción:** Implementar `interactive.require_tty()` y `is_interactive()`. Wiring en `convert` para que cuando un prompt sería necesario y `not is_interactive()`, levante `InteractiveRequiredError` (mapeada a exit 2). Soportar flag explícito `--non-interactive`.

**Criterio de done:**
- [ ] Test `test_non_tty_raises_interactive_required` (REQ-004) — `CliRunner` con `isatty=False`
- [ ] Test `test_non_interactive_flag_disables_prompts`
- [ ] Test `test_interactive_prompt_for_frequency` (REQ-003) — con TTY simulado, callback invocado cuando frecuencia desconocida
- [ ] Sin bloqueos en CI (timeouts en tests <5s)
- [ ] mypy --strict + ruff verde

**Archivos:**
- `src/tempify/cli/interactive.py` (extensión)
- `tests/unit/cli/test_interactive.py`

### task-2.9: Test arquitectónico `test_cli_imports_only_pipeline` (AST)

**Tipo:** test
**Estimación:** 2h
**Bloquea:** task-2.10
**Bloqueada por:** task-2.8

**Descripción:** Test que parsea con `ast.parse` todos los `.py` bajo `src/tempify/cli/`, recolecta `ast.Import` y `ast.ImportFrom`, y verifica que ningún módulo importa `tempify.detection`, `tempify.io`, `tempify.interpolation`, `tempify.validation`. Allow-list: `tempify.pipeline`, `tempify.profiles`, `tempify.errors`, stdlib, `typer`, `rich`, `importlib`.

**Criterio de done:**
- [ ] Test `test_cli_imports_only_pipeline` (REQ-012) pasa con la implementación actual
- [ ] Test parametrizado por archivo bajo `src/tempify/cli/`
- [ ] Mensajes de falla indican exactamente qué archivo y qué import viola la regla
- [ ] Detecta imports dinámicos triviales (`importlib.import_module("tempify.detection")`) via búsqueda de strings

**Archivos:**
- `tests/unit/cli/test_architecture.py`

### task-2.10: Tests canónicos pendientes (exit codes, encoding, report schema)

**Tipo:** test
**Estimación:** 3h
**Bloquea:** task-2.11
**Bloqueada por:** task-2.9

**Descripción:** Cerrar los tests canónicos restantes de la matriz de aceptación:
- `test_exit_codes_canonical` (REQ-006) parametrizado por código (0, 1, 2, 3, 130)
- `test_spanish_accents_render` (Windows cp1252 simulado vía monkeypatch)
- `test_report_flag_writes_markdown_conformant` (parser de las 9 secciones + jsonschema/regex)
- `test_error_messages_spanish` (NFR-002, parametrizado sobre catálogo)

**Criterio de done:**
- [ ] Los 4 tests pasan
- [ ] Cobertura del módulo `tempify.cli` ≥ 85% (NFR-004)
- [ ] mypy --strict + ruff verde

**Archivos:**
- `tests/unit/cli/test_exit_codes.py`
- `tests/unit/cli/test_encoding.py`
- `tests/unit/cli/test_report.py`
- `tests/unit/cli/test_error_messages.py`

### task-2.11: Mensajes de error TFY-CLI-NNNN completos

**Tipo:** impl+test
**Estimación:** 2h
**Bloquea:** —
**Bloqueada por:** task-2.10

**Descripción:** Poblar el catálogo `TFY-CLI-NNNN` en `tempify.errors.codes` (single source of truth referenciada en requirements §7). Cubrir todos los errores que el CLI puede emitir: arg inválido, archivo no encontrado, method desconocido, override sin i-know, etc.

**Criterio de done:**
- [ ] Test contractual `test_all_cli_errors_have_code_and_message` (itera el catálogo)
- [ ] Cada código tiene mensaje ES y EN
- [ ] Mensajes referencian `TFY-CLI-XXXX` literal
- [ ] mypy --strict + ruff verde

**Archivos:**
- `src/tempify/errors/codes.py` (extensión namespace CLI)
- `src/tempify/cli/i18n.py` (extensión)
- `tests/unit/cli/test_error_catalog.py`

## Fase 3: Documentación e integración

### task-3.1: Docstrings NumPy en API pública

**Tipo:** docs
**Estimación:** 2h
**Bloquea:** task-3.2
**Bloqueada por:** task-2.11

**Descripción:** Completar docstrings NumPy en todas las funciones-comando, `_build_pipeline_config`, `_make_progress_callback`, `prompt_typed_confirmation`, `errors.handle`. Sections: Parameters, Returns, Raises, Examples.

**Criterio de done:**
- [ ] Lint `pydocstyle --convention=numpy` verde sobre `src/tempify/cli/`
- [ ] Examples ejecutables vía doctest donde aplica
- [ ] Cobertura de docstrings ≥95% (medida por `interrogate`)

**Archivos:**
- `src/tempify/cli/**/*.py`

### task-3.2: Test de integración end-to-end con fixture mini WorldClim

**Tipo:** test
**Estimación:** 3h
**Bloquea:** task-3.3
**Bloqueada por:** task-3.1

**Descripción:** Test que ejecuta el CLI real (`subprocess.run`) sobre un fixture sintético tipo WorldClim 3x3 mensual y verifica: (a) genera NetCDF de salida con 365 valores, (b) reporte Markdown se escribe, (c) exit 0. Test paralelo: `inspect` luego `convert` con parámetros sugeridos.

**Criterio de done:**
- [ ] Test `test_end_to_end_convert_small_fixture` pasa
- [ ] Test `test_end_to_end_inspect_then_convert` pasa
- [ ] Fixture `synthetic_3x3_monthly.nc` documentado/generado en `tests/fixtures/`
- [ ] Tests marcados con `@pytest.mark.integration`, tiempo <30s

**Archivos:**
- `tests/integration/cli/test_end_to_end.py`
- `tests/fixtures/generate_synthetic.py` (si no existe)

### task-3.3: Benchmark cold start <500ms p95 (NFR-003)

**Tipo:** test
**Estimación:** 2h
**Bloquea:** task-3.4
**Bloqueada por:** task-3.2

**Descripción:** Test `test_cli_cold_start_under_500ms` mide `subprocess.run(["tempify", "version"])` 20 veces, calcula p95, exige `<500ms`. Si falla, profilear con `python -X importtime` y eliminar imports eager. Test condicional (skip en CI containerizado si baseline >500ms).

**Criterio de done:**
- [ ] Test pasa en máquina local (Windows + Linux)
- [ ] `pyproject.toml` no introduce nuevas deps top-level
- [ ] Documentar en `impl-log.md` el baseline medido

**Archivos:**
- `tests/perf/test_cold_start.py`
- `specs/cli/impl-log.md` (apunte)

### task-3.4: README example + CHANGELOG

**Tipo:** docs
**Estimación:** 1.5h
**Bloquea:** —
**Bloqueada por:** task-3.3

**Descripción:** Agregar sección "CLI usage" al README con ejemplos de `convert`, `inspect`, `validate`, `profiles list`, `version`. Actualizar `CHANGELOG.md` con entrada para la feature CLI.

**Criterio de done:**
- [ ] README incluye al menos 3 ejemplos ejecutables
- [ ] CHANGELOG entrada bajo `[Unreleased]` con referencia a REQs cubiertas
- [ ] Markdown lint verde

**Archivos:**
- `README.md`
- `CHANGELOG.md`

## Resumen

| Fase | # tasks | Estimación total |
|---|---|---|
| Fase 1 — Fundamentos | 7 | 14h |
| Fase 2 — Subcomandos e incremental | 11 | 24h |
| Fase 3 — Docs e integración | 4 | 8.5h |
| **Total** | **22** | **46.5h** |

## Trazabilidad tasks → REQs

| REQ | Task(s) primarias |
|---|---|
| REQ-001 | task-1.6, task-2.1, task-2.2 |
| REQ-002 | task-1.5, task-2.2 |
| REQ-003 | task-2.8 |
| REQ-004 | task-2.8 |
| REQ-005 | task-2.2, task-2.10 |
| REQ-006 | task-1.2, task-2.10 |
| REQ-007 | task-2.3 |
| REQ-008 | task-2.4 |
| REQ-009 | task-2.5 |
| REQ-010 | task-2.6 |
| REQ-011 | task-2.7 |
| REQ-012 | task-2.9 |
| REQ-013 | task-1.7 |
| NFR-001 | task-2.10 |
| NFR-002 | task-2.11 |
| NFR-003 | task-3.3 |
| NFR-004 | task-2.10 (≥85% coverage gate) |
