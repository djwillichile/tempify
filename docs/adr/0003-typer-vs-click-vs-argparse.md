# ADR-0003: Typer vs Click vs argparse

**Status:** Accepted
**Date:** 2026-05-16
**Decision-makers:** Guillermo Fuentes-Jaque

## Contexto

La Capa 6 (`tempify.cli`) requiere una interfaz humana con cinco subcomandos (`convert`, `inspect`, `validate`, `profiles`, `version`), prompts interactivos en español para resolver ambigüedades (frecuencia temporal desconocida, perfil de variable no detectado), progress bars y tablas formateadas con `rich`, mensajes y `--help` localizables, exit codes diferenciados (0/1/2/3 según `specs/cli/requirements.md` REQ-006) y facilidad de testeo automatizado.

Restricciones adicionales:

- Python 3.11+ con type hints obligatorios y `mypy --strict` (ver `steering/tech.md`).
- El entry point ya está fijado en `pyproject.toml`: `tempify = "tempify.cli:app"`. El nombre `app` es idiomático en Typer (instancia `typer.Typer()`).
- La CLI no debe contener lógica de negocio; solo orquestar llamadas al pipeline (regla arquitectónica de `steering/architecture.md`).
- Se busca minimizar boilerplate para preservar legibilidad de los comandos.

Candidatos evaluados en el ecosistema Python:

1. **argparse** (biblioteca estándar)
2. **Click** (Pallets Projects)
3. **Typer** (tiangolo, basado en Click)
4. **Fire** (Google)

## Decisión

Adoptar **Typer (>= 0.12)** como framework de CLI, con **Rich (>= 13.7)** para presentación (progress bars, tablas, color, syntax highlighting de errores).

## Justificación

### Pros de Typer

- **Type-hints-first.** La firma de la función define el contrato del comando; las anotaciones se traducen automáticamente a opciones/argumentos validados. Alineado con la política `mypy --strict` del proyecto.
- **Construido sobre Click.** Hereda la madurez de Click (parsing robusto, manejo de TTY, callbacks, grupos de comandos) sin pagar su boilerplate decorativo.
- **Integración nativa con Rich.** `typer.Typer(rich_markup_mode="rich")` activa renderizado de markup y tracebacks formateados sin código adicional. Cumple REQ-002 (progress bar) y NFR-002 (mensajes legibles).
- **Subcomandos limpios.** `@app.command()` sobre funciones tipadas produce los cinco subcomandos requeridos sin árbol manual de parsers.
- **Testing ergonómico.** `typer.testing.CliRunner` invoca comandos in-process, captura stdout/stderr y exit codes; encaja con la cobertura >= 85% exigida por los guardrails.
- **Detección de TTY.** Permite cumplir REQ-004 (fallar con `InteractiveRequiredError` cuando no hay TTY) usando `typer.prompt` + `sys.stdin.isatty()`.
- **IDE-friendly.** Autocompletado y refactor seguros sobre los parámetros del comando.

### Cons de Typer

- **Versión < 1.0.** API aún puede evolucionar. Mitigado con pin `>= 0.12` y revisión en cada bump.
- **Dependencia transitiva sobre Click.** Mayor superficie de actualización, pero ya estable.
- **Curva de aprendizaje para contribuidores acostumbrados a argparse.**

### Por qué no las alternativas

- **argparse (stdlib).** Verboso para cinco subcomandos; requiere construir subparsers a mano, mapear tipos manualmente y validar enums con `choices=[...]`. Sin integración nativa con Rich (los progress bars y tablas se acoplan ad-hoc). Sin type-hints como contrato. Aumenta el boilerplate y degrada la trazabilidad del contrato comando-función.
- **Click.** Maduro, ecosistema amplio y subcomandos elegantes vía `@click.group` + `@click.command`. Sin embargo, no es type-hints-first: cada opción se declara con un decorador `@click.option(..., type=...)` redundante con la firma. Mayor fricción contra `mypy --strict` y más ruido visual en módulos con muchos comandos.
- **Fire (Google).** Convierte cualquier objeto Python en CLI por reflexión. Mágico, sin contrato explícito de opciones, dificulta documentar y testear; no es apto para una CLI productiva con prompts interactivos, exit codes diferenciados y mensajes localizados.

## Consecuencias

### Positivas

- Boilerplate mínimo: cada subcomando es una función tipada con docstring; el `--help` se genera desde las anotaciones y el docstring.
- Tests deterministas vía `CliRunner` (sin subprocess), facilita alcanzar cobertura del módulo CLI.
- Output consistente con el resto del ecosistema científico-Python que ya usa Rich (xarray, dask).
- Refactors seguros: cambiar la firma de un comando rompe el typecheck antes de runtime.

### Negativas

- Dependencia obligatoria adicional (`typer`, que arrastra `click`).
- Cambios mayores en Typer < 1.0 podrían requerir migración; se compensa con pin de versión y CI en matriz Python 3.11/3.12/3.13.
- Los contribuidores deben aprender el modelo de `Annotated[T, typer.Option(...)]` para opciones avanzadas.

### Riesgos

- **Estabilidad pre-1.0.** Mitigado fijando `typer >= 0.12, < 1.0` y revisando el changelog en cada upgrade.
- **Acoplamiento con Rich.** Si Rich introduce breaking changes en formateo, los snapshots de tests podrían romperse; mitigado con pin `rich >= 13.7` y assertions sobre contenido, no sobre escapes ANSI.

## Notas de implementación

- **Entry point.** `pyproject.toml` declara `tempify = "tempify.cli:app"`, donde `app = typer.Typer(help="tempify — densificación temporal de stacks ráster")`.
- **Estructura modular.** Un módulo por subcomando bajo `tempify/cli/commands/` (`convert.py`, `inspect.py`, `validate.py`, `profiles.py`, `version.py`); cada uno registra su comando contra `app` o un sub-`Typer()`.
- **Localización.** Mensajes y `--help` en español por defecto. Activar inglés vía variable de entorno `TEMPIFY_LANG=en` (mecanismo concreto a fijar en la spec CLI, no en este ADR).
- **Exit codes.** Usar `raise typer.Exit(code=N)` con la tabla de REQ-006 (0 éxito, 1 validación fallida, 2 cancelación de usuario, 3 error interno).
- **Prompts interactivos.** `typer.prompt(...)` envuelto en un helper que valida TTY (`sys.stdin.isatty()`) y lanza `InteractiveRequiredError` en su ausencia (REQ-004).
- **Progress bars.** `rich.progress.Progress` instanciado desde el comando `convert`, pasado al pipeline mediante un callback opaco para no acoplar la Capa 5 a Rich.
- **Errores tipados.** Excepciones del dominio se mapean a códigos de error referenciables (`E001-...`) en un handler global registrado vía `app.callback`.
- **Tests.** `pytest` con `typer.testing.CliRunner`. Fixtures producen `xr.DataArray` sintéticos; los snapshots de stdout se normalizan eliminando ANSI cuando corresponde.
- **Documentación.** `--help` autogenerado se publica como página de Sphinx vía `sphinx-click` (compatible con Typer dado que comparte runtime con Click).

## Referencias

- Typer: https://typer.tiangolo.com/
- Click: https://click.palletsprojects.com/
- Rich: https://rich.readthedocs.io/
- argparse: https://docs.python.org/3/library/argparse.html
- ADR-0001 (xarray como abstracción central): `docs/adr/0001-use-xarray-as-central-abstraction.md`
- Spec CLI: `specs/cli/requirements.md`
- Arquitectura, Capa 6: `steering/architecture.md`
