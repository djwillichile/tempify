"""Regenera docs/assets/maipo_monthly_grid.jpg con cubic spline + fila de diff.

Layout 3 filas × 4 columnas:
- Fila 1: input mensual WorldClim (Ene/Abr/Jul/Oct)
- Fila 2: salida tempify (cubic) en el día 15 del mismo mes
- Fila 3: diff = anchor - predicción, con COLORBAR INDEPENDIENTE (diverging)
  porque las diferencias son varios órdenes de magnitud más pequeñas que
  la temperatura absoluta.

Cubic spline pasa exactamente por los nodos de midpoint, por lo que la diff
en el día ancla es esencialmente ruido float64 (~1e-14 °C), mostrando
visualmente que las anclas se conservan exactamente incluso con un método
no mean-preserving.
"""

from __future__ import annotations

import datetime as _dt
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rioxarray  # noqa: F401
import xarray as xr
from matplotlib.gridspec import GridSpec

from tempify.pipeline import PipelineConfig, TempifyPipeline

STACK_PATH = Path("examples/data/worldclim_maipo_alto/wc1_6_maipo_alto_tavg_stack.tif")
OUT_DIR = Path("examples/out/maipo_cubic")
ASSET_PATH = Path("docs/assets/maipo_monthly_grid.jpg")

SHOW_MONTHS = [1, 4, 7, 10]
MONTH_NAMES_ES = {1: "Enero", 4: "Abril", 7: "Julio", 10: "Octubre"}
CMAP_TEMP = "RdYlBu_r"
CMAP_DIFF = "RdBu_r"


def main() -> None:
    monthly = xr.load_dataarray(STACK_PATH)
    print(f"Monthly input: dims={monthly.dims}, shape={monthly.shape}")

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    cfg = PipelineConfig(
        method="cubic",
        target_year=2024,
        output_dir=OUT_DIR,
        output_format="netcdf",
    )
    result = TempifyPipeline(cfg).run(STACK_PATH)
    daily = xr.load_dataarray(result.outputs[0])
    print(f"Daily cubic: shape={daily.shape}")

    # Compute diffs first to get symmetric range for diverging colorbar
    diffs = []
    for month in SHOW_MONTHS:
        anchor = monthly.isel(band=month - 1).values
        doy_15 = _dt.date(2024, month, 15).timetuple().tm_yday - 1
        pred = daily.isel(time=doy_15).values
        diffs.append(anchor - pred)
    diffs_arr = np.stack(diffs)
    diff_abs_max = float(np.nanmax(np.abs(diffs_arr)))
    print(f"Max |diff| en celdas mostradas: {diff_abs_max:.3e} °C")

    # Use symmetric scale for the diverging colorbar
    diff_vmin = -diff_abs_max if diff_abs_max > 0 else -1e-15
    diff_vmax = diff_abs_max if diff_abs_max > 0 else 1e-15

    vmin = float(monthly.min())
    vmax = float(monthly.max())

    fig = plt.figure(figsize=(15, 10.5), dpi=110, layout="constrained")
    gs = GridSpec(
        3, 5, figure=fig,
        width_ratios=[1, 1, 1, 1, 0.04],
        hspace=0.18,
    )

    axes_in  = [fig.add_subplot(gs[0, c]) for c in range(4)]
    axes_out = [fig.add_subplot(gs[1, c], sharex=axes_in[c], sharey=axes_in[c]) for c in range(4)]
    axes_dif = [fig.add_subplot(gs[2, c], sharex=axes_in[c], sharey=axes_in[c]) for c in range(4)]
    cbar_temp_ax = fig.add_subplot(gs[0:2, -1])
    cbar_diff_ax = fig.add_subplot(gs[2, -1])

    im_temp = None
    im_diff = None
    for col, month in enumerate(SHOW_MONTHS):
        data_in = monthly.isel(band=month - 1).values
        doy_15 = _dt.date(2024, month, 15).timetuple().tm_yday - 1
        data_out = daily.isel(time=doy_15).values
        data_dif = data_in - data_out

        im_temp = axes_in[col].imshow(data_in, cmap=CMAP_TEMP, vmin=vmin, vmax=vmax, aspect="auto")
        axes_in[col].set_title(MONTH_NAMES_ES[month], fontsize=11,
                               fontweight="bold", color="#0d2854")
        axes_in[col].set_xticks([]); axes_in[col].set_yticks([])

        axes_out[col].imshow(data_out, cmap=CMAP_TEMP, vmin=vmin, vmax=vmax, aspect="auto")
        axes_out[col].set_xticks([]); axes_out[col].set_yticks([])

        im_diff = axes_dif[col].imshow(
            data_dif, cmap=CMAP_DIFF, vmin=diff_vmin, vmax=diff_vmax, aspect="auto"
        )
        axes_dif[col].set_xticks([]); axes_dif[col].set_yticks([])

    axes_in[0].set_ylabel(
        "WorldClim v2.1\n(entrada mensual)",
        fontsize=10, color="#1e3a8a", fontweight="bold", labelpad=8,
    )
    axes_out[0].set_ylabel(
        "tempify cubic\n(salida día 15)",
        fontsize=10, color="#065f46", fontweight="bold", labelpad=8,
    )
    axes_dif[0].set_ylabel(
        "Diferencia\n(ancla − predicción)",
        fontsize=10, color="#7c2d12", fontweight="bold", labelpad=8,
    )

    if im_temp is not None:
        fig.colorbar(im_temp, cax=cbar_temp_ax, label="Temperatura (°C)")
    if im_diff is not None:
        cb = fig.colorbar(im_diff, cax=cbar_diff_ax, label="Δ (°C)")
        # Format with scientific notation
        cb.formatter.set_powerlimits((-2, 2))
        cb.update_ticks()

    fig.suptitle(
        "Entrada mensual WorldClim vs salida diaria tempify (cubic spline) — anclas conservadas",
        fontsize=12, fontweight="bold", color="#0d2854",
    )

    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(ASSET_PATH, dpi=110, bbox_inches="tight", facecolor="white",
                pil_kwargs={"quality": 88})
    plt.close(fig)
    print(f"\nFigura guardada: {ASSET_PATH} ({ASSET_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
