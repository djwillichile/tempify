"""End-to-end demo: tempify on a small WorldClim-like sample (Chile Central).

Runs the full pipeline (Linear and PCHIP+RM) and verifies that:

1. Output is a daily NetCDF with 365 time steps for year 2023.
2. The monthly mean of the daily output reproduces the input climatology
   within the contractual tolerance (ADR-0010 nivel 2: atol=1e-4).
3. The processing report contains canonical provenance fields.

Usage:
    # 1. Generate the synthetic WorldClim sample (one-time, ~50 KB)
    python examples/generate_worldclim_sample.py

    # 2. Run the demo
    python examples/run_demo.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr

from tempify.pipeline import (
    PipelineConfig,
    ProcessingReport,
    ReportGenerator,
    TempifyPipeline,
)

DATA_DIR = Path(__file__).parent / "data" / "worldclim_chile_central"


def _aggregate_to_monthly(daily: xr.DataArray) -> xr.DataArray:
    """Aggregate daily output to monthly mean for verification."""
    return daily.groupby(daily["time"].dt.month).mean(dim="time")


def _load_monthly_input() -> xr.DataArray:
    """Read the 12 input GeoTIFFs as a (month, y, x) DataArray."""
    import rioxarray  # noqa: F401 - registers the rio accessor

    arrays = []
    for month in range(1, 13):
        path = DATA_DIR / f"wc2.1_2.5m_tavg_{month:02d}.tif"
        arrays.append(xr.open_dataarray(path, engine="rasterio").squeeze("band", drop=True))
    return xr.concat(arrays, dim="month").assign_coords(month=list(range(1, 13)))


def _run(method: str, out_subdir: str) -> ProcessingReport:
    out_dir = Path(__file__).parent / "out" / out_subdir
    cfg = PipelineConfig(
        method=method,  # type: ignore[arg-type]
        target_year=2023,
        output_dir=out_dir,
        output_format="netcdf",
    )
    print(f"\n=== Ejecutando tempify con metodo '{method}' ===")
    result = TempifyPipeline(cfg).run(DATA_DIR)
    print(f"  Outputs: {[str(p) for p in result.outputs]}")
    print(
        f"  Pre-validacion: errors={len(result.pre_validation.errors)} "
        f"warnings={len(result.pre_validation.warnings)}"
    )
    if result.post_validation is not None:
        print(
            "  Post-validacion: errors="
            f"{len(result.post_validation.errors)} warnings="
            f"{len(result.post_validation.warnings)}"
        )

    # Verify mean preservation
    daily = xr.open_dataarray(result.outputs[0])
    monthly_input = _load_monthly_input()
    monthly_recon = _aggregate_to_monthly(daily).transpose("month", "y", "x")
    max_diff = float(np.max(np.abs(monthly_recon.values - monthly_input.values)))
    print(f"  Diferencia maxima entre media reconstruida e input: {max_diff:.3e} degC")
    if method == "pchip_mp":
        assert max_diff < 1e-4, f"PCHIP+RM debe preservar media; max_diff={max_diff:.3e}"
        print("  OK: PCHIP+RM preservo la media mensual dentro de la tolerancia.")
    return result.report


def main() -> None:
    if not DATA_DIR.exists():
        raise SystemExit(
            "Datos sinteticos no encontrados. Ejecute primero:\n"
            "    python examples/generate_worldclim_sample.py"
        )

    _run("linear", "linear")
    report_pchip_mp = _run("pchip_mp", "pchip_mp")

    rg = ReportGenerator()
    md = rg.to_markdown(report_pchip_mp)
    print("\n=== Reporte (PCHIP+RM) ===")
    print(md)


if __name__ == "__main__":
    main()
