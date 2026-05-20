"""Funciones auxiliares para generar y cargar datos sintéticos tipo WorldClim.

Proporciona datasets reproducibles para demos, notebooks y tests. Los outputs
usan la convención de nombres WorldClim v2.1 para que el pipeline de tempify
los lea directamente sin configuración adicional.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import rioxarray  # noqa: F401 — registra el accessor rio
import xarray as xr

SANTIAGO_MONTHLY_TAVG: tuple[float, ...] = (
    21.0,  # Ene
    20.0,  # Feb
    18.0,  # Mar
    15.0,  # Abr
    12.0,  # May
    9.0,   # Jun
    9.0,   # Jul
    10.0,  # Ago
    12.0,  # Sep
    14.0,  # Oct
    17.0,  # Nov
    20.0,  # Dic
)

_FILENAME_TEMPLATE = "wc2.1_2.5m_{variable}_{month:02d}.tif"


def _gaussian_cluster(
    lon_grid: np.ndarray,
    lat_grid: np.ndarray,
    lon0: float,
    lat0: float,
    sx: float,
    sy: float,
    amplitude: float,
) -> np.ndarray:
    return amplitude * np.exp(
        -((lon_grid - lon0) ** 2 / (2 * sx**2) + (lat_grid - lat0) ** 2 / (2 * sy**2))
    )


def _smooth_noise(
    shape: tuple[int, int],
    seed: int,
    n_iter: int = 18,
    scale: float = 1.0,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    arr = rng.normal(0, 1, size=shape).astype(np.float64)
    for _ in range(n_iter):
        arr = (
            arr
            + np.roll(arr, 1, axis=0)
            + np.roll(arr, -1, axis=0)
            + np.roll(arr, 1, axis=1)
            + np.roll(arr, -1, axis=1)
        ) / 5.0
    return arr * scale


def _build_spatial_temperature_field(
    month_idx: int,
    base_value: float,
    lon_grid: np.ndarray,
    lat_grid: np.ndarray,
    bbox_lon: tuple[float, float],
    bbox_lat: tuple[float, float],
    seed: int,
) -> np.ndarray:
    n_pixels = lon_grid.shape[0]

    altitude_effect = -6.0 * (lon_grid - bbox_lon[0]) / (bbox_lon[1] - bbox_lon[0])
    lat_effect = -0.5 * (lat_grid - bbox_lat[0]) / (bbox_lat[1] - bbox_lat[0])

    phase = month_idx / 12.0
    cluster_amp = 1.5 * np.sin(2 * np.pi * phase + np.pi / 4)
    warm_cluster = _gaussian_cluster(
        lon_grid, lat_grid,
        bbox_lon[0] + 0.3, bbox_lat[0] + 0.3, 0.3, 0.25, cluster_amp,
    )
    cold_cluster = _gaussian_cluster(
        lon_grid, lat_grid,
        bbox_lon[1] - 0.4, bbox_lat[1] - 0.3, 0.35, 0.3, -cluster_amp,
    )

    texture = _smooth_noise(
        (n_pixels, n_pixels), seed=seed + month_idx * 7, n_iter=12, scale=0.8
    )

    rng = np.random.default_rng(seed + month_idx * 31)
    noise = rng.normal(0, 0.15, size=(n_pixels, n_pixels))

    field = (
        base_value + altitude_effect + lat_effect
        + warm_cluster + cold_cluster + texture + noise
    )
    return field.astype(np.float32)  # type: ignore[no-any-return]


def create_worldclim_like_sample(
    output_dir: Path,
    variable: str = "tavg",
    n_pixels: int = 60,
    bbox_lon: tuple[float, float] = (-71.5, -69.5),
    bbox_lat: tuple[float, float] = (-34.5, -32.5),
    monthly_values: tuple[float, ...] | None = None,
    overwrite: bool = False,
    seed: int = 42,
) -> Path:
    """Genera 12 GeoTIFFs sintéticos con nomenclatura WorldClim v2.1.

    Parameters
    ----------
    output_dir : Path
        Directorio donde se escribirán los 12 GeoTIFFs.
    variable : str
        Nombre de la variable climática (p.ej., ``"tavg"``, ``"prec"``).
    n_pixels : int
        Tamaño de la grilla en cada dimensión (``n_pixels x n_pixels``).
    bbox_lon : tuple[float, float]
        Límites longitud (oeste, este).
    bbox_lat : tuple[float, float]
        Límites latitud (sur, norte).
    monthly_values : tuple[float, ...] | None
        12 valores base, uno por mes. Por defecto: climatología de Santiago de Chile.
    overwrite : bool
        Si ``False`` y los 12 archivos ya existen, omite la generación (idempotente).
    seed : int
        Semilla RNG para reproducibilidad bit-exacta.

    Returns
    -------
    Path
        Ruta a ``output_dir``.

    Raises
    ------
    ValueError
        Si ``monthly_values`` no tiene exactamente 12 elementos.
    """
    output_dir = Path(output_dir)

    if monthly_values is None:
        monthly_values = SANTIAGO_MONTHLY_TAVG

    if len(monthly_values) != 12:
        raise ValueError(
            f"monthly_values debe tener exactamente 12 elementos, "
            f"se recibieron {len(monthly_values)}"
        )

    expected_paths = [
        output_dir / _FILENAME_TEMPLATE.format(variable=variable, month=m)
        for m in range(1, 13)
    ]

    if not overwrite and all(p.exists() for p in expected_paths):
        return output_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    lon = np.linspace(bbox_lon[0], bbox_lon[1], n_pixels)
    lat = np.linspace(bbox_lat[1], bbox_lat[0], n_pixels)  # norte → sur
    lon_grid, lat_grid = np.meshgrid(lon, lat)

    for month_idx, base in enumerate(monthly_values):
        arr = _build_spatial_temperature_field(
            month_idx, base, lon_grid, lat_grid, bbox_lon, bbox_lat, seed
        )
        da = xr.DataArray(
            arr,
            dims=("y", "x"),
            coords={"y": lat, "x": lon},
            name=variable,
        ).rio.write_crs("EPSG:4326")
        da.rio.to_raster(expected_paths[month_idx])

    return output_dir


def read_monthly_stack(
    data_dir: Path,
    variable: str = "tavg",
) -> xr.DataArray:
    """Carga 12 GeoTIFFs mensuales como un único ``DataArray (month=12, y, x)``.

    Parameters
    ----------
    data_dir : Path
        Directorio con archivos ``wc2.1_2.5m_{variable}_NN.tif``.
    variable : str
        Nombre de la variable climática en los nombres de archivo.

    Returns
    -------
    xr.DataArray
        Forma ``(12, y, x)`` con coordenada ``month`` con valores ``1..12``.
    """
    arrays = []
    for month in range(1, 13):
        path = Path(data_dir) / _FILENAME_TEMPLATE.format(variable=variable, month=month)
        da = xr.open_dataarray(path, engine="rasterio").squeeze("band", drop=True)
        arrays.append(da)
    return xr.concat(arrays, dim="month").assign_coords(month=list(range(1, 13)))
