# Design — cli

**Estado:** Draft
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-15

## 1. Visión técnica

La capa CLI es una **fachada delgada** sobre `tempify.pipeline`. Su única responsabilidad es traducir argumentos de línea de comandos, prompts y entornos de terminal a `PipelineConfig`, invocar `TempifyPipeline.run()` y formatear el `PipelineResult` para consumo humano (tablas `rich`, progress bars, reporte Markdown). No contiene lógica de negocio ni conoce a las capas de dominio (`detection`, `interpolation`, `io`, `validation`); ese aislamiento es una **regla arquitectónica dura** (REQ-012) verificada por test AST.

El módulo se estructura como un paquete Python con submódulos por preocupación: `app` (instancia Typer y wiring global), `commands/` (un archivo por subcomando), `progress` (adaptador Rich → `ProgressCallback`), `errors` (catálogo de excepciones y exit codes), `i18n` (mensajes localizados ES/EN) e `interactive` (prompts tipados). Los imports de `tempify.pipeline` son **lazy** dentro de cada comando para preservar NFR-003 (cold start `<500ms`).

## 2. Arquitectura propuesta

### Diagrama de componentes

```
                    ┌──────────────────────────────────────┐
   $ tempify ...    │  tempify.cli.app                     │
   ────────────────►│  • typer.Typer instance              │
                    │  • global callbacks (SIGINT, locale) │
                    │  • exit code translation             │
                    └────────┬─────────────────────────────┘
                             │
       ┌─────────────────────┼─────────────────────────┐
       ▼                     ▼                         ▼
┌──────────────┐    ┌──────────────┐         ┌────────────────┐
│  commands/   │    │  progress.py │         │  interactive.py│
│  convert.py  │    │  Rich ↔      │         │  prompts ES    │
│  inspect.py  │    │  ProgressCb  │         │  TTY checks    │
│  validate.py │    └──────────────┘         └────────────────┘
│  profiles.py │           │                         │
│  version.py  │           │                         │
└──────┬───────┘           │                         │
       │  build PipelineConfig                       │
       │  + ProgressCallback + frequency_resolver_cb │
       ▼                                             ▼
       ┌─────────────────────────────────────────────────┐
       │  tempify.pipeline.TempifyPipeline (LAZY IMPORT) │
       │   .run(source) → PipelineResult                 │
       └─────────────────────────────────────────────────┘
                             │
                             ▼
                ┌──────────────────────┐
                │  errors.py (TFY-XXXX)│
                │  i18n.py (ES/EN)     │
                └──────────────────────┘
```

### Componentes nuevos

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| `app` | `src/tempify/cli/app.py` | Instancia `typer.Typer`, registra subcomandos, instala SIGINT handler, valida `PYTHONIOENCODING`, resuelve locale desde `TEMPIFY_LANG`. Exporta el callable usado como entry point. |
| `convert` | `src/tempify/cli/commands/convert.py` | Comando `convert`: parsea flags → `_build_pipeline_config` → `TempifyPipeline.run()` → render con `rich` → escritura opcional de reporte. |
| `inspect` | `src/tempify/cli/commands/inspect.py` | Comando `inspect`: ejecuta pipeline en `dry_run` con bandera adicional `skip_pre_validation=True` para reportar solo `DetectionResult`. |
| `validate` | `src/tempify/cli/commands/validate.py` | Comando `validate`: ejecuta pipeline en `dry_run` y reporta sólo `ValidationReport` (pre-validation). |
| `profiles` | `src/tempify/cli/commands/profiles.py` | Subcomando `profiles list`: itera `tempify.profiles.iter_profiles()` (acceso restringido vía `importlib.resources`, no viola REQ-012 porque `profiles` es paquete de datos, no capa de dominio). |
| `version` | `src/tempify/cli/commands/version.py` | Imprime versiones de `tempify`, `numpy`, `xarray`, `dask`, `rioxarray`, `scipy`, `typer`. |
| `progress` | `src/tempify/cli/progress.py` | Fábrica `_make_progress_callback` que adapta `rich.progress.Progress` al `Protocol` `ProgressCallback` del pipeline. |
| `errors` | `src/tempify/cli/errors.py` | Catálogo `EXIT_CODES`, clase `CliError`, mapeo `TempifyPipelineError → exit code`, formateador de mensajes con código `TFY-XXXX`. |
| `i18n` | `src/tempify/cli/i18n.py` | Diccionario de mensajes por locale (`es`, `en`), función `t(key, **kwargs)`. |
| `interactive` | `src/tempify/cli/interactive.py` | Helpers: `require_tty()`, `prompt_frequency()`, `prompt_typed_confirmation(literal)`, `is_interactive()`. |

### Componentes modificados

| Componente | Ubicación | Cambio |
|---|---|---|
| Ninguno | — | El módulo `tempify.cli` es nuevo; el resto del código no se toca. |

## 3. Contratos públicos (APIs)

### Entry point

```python
# src/tempify/cli/__init__.py
from tempify.cli.app import app

__all__ = ["app"]
```

`pyproject.toml` ya declara `tempify = "tempify.cli:app"` (línea 57). El callable expuesto es la instancia `typer.Typer`, que Typer convierte en función al invocarla.

### `tempify.cli.app`

```python
import typer

app: typer.Typer = typer.Typer(
    name="tempify",
    help="Densificación temporal de stacks ráster geoespaciales.",
    no_args_is_help=True,
    add_completion=False,  # diferido a v0.2
    pretty_exceptions_enable=False,  # control propio vía errors.py
)
```

**Pre-condiciones:** locale resoluble (`TEMPIFY_LANG` ∈ {`es`, `en`} o ausente → `es`).
**Post-condiciones:** todos los subcomandos registrados; SIGINT handler instalado.

### Subcomandos

```python
@app.command()
def convert(
    source: Path = typer.Argument(..., exists=True, readable=True),
    output: Path = typer.Option(..., "--output", "-o"),
    method: str = typer.Option("pchip_mp", "--method", "-m"),
    target_freq: str = typer.Option("daily", "--target-freq"),
    report: Path | None = typer.Option(None, "--report"),
    force_method: bool = typer.Option(False, "--force-method"),
    i_know: bool = typer.Option(False, "--i-know-what-i-am-doing"),
    non_interactive: bool = typer.Option(False, "--non-interactive"),
    chunk_size: int = typer.Option(512, "--chunk-size"),
    seed: int | None = typer.Option(None, "--seed"),
) -> None: ...

@app.command()
def inspect(source: Path = typer.Argument(...)) -> None: ...

@app.command()
def validate(source: Path = typer.Argument(...)) -> None: ...

profiles_app = typer.Typer(help="Gestión de perfiles de variable.")
app.add_typer(profiles_app, name="profiles")

@profiles_app.command("list")
def profiles_list() -> None: ...

@app.command()
def version() -> None: ...
```

**Excepciones:** todas las funciones-comando capturan en su frontera `TempifyPipelineError` y subclases, las traducen vía `errors.handle()` y llaman `raise typer.Exit(code)`. Ninguna excepción del dominio escapa a la terminal sin formateo.

### Función `_build_pipeline_config`

```python
def _build_pipeline_config(
    *,
    output: Path,
    method: str,
    target_freq: str,
    chunk_size: int,
    seed: int | None,
    force_method: bool,
    dry_run: bool = False,
    progress_callback: ProgressCallback | None = None,
    frequency_resolver_callback: FrequencyResolverProtocol | None = None,
) -> PipelineConfig:
    """Traduce flags de CLI a un PipelineConfig inmutable."""
```

**Pre-condiciones:** `method` ∈ catálogo de métodos válidos; `target_freq` parseable.
**Post-condiciones:** `PipelineConfig` válido, inmutable, listo para `TempifyPipeline(config)`.
**Única función que traduce CLI → pipeline.** Toda otra ruta a `PipelineConfig` está prohibida.

### Función `_make_progress_callback`

```python
def _make_progress_callback(
    rich_progress: rich.progress.Progress,
    task_id: rich.progress.TaskID,
) -> ProgressCallback:
    """Adapta una barra Rich al Protocol ProgressCallback del pipeline."""
```

**Post-condiciones:** retorna un callable conforme al `Protocol` definido en `specs/pipeline/requirements.md` REQ-003. Mapea las siete fases a updates de la barra y actualiza descripción + porcentaje.

### Catálogo de exit codes

```python
# src/tempify/cli/errors.py
from typing import Final

EXIT_CODES: Final[dict[str, int]] = {
    "SUCCESS": 0,
    "VALIDATION_FAILURE": 1,
    "USER_CANCEL": 2,
    "INTERNAL_ERROR": 3,
    "SIGINT": 130,
}
```

Mapeo `TempifyPipelineError → exit code`:

| Excepción | Exit code |
|---|---|
| `PipelinePreValidationError` | `1` |
| `PostInterpolationFailure` (solo si configurado strict) | `1` |
| `InteractiveRequiredError` | `2` |
| `UserCancelledError` (incluye prompt rechazado) | `2` |
| KeyboardInterrupt → handler | `130` |
| Cualquier otra `TempifyPipelineError` | `3` |
| Excepción no esperada | `3` |

## 4. Modelos de datos

### `CliError`

```python
@dataclass(frozen=True)
class CliError(Exception):
    code: str            # e.g. "TFY-CLI-0003"
    message_key: str     # clave i18n
    context: dict[str, str] = field(default_factory=dict)
    exit_code: int = 3
```

### `LocaleConfig`

```python
@dataclass(frozen=True)
class LocaleConfig:
    lang: Literal["es", "en"]
    encoding: str  # se valida que sea utf-8
```

Catálogo de mensajes vive en `i18n.py` como dict literal `MESSAGES: dict[str, dict[str, str]]` (clave: locale, valor: clave→template). Sin dependencia externa de gettext.

## 5. Algoritmos clave

### Algoritmo `convert`

Pseudo-código:

```
1. require_utf8_locale()  # warn si no UTF-8
2. progress = rich.progress.Progress(...)
3. with progress:
       task = progress.add_task("Procesando...", total=1.0)
       cb   = _make_progress_callback(progress, task)
       freq_cb = make_interactive_frequency_resolver()
                   if is_interactive() and not non_interactive
                   else None
       if force_method:
           require_typed_confirmation(literal="si entiendo")
           log.warning("Override de compatibilidad de método: %s", method)
       config = _build_pipeline_config(
           output=output, method=method, target_freq=target_freq,
           chunk_size=chunk_size, seed=seed,
           force_method=force_method,
           progress_callback=cb,
           frequency_resolver_callback=freq_cb,
       )
       from tempify.pipeline import TempifyPipeline   # LAZY
       result = TempifyPipeline(config).run(source)
4. render_summary(result)
5. if report:
       report.write_text(result.report.to_markdown(), encoding="utf-8")
6. raise typer.Exit(0)
```

Render con `rich.Table` para `inputs`, `outputs`, `validation`. Errores capturados y traducidos por `errors.handle()`.

**Complejidad:** O(1) overhead sobre el pipeline. La barra de progreso se actualiza a `progress_frequency_hz` (default 4 Hz, definido por el pipeline).

### Algoritmo `inspect`

Para no violar REQ-012, **no se importa `tempify.detection` directamente**. El subcomando construye `PipelineConfig(dry_run=True, skip_pre_validation=True, ...)` y ejecuta el pipeline. El campo `skip_pre_validation` está formalmente declarado en `specs/pipeline/design.md` § "PipelineConfig" (Decisión 7) y su invariante exige que solo pueda activarse junto con `dry_run=True`. Bajo este modo combinado, el pipeline omite tanto la interpolación, post-validation y escritura (por `dry_run`) como la pre-validation geoespacial y de compatibilidad método/variable (por `skip_pre_validation`), dejando solo `detect → generate_report` con outputs vacíos y `validation_pre=[]`. El CLI extrae `result.detection` del `PipelineResult` y lo renderiza.

```
config = _build_pipeline_config(..., dry_run=True, skip_pre_validation=True)
result = TempifyPipeline(config).run(source)
render_detection(result.detection)
exit(0)
```

**Trade-off considerado:** importar `tempify.detection` directamente sería más eficiente pero rompe la regla arquitectónica REQ-012. Se prefiere la ruta vía pipeline aunque agregue ~50ms de overhead (aún dentro de NFR-003 porque `inspect` no es el camino crítico de cold start). El test `test_cli_imports_only_pipeline` sigue siendo válido sin modificación: el CLI continúa importando exclusivamente `tempify.pipeline` (más `tempify.profiles`, `typer`, `rich`, stdlib).

### Algoritmo `validate`

```
config = _build_pipeline_config(..., dry_run=True)
result = TempifyPipeline(config).run(source)
render_validation(result.validation)
exit(0 if all_pass else 1)
```

### Algoritmo `profiles list`

```python
from tempify.profiles import iter_profiles  # carga vía importlib.resources
table = Table(...)
for profile in iter_profiles():
    table.add_row(profile.name, profile.units, ", ".join(profile.allowed_methods))
console.print(table)
```

`tempify.profiles` es paquete de datos (YAML + loader puro), no capa de dominio. Su import está permitido bajo REQ-012 porque no contiene lógica de detection/interpolation/io/validation.

### Algoritmo `version`

```python
import importlib.metadata as md
deps = ["tempify", "xarray", "dask", "rioxarray", "numpy", "scipy", "typer"]
for d in deps:
    console.print(f"{d:12s} {md.version(d)}")
```

**Sin imports de pipeline.** Cold start mínimo: solo `typer`, `rich`, `importlib.metadata`.

### SIGINT handler

```python
import signal, sys
def _sigint_handler(signum, frame):
    log.warning("Cancelación solicitada por el usuario.")
    # futuro: pipeline.cancel() cuando esté implementado
    cleanup_tmp_files()
    sys.exit(EXIT_CODES["SIGINT"])  # 130

signal.signal(signal.SIGINT, _sigint_handler)
```

Instalado en `app.py` al inicializar el módulo. Idempotente; no se reinstala por subcomando.

### Flujo `--force-method`

```
if force_method and not i_know:
    raise CliError("TFY-CLI-0011", "force_method_requires_flag")
if force_method:
    require_typed_confirmation(prompt=t("force_method_warning"), literal="si entiendo")
    log.warning("force_method=True override aplicado: variable=%s method=%s", var, method)
    config.force_method = True   # stamped por pipeline en attrs (ADR-0004)
```

La confirmación tipada **solo** acepta el string literal `si entiendo`. Cualquier otra respuesta levanta `UserCancelledError` (exit 2).

## 6. Decisiones de diseño

### Decisión 1: aislamiento estricto de imports (REQ-012)

**Opciones consideradas:**
1. Permitir imports de `tempify.detection` solo en `inspect` (atajo de performance).
2. Restringir todos los imports a `tempify.pipeline`, `tempify.profiles`, `typer`, `rich`, stdlib. Test AST que rompe el build si se viola.

**Decisión:** Opción 2.
**Razón:** la spec lo exige (REQ-012) y la regla arquitectónica dura nº 1 lo refuerza. El costo es ~50ms en `inspect`, aceptable. El beneficio es protección automática contra drift arquitectónico futuro.
**Trade-offs:** ligeramente más lento en `inspect` y `validate`; requiere que el pipeline ofrezca `skip_pre_validation` además de `dry_run` (contrato menor a coordinar con `specs/pipeline/`).

### Decisión 2: lazy imports de `tempify.pipeline`

**Opciones consideradas:**
1. Import top-level en `app.py`.
2. Import dentro de cada función-comando que lo necesita (`convert`, `inspect`, `validate`).

**Decisión:** Opción 2.
**Razón:** NFR-003 exige `<500ms` cold start. `xarray` + `dask` suman ~250ms; importarlos solo cuando se ejecuta `convert`/`inspect`/`validate` deja a `version` y `profiles list` por debajo de 200ms.
**Trade-offs:** los IDEs no descubren tan fácilmente la dependencia; se mitiga con un `__all__` explícito y un comentario `# noqa: lazy import`.

### Decisión 3: locale por defecto = español

**Opciones consideradas:**
1. Inglés por defecto (estándar industria).
2. Español por defecto, configurable vía `TEMPIFY_LANG=en`.

**Decisión:** Opción 2.
**Razón:** público objetivo declarado (CLAUDE.md, steering/product.md) es hispanohablante; los mensajes y prompts ya están escritos en español (REQ-003, REQ-011).
**Trade-offs:** usuarios anglo deben configurar env var; aceptable.

### Decisión 4: UTF-8 forzado

**Opciones consideradas:**
1. Asumir terminal correcta y dejar que falle con UnicodeEncodeError.
2. Verificar `PYTHONIOENCODING` o `sys.stdout.encoding` al startup y emitir warning + setear `errors="replace"` si no es UTF-8.

**Decisión:** Opción 2.
**Razón:** Windows defaultea a `cp1252` y corrompe acentos (riesgo identificado en requirements.md §7).
**Trade-offs:** un warning extra en consolas legacy; tolerable.

### Decisión 5: `typer` como framework (ya ADR-0003)

Sin re-decisión. Documentado en `docs/adr/0003-typer-vs-click-vs-argparse.md`.

### Decisión 6: catálogo de errores con prefijo `TFY-CLI-NNNN`

**Opciones consideradas:**
1. Códigos planos `TFY-NNNN` compartidos con pipeline.
2. Sub-namespaces por capa: `TFY-CLI-NNNN`, `TFY-PIPE-NNNN`, etc.

**Decisión:** Opción 2 dentro del catálogo único en `tempify.errors.codes` (single source of truth, requirements §7).
**Razón:** facilita triage; el namespace `TFY-CLI-*` reserva un rango para errores de presentación sin colisionar con códigos del pipeline.
**Trade-offs:** más prolijidad; mitigado por constantes nombradas.

## 7. Estrategia de testing

### Tests unitarios

Todos con `from typer.testing import CliRunner`. `CliRunner` provee un entorno simulado con `stdin`/`stdout` controlables y `isatty` configurable.

- `test_convert_basic` — REQ-001. Ejecuta `convert` con fixture pequeño, verifica exit 0 y output esperado.
- `test_progress_bar_shown` — REQ-002. Mockea `Rich Progress` y asserta que `_make_progress_callback` recibe ≥1 invocación por fase del pipeline.
- `test_interactive_prompt_for_frequency` — REQ-003. Stub que simula frequency_resolver callback y verifica que se invoca cuando `DetectionResult` no resuelve frecuencia.
- `test_non_tty_raises_interactive_required` — REQ-004. `CliRunner(stdin=...)` con `isatty=False` debe terminar con `InteractiveRequiredError` (exit 2) sin bloquearse.
- `test_report_flag_writes_markdown_conformant` — REQ-005 + NFR-001. Genera reporte, parsea Markdown, verifica que contiene las 9 secciones del schema canónico (`docs/schemas/processing-report.schema.md`).
- `test_exit_codes_canonical` — REQ-006. Parametrizado: PASS→0, validation FAIL→1, cancelación→2, internal→3, SIGINT→130.
- `test_inspect_runs_only_detection` — REQ-007. Mockea `TempifyPipeline.run` y verifica que `PipelineConfig` recibido tiene `dry_run=True` y `skip_pre_validation=True`.
- `test_validate_exits_1_on_error` — REQ-008. Fixture con CRS incoherente; verifica exit 1 y mensaje ES.
- `test_profiles_list_outputs` — REQ-009. Asserta que cada perfil del paquete aparece con nombre, unidades, métodos.
- `test_version_outputs` — REQ-010. Asserta presencia de `tempify`, `xarray`, `dask`, `rioxarray`, `numpy`, `scipy`.
- `test_force_method_requires_confirmation` — REQ-011. Tres escenarios: (a) sin `--i-know-what-i-am-doing` → exit 3 con TFY-CLI-0011, (b) flag presente pero confirmación distinta de `si entiendo` → exit 2, (c) confirmación correcta → propaga `force_method=True` al PipelineConfig.
- `test_cli_imports_only_pipeline` — REQ-012. Test AST: parsea todos los `.py` bajo `src/tempify/cli/`, recolecta imports, verifica que **no hay imports** que comiencen con `tempify.detection`, `tempify.io`, `tempify.interpolation`, `tempify.validation`. Permite `tempify.pipeline`, `tempify.profiles`, `tempify.errors`, stdlib, `typer`, `rich`, `importlib`.
- `test_sigint_exits_130` — REQ-013. Envía `SIGINT` durante ejecución simulada; verifica exit 130 y que `cleanup_tmp_files` fue invocado.
- `test_error_messages_spanish` — NFR-002. Parametrizado sobre catálogo: cada error contiene código `TFY-XXXX` y string en español.
- `test_cli_cold_start_under_500ms` — NFR-003. Mide `subprocess.run(["tempify", "version"])` 20 veces; p95 `<500ms`.
- `test_spanish_accents_render` — riesgo encoding Windows. Captura stdout y verifica que acentos no se corrompen.

### Tests property-based (hypothesis)

- No aplica. La CLI es determinista y sin invariantes algorítmicos; las propiedades viven en capas de dominio.

### Tests de integración

- `test_end_to_end_convert_small_fixture` — flujo completo `convert` → archivo NetCDF generado → reporte Markdown parseable.
- `test_end_to_end_inspect_then_convert` — pipeline humano: usuario inspecciona, luego convierte con los parámetros sugeridos.

### Fixtures necesarios

- `synthetic_3x3_monthly.nc` — ya existe (CLAUDE.md indica que vive en fixtures globales).
- `synthetic_3x3_monthly_with_unknown_freq.nc` — generar; sin metadata CF de tiempo, para forzar prompt interactivo.
- `synthetic_3x3_monthly_crs_incoherent.nc` — generar; dos archivos con CRS distintos, para `test_validate_exits_1_on_error`.
- `mock_pipeline.py` — stub de `TempifyPipeline` que devuelve `PipelineResult` controlados sin ejecutar interpolación real (acelera tests unitarios).

## 8. Plan de migración

No aplica. Esta es la primera versión de la CLI; no hay usuarios previos que migrar.

## 9. Métricas de calidad

| Métrica | Umbral |
|---|---|
| Coverage del módulo `tempify.cli` | ≥ 85% (NFR-004) |
| Cold start `tempify version` (p95, 20 ejecuciones) | < 500 ms (NFR-003) |
| Tiempo de respuesta `tempify profiles list` | < 600 ms |
| Tamaño del paquete `tempify.cli` (LOC sin tests) | < 1200 líneas |
| Cyclomatic complexity por función | ≤ 8 |

## 10. Trazabilidad requirements → design

| Requirement | Componente que lo implementa | Test |
|---|---|---|
| REQ-001 | `app` + `commands/{convert,inspect,validate,profiles,version}.py` | `test_convert_basic` |
| REQ-002 | `progress._make_progress_callback` + `commands/convert.py` | `test_progress_bar_shown` |
| REQ-003 | `interactive.prompt_frequency` + `frequency_resolver_callback` en `_build_pipeline_config` | `test_interactive_prompt_for_frequency` |
| REQ-004 | `interactive.require_tty` + `InteractiveRequiredError` en `errors.py` | `test_non_tty_raises_interactive_required` |
| REQ-005 | `commands/convert.py` (escritura de `result.report.to_markdown()`) | `test_report_flag_writes_markdown_conformant` |
| REQ-006 | `errors.EXIT_CODES` + mapeo `TempifyPipelineError → exit` | `test_exit_codes_canonical` |
| REQ-007 | `commands/inspect.py` (dry_run + skip_pre_validation) | `test_inspect_runs_only_detection` |
| REQ-008 | `commands/validate.py` (dry_run, exit según `ValidationReport`) | `test_validate_exits_1_on_error` |
| REQ-009 | `commands/profiles.py` (iter sobre `tempify.profiles.iter_profiles`) | `test_profiles_list_outputs` |
| REQ-010 | `commands/version.py` (importlib.metadata) | `test_version_outputs` |
| REQ-011 | `interactive.prompt_typed_confirmation` + `commands/convert.py` | `test_force_method_requires_confirmation` |
| REQ-012 | regla arquitectónica enforzada por test AST sobre `src/tempify/cli/` | `test_cli_imports_only_pipeline` |
| REQ-013 | SIGINT handler en `app.py` + `cleanup_tmp_files` | `test_sigint_exits_130` |
| NFR-001 | `commands/convert.py` (parse del `ProcessingReport` y serialización Markdown) | `test_report_flag_writes_markdown_conformant` |
| NFR-002 | `errors.py` + `i18n.py` (catálogo ES con códigos `TFY-XXXX`) | `test_error_messages_spanish` |
| NFR-003 | lazy imports + `commands/version.py` minimal | `test_cli_cold_start_under_500ms` |
| NFR-004 | suite completa de tests unitarios | reporte CI con `coverage.py` |
