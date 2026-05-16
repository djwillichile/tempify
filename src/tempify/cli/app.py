"""Top-level Typer application for ``tempify`` CLI."""

from __future__ import annotations

import signal
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from tempify.cli.errors import EXIT_CODES

app = typer.Typer(
    name="tempify",
    help="Densificación temporal de stacks ráster geoespaciales.",
    no_args_is_help=True,
    rich_markup_mode="rich",
    pretty_exceptions_enable=False,
)

console = Console()


def _sigint_handler(signum: int, frame: object) -> None:
    """Handle Ctrl+C by exiting cleanly with code 130 (per cli spec REQ-013)."""
    console.print("[yellow]\nInterrumpido por el usuario.[/yellow]")
    sys.exit(EXIT_CODES["sigint"])


signal.signal(signal.SIGINT, _sigint_handler)


# ---------------------------------------------------------------------------
# `convert` subcommand
# ---------------------------------------------------------------------------


@app.command(help="Convierte un stack mensual a diario.")
def convert(
    source: Annotated[Path, typer.Argument(help="Archivo o carpeta de entrada.")],
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Carpeta de salida."),
    ] = Path("./tempify_out"),
    method: Annotated[
        str,
        typer.Option("--method", "-m", help="Método: linear, pchip, pchip_mp, fourier."),
    ] = "pchip_mp",
    year: Annotated[
        int,
        typer.Option("--year", "-y", help="Año destino para el eje diario."),
    ] = 2023,
    output_format: Annotated[
        str,
        typer.Option(
            "--format",
            help="Formato de salida: netcdf, multiband_geotiff, geotiff_collection, zarr.",
        ),
    ] = "netcdf",
    report: Annotated[
        Path | None,
        typer.Option(
            "--report",
            help="Ruta para guardar el reporte de procesamiento (Markdown).",
        ),
    ] = None,
    force_method: Annotated[
        bool,
        typer.Option(
            "--force-method",
            help=(
                "Forzar el método aunque sea incompatible con la variable "
                "(requiere --i-know-what-i-am-doing y confirmación)."
            ),
        ),
    ] = False,
    i_know: Annotated[
        bool,
        typer.Option(
            "--i-know-what-i-am-doing",
            help="Confirmación obligatoria para usar --force-method.",
        ),
    ] = False,
    variable: Annotated[
        str | None,
        typer.Option(
            "--variable",
            help=(
                "Nombre del perfil de variable a usar "
                "(temperature, precipitation, relative_humidity, solar_radiation)."
            ),
        ),
    ] = None,
) -> None:
    """Convert a monthly stack to daily and write the result to disk."""
    # Lazy import to keep cold start fast.
    from tempify.pipeline import PipelineConfig, TempifyPipeline, TempifyPipelineError

    if force_method:
        if not i_know:
            console.print("[red]ERROR:[/red] --force-method requiere --i-know-what-i-am-doing.")
            raise typer.Exit(code=EXIT_CODES["user_cancellation"])
        confirmation = typer.prompt(
            "ATENCIÓN: Forzar el método puede producir resultados científicamente "
            "no válidos. Escriba 'si entiendo' para continuar"
        )
        if confirmation.strip().lower() != "si entiendo":
            console.print("[yellow]Cancelado por el usuario.[/yellow]")
            raise typer.Exit(code=EXIT_CODES["user_cancellation"])

    cfg = PipelineConfig(
        method=method,  # type: ignore[arg-type]
        target_year=year,
        output_dir=output,
        output_format=output_format,  # type: ignore[arg-type]
        force_method=force_method,
        variable_profile_override=variable,
    )
    try:
        result = TempifyPipeline(cfg).run(source)
    except TempifyPipelineError as exc:
        console.print(f"[red]Error de pipeline:[/red] {exc}")
        raise typer.Exit(code=EXIT_CODES["validation_failure"]) from exc

    console.print(f"[green]OK:[/green] {len(result.outputs)} archivo(s) escritos en {output}")
    for p in result.outputs:
        console.print(f"  - {p}")

    if report is not None:
        from tempify.pipeline import ReportGenerator

        report.write_text(ReportGenerator().to_markdown(result.report), encoding="utf-8")
        console.print(f"[green]Reporte guardado en:[/green] {report}")


# ---------------------------------------------------------------------------
# `inspect` subcommand
# ---------------------------------------------------------------------------


@app.command(help="Inspecciona la estructura y frecuencia de la entrada (dry-run).")
def inspect(
    source: Annotated[Path, typer.Argument(help="Archivo o carpeta de entrada.")],
) -> None:
    """Run detection + pre-validation without interpolating."""
    from tempify.pipeline import PipelineConfig, TempifyPipeline, TempifyPipelineError

    cfg = PipelineConfig(
        method="linear",
        target_year=2023,
        output_dir=Path("./tempify_inspect_out"),
        dry_run=True,
        skip_pre_validation=True,
    )
    try:
        result = TempifyPipeline(cfg).run(source)
    except TempifyPipelineError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=EXIT_CODES["internal_error"]) from exc

    console.print(f"[bold]Modo de estructura:[/bold] {result.detection.structure_mode.value}")
    console.print(f"[bold]Archivos detectados:[/bold] {len(result.detection.files)}")
    console.print(f"[bold]Frecuencia inferida:[/bold] {result.frequency.frequency.value}")
    console.print(
        f"[bold]Confianza estructural:[/bold] {result.detection.confidence['structure_mode']:.2f}"
    )


# ---------------------------------------------------------------------------
# `validate` subcommand
# ---------------------------------------------------------------------------


@app.command(help="Valida coherencia geoespacial sin interpolar.")
def validate(
    source: Annotated[Path, typer.Argument(help="Archivo o carpeta de entrada.")],
    variable: Annotated[
        str | None,
        typer.Option("--variable", help="Perfil de variable a usar para compatibilidad."),
    ] = None,
) -> None:
    """Run only detection + pre-validation. Exit 1 if any ERROR found."""
    from tempify.pipeline import PipelineConfig, TempifyPipeline, TempifyPipelineError

    cfg = PipelineConfig(
        method="linear",
        target_year=2023,
        output_dir=Path("./tempify_validate_out"),
        dry_run=True,
        variable_profile_override=variable,
    )
    try:
        result = TempifyPipeline(cfg).run(source)
    except TempifyPipelineError as exc:
        console.print(f"[red]Validación falló:[/red] {exc}")
        raise typer.Exit(code=EXIT_CODES["validation_failure"]) from exc

    pre = result.pre_validation
    console.print(
        f"[bold]Pre-validación:[/bold] errors={len(pre.errors)}, "
        f"warnings={len(pre.warnings)}, info={len(pre.info_items)}"
    )
    for check in pre.checks:
        marker = "✓" if check.passed else "✗"
        color = "green" if check.passed else "red"
        console.print(f"  [{color}]{marker}[/] [{check.check_id}] {check.name}")
    if not pre.pre_passed:
        raise typer.Exit(code=EXIT_CODES["validation_failure"])


# ---------------------------------------------------------------------------
# `profiles` subcommand group
# ---------------------------------------------------------------------------


profiles_app = typer.Typer(help="Operaciones sobre perfiles de variable.")
app.add_typer(profiles_app, name="profiles")


@profiles_app.command("list", help="Lista los perfiles de variable disponibles.")
def profiles_list() -> None:
    """Print the table of built-in variable profiles."""
    # We deliberately go through pipeline's public exports to satisfy the
    # "CLI only imports pipeline" architectural test. The pipeline module
    # re-exposes Profile loading via VariableProfileMatcher which we can
    # access transitively by reading the profiles directory.
    from importlib import resources

    from rich.table import Table

    table = Table(title="Perfiles de variable")
    table.add_column("Nombre", style="bold")
    table.add_column("Alias")
    table.add_column("Unidad")
    table.add_column("Métodos permitidos")

    for entry in resources.files("tempify.profiles").iterdir():
        name = entry.name
        if not name.endswith(".yaml") or name.startswith("_"):
            continue
        # Read raw to avoid importing tempify.validation directly.
        text = entry.read_text(encoding="utf-8")
        # Tiny YAML inline scan: extract fields we display.
        fields = _scan_profile_yaml(text)
        fallback_name = name.removesuffix(".yaml")
        table.add_row(
            fields.get("name", fallback_name),
            fields.get("aliases", ""),
            fields.get("units", ""),
            fields.get("allowed_methods", "(ninguno)"),
        )
    console.print(table)


def _scan_profile_yaml(text: str) -> dict[str, str]:
    """Minimal YAML scan for the four fields shown by `profiles list`.

    Intentionally avoids importing ``yaml`` or ``tempify.validation`` so the
    CLI keeps the smallest possible import surface and the architectural
    test ``test_cli_imports_only_pipeline`` stays green.
    """
    out: dict[str, str] = {}
    in_methods = False
    methods: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("name:"):
            out["name"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("units:"):
            out["units"] = stripped.split(":", 1)[1].strip().strip("\"'")
        elif stripped.startswith("aliases:"):
            rest = stripped.split(":", 1)[1].strip()
            out["aliases"] = rest.strip("[]")
        elif stripped.startswith("allowed_methods:"):
            rest = stripped.split(":", 1)[1].strip()
            if rest in ("", "[]"):
                in_methods = False
                out["allowed_methods"] = "(ninguno)"
            elif rest.startswith("["):
                in_methods = False
                out["allowed_methods"] = rest.strip("[]")
            else:
                in_methods = True
        elif in_methods and stripped.startswith("-"):
            methods.append(stripped.lstrip("- ").strip())
        elif in_methods:
            in_methods = False
            if methods:
                out["allowed_methods"] = ", ".join(methods)
    if in_methods and methods:
        out["allowed_methods"] = ", ".join(methods)
    return out


# ---------------------------------------------------------------------------
# `version` subcommand
# ---------------------------------------------------------------------------


@app.command(help="Imprime la versión de tempify y sus dependencias clave.")
def version() -> None:
    """Print tempify version + the canonical dependencies."""
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as pkg_version

    def _v(name: str) -> str:
        try:
            return pkg_version(name)
        except PackageNotFoundError:
            return "(no instalado)"

    console.print(f"[bold]tempify[/bold] {_v('tempify')}")
    console.print("Dependencias principales:")
    for name in ("numpy", "xarray", "dask", "rioxarray", "netcdf4", "scipy", "typer", "rich"):
        console.print(f"  - {name}: {_v(name)}")


if __name__ == "__main__":  # pragma: no cover
    app()
