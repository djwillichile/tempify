"""Benchmark: max |diff| per method on the WorldClim Chile Central sample.

Computes the worst pixel-wise discrepancy between the monthly mean
reconstructed from the daily output and the original monthly input,
for the six interpolation methods available in tempify.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import xarray as xr

from tempify.pipeline import PipelineConfig, TempifyPipeline

DATA_DIR = Path(__file__).parent / "data" / "worldclim_chile_central"
OUT_ROOT = Path(__file__).parent / "out" / "bench_max_diff"
METHODS = ["linear", "pchip", "pchip_mp", "fourier", "akima", "cubic"]


def _aggregate_to_monthly(daily: xr.DataArray) -> xr.DataArray:
    return daily.groupby(daily["time"].dt.month).mean(dim="time")


def _load_monthly_input() -> xr.DataArray:
    import rioxarray  # noqa: F401
    arrays = []
    for month in range(1, 13):
        path = DATA_DIR / f"wc2.1_2.5m_tavg_{month:02d}.tif"
        arrays.append(
            xr.open_dataarray(path, engine="rasterio").squeeze("band", drop=True)
        )
    return xr.concat(arrays, dim="month").assign_coords(month=list(range(1, 13)))


def _run(method: str) -> float:
    out_dir = OUT_ROOT / method
    if out_dir.exists():
        shutil.rmtree(out_dir)
    cfg = PipelineConfig(
        method=method,
        target_year=2023,
        output_dir=out_dir,
        output_format="netcdf",
    )
    result = TempifyPipeline(cfg).run(DATA_DIR)
    daily = xr.open_dataarray(result.outputs[0])
    monthly_input = _load_monthly_input()
    monthly_recon = _aggregate_to_monthly(daily).transpose("month", "y", "x")
    return float(np.max(np.abs(monthly_recon.values - monthly_input.values)))


def main() -> None:
    print(f"{'method':<10}  {'max |diff| (°C)':<22}  scientific")
    print("-" * 60)
    for m in METHODS:
        d = _run(m)
        mantissa = d / 10 ** np.floor(np.log10(d)) if d > 0 else 0.0
        exponent = int(np.floor(np.log10(d))) if d > 0 else 0
        print(f"{m:<10}  {d:<22.6e}  {mantissa:.2f} × 10^{exponent}")


if __name__ == "__main__":
    main()
