"""Regenera docs/assets/maipo_pixel_timeseries.jpg desde el notebook 02.

Replica exactamente las celdas 5 + 9 + 16 del notebook 02-real-worldclim-maipo.ipynb,
ejecutando el pipeline pchip_mp sobre WorldClim Alto Maipo y guardando la figura
del ciclo anual reconstruido.
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

from tempify.pipeline import PipelineConfig, TempifyPipeline

STACK_PATH = Path("examples/data/worldclim_maipo_alto/wc1_6_maipo_alto_tavg_stack.tif")
OUT_DIR = Path("examples/out/maipo_pchip_mp")
ASSET_PATH = Path("docs/assets/maipo_pixel_timeseries.jpg")


def main() -> None:
    monthly = xr.load_dataarray(STACK_PATH)
    print(f"Monthly: dims={monthly.dims}, shape={monthly.shape}")

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    cfg = PipelineConfig(
        method="pchip_mp",
        target_year=2024,
        output_dir=OUT_DIR,
        output_format="netcdf",
    )
    result = TempifyPipeline(cfg).run(STACK_PATH)
    daily = xr.load_dataarray(result.outputs[0])
    print(f"Daily: shape={daily.shape}, dims={daily.dims}")

    # Localizar pixel mas frio (cordillera) y mas calido (valle) en mes de enero
    # (mismo criterio que el notebook).
    jan = daily.isel(time=14).values
    iy_cold, ix_cold = np.unravel_index(np.nanargmin(jan), jan.shape)
    iy_warm, ix_warm = np.unravel_index(np.nanargmax(jan), jan.shape)

    series_cold = daily.isel(y=iy_cold, x=ix_cold).values
    series_warm = daily.isel(y=iy_warm, x=ix_warm).values
    assert not np.isnan(series_cold).any()
    assert not np.isnan(series_warm).any()

    month_doy = [int(_dt.date(2024, m, 15).timetuple().tm_yday) for m in range(1, 13)]
    month_cold = monthly.isel(band=slice(0, 12), y=iy_cold, x=ix_cold).values
    month_warm = monthly.isel(band=slice(0, 12), y=iy_warm, x=ix_warm).values

    print(f"Pixel cordillera: y={iy_cold}, x={ix_cold}  T_ene={jan[iy_cold, ix_cold]:.1f} degC")
    print(f"Pixel valle:      y={iy_warm}, x={ix_warm}  T_ene={jan[iy_warm, ix_warm]:.1f} degC")

    fig, ax = plt.subplots(figsize=(12, 4.6), dpi=110)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f6faf8")
    doy_all = np.arange(1, daily.sizes["time"] + 1)
    ax.plot(doy_all, series_warm, color="#dc2626", linewidth=2.0,
            label=f"Valle (y={iy_warm}, x={ix_warm})", zorder=3)
    ax.plot(doy_all, series_cold, color="#1d4ed8", linewidth=2.0,
            label=f"Alta cordillera (y={iy_cold}, x={ix_cold})", zorder=3)
    ax.scatter(month_doy, month_warm, color="#7f1d1d", s=40,
               edgecolors="white", linewidth=1.2, zorder=4, label="Nodo mensual valle")
    ax.scatter(month_doy, month_cold, color="#1e3a8a", s=40,
               edgecolors="white", linewidth=1.2, zorder=4, label="Nodo mensual cordillera")
    ax.set_xlim(0, daily.sizes["time"] + 1)
    ax.set_xticks([int(_dt.date(2024, m, 15).timetuple().tm_yday) for m in range(1, 13)])
    ax.set_xticklabels(["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                        "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"], fontsize=9)
    ax.axhline(0, color="#94a3b8", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_ylabel("Temperatura (degC)", color="#4a5b6b", fontsize=10)
    ax.set_title(
        "Ciclo anual reconstruido — Alta cordillera vs valle (pchip_mp sobre WorldClim Alto Maipo)",
        color="#0d2854", fontsize=12, fontweight="bold", pad=12, loc="left",
    )
    ax.grid(True, alpha=0.18, linewidth=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper center", framealpha=0.95, fontsize=9,
              edgecolor="#0d2854", ncol=2)
    plt.tight_layout()
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(ASSET_PATH, dpi=110, bbox_inches="tight", facecolor="white",
                pil_kwargs={"quality": 88})
    plt.close(fig)
    print(f"\nFigura guardada: {ASSET_PATH} ({ASSET_PATH.stat().st_size // 1024} KB)")
    print(f"Amplitud termica valle:      {series_warm.max() - series_warm.min():.1f} degC")
    print(f"Amplitud termica cordillera: {series_cold.max() - series_cold.min():.1f} degC")
    print(f"Offset valle vs cordillera:  {series_warm.mean() - series_cold.mean():.1f} degC")


if __name__ == "__main__":
    main()
