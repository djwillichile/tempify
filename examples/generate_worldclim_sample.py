"""Generate a small WorldClim-like sample (Chile Central).

This script produces 12 GeoTIFFs with the WorldClim v2.1 naming convention
(``wc2.1_2.5m_tavg_NN.tif``) over a small bounding box covering roughly
the Metropolitan Region of Santiago, Chile. Values are synthesised from
the real monthly mean temperature climatology for the area (~21 degC in
summer, ~9 degC in winter) plus a small spatial gradient simulating
altitude.

Why synthetic? The real WorldClim global product weights several MB per
file and requires internet to download. This sample stays under 100 KB
total while keeping the temporal pattern realistic enough to validate
that tempify preserves the monthly mean and produces a smooth daily
signal.

Run:
    python examples/generate_worldclim_sample.py [--output ./data]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import rioxarray  # noqa: F401 - registers the rio accessor
import xarray as xr

# Monthly mean temperature (degC) for Santiago, Chile (rounded climatology).
SANTIAGO_MONTHLY_TAVG: tuple[float, ...] = (
    21.0,  # Jan
    20.0,  # Feb
    18.0,  # Mar
    15.0,  # Apr
    12.0,  # May
    9.0,  # Jun
    9.0,  # Jul
    10.0,  # Aug
    12.0,  # Sep
    14.0,  # Oct
    17.0,  # Nov
    20.0,  # Dec
)

# Bounding box approximating the Metropolitan Region (lon_min, lat_min,
# lon_max, lat_max). 30x30 pixels at ~2.5min resolution covers the area.
BBOX_LON: tuple[float, float] = (-71.5, -69.5)
BBOX_LAT: tuple[float, float] = (-34.5, -32.5)
N_PIXELS: int = 30


def _build_field(month_idx: int, base_value: float) -> np.ndarray:
    """Build a 30x30 raster: base value + altitude-driven cooling toward east."""
    rng = np.random.default_rng(month_idx)
    lon = np.linspace(BBOX_LON[0], BBOX_LON[1], N_PIXELS)
    lat = np.linspace(BBOX_LAT[0], BBOX_LAT[1], N_PIXELS)
    lon_grid, _ = np.meshgrid(lon, lat)
    # Altitude proxy: cooler toward east (Andes). Linear gradient ~6 degC.
    altitude_effect = -6.0 * (lon_grid - BBOX_LON[0]) / (BBOX_LON[1] - BBOX_LON[0])
    noise = rng.normal(scale=0.2, size=(N_PIXELS, N_PIXELS))
    field = base_value + altitude_effect + noise
    return field.astype(np.float32)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a WorldClim-like sample.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / "data" / "worldclim_chile_central",
        help="Output directory (default: examples/data/worldclim_chile_central/).",
    )
    args = parser.parse_args()

    out_dir = args.output
    out_dir.mkdir(parents=True, exist_ok=True)

    lon = np.linspace(BBOX_LON[0], BBOX_LON[1], N_PIXELS)
    lat = np.linspace(BBOX_LAT[1], BBOX_LAT[0], N_PIXELS)  # north -> south

    for month_idx, base in enumerate(SANTIAGO_MONTHLY_TAVG):
        arr = _build_field(month_idx, base)
        da = xr.DataArray(
            arr,
            dims=("y", "x"),
            coords={"y": lat, "x": lon},
            name="tavg",
        ).rio.write_crs("EPSG:4326")
        path = out_dir / f"wc2.1_2.5m_tavg_{month_idx + 1:02d}.tif"
        da.rio.to_raster(path)
        print(f"  wrote {path.name} (mean={float(arr.mean()):.2f} degC)")
    print(f"OK: 12 GeoTIFFs en {out_dir}")


if __name__ == "__main__":
    main()
