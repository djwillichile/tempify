"""Helpers para cargar y filtrar outputs del pipeline de tempify."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import xarray as xr

if TYPE_CHECKING:
    from tempify.pipeline.result import PipelineResult


def open_tempify_output(result: PipelineResult | Path) -> xr.DataArray:
    """Abre el primer output de un :class:`~tempify.pipeline.result.PipelineResult` o ruta.

    Detecta el formato desde la extensión del archivo y despacha al backend
    correcto de xarray.

    Parameters
    ----------
    result : PipelineResult | Path
        Resultado completado del pipeline o ruta directa al archivo de salida.

    Returns
    -------
    xr.DataArray
        Serie temporal diaria con dims ``(time, y, x)``.

    Raises
    ------
    ValueError
        Si el resultado no tiene outputs (modo dry_run) o el formato es desconocido.
    """
    if isinstance(result, Path):
        path = result
    else:
        # Duck-type as PipelineResult (avoids circular import issues with MagicMock in tests)
        if not result.outputs:
            raise ValueError(
                "PipelineResult has no outputs. Was the pipeline run in dry_run mode?"
            )
        path = result.outputs[0]

    suffix = path.suffix.lower()
    if suffix in {".nc", ".nc4", ".netcdf"}:
        return xr.open_dataarray(path, engine="netcdf4")
    elif suffix in {".tif", ".tiff"}:
        import rioxarray  # noqa: F401
        return xr.open_dataarray(path, engine="rasterio")
    elif suffix == ".zarr" or path.is_dir():
        return xr.open_dataarray(path, engine="zarr")
    else:
        raise ValueError(
            f"Cannot determine output format from path: {path}. "
            "Supported: .nc, .tif, .zarr"
        )


def extract_daily_rasters(
    daily_out: xr.DataArray,
    months: list[int] | None = None,
    days: list[int] | None = None,
    year: int | None = None,
) -> xr.DataArray:
    """Filtra un DataArray diario a meses y/o días-del-mes específicos.

    Parameters
    ----------
    daily_out : xr.DataArray
        Serie temporal diaria con coordenada ``time`` (datetime de pandas).
    months : list[int] | None
        Meses a conservar (1=Ene … 12=Dic). ``None`` conserva todos.
    days : list[int] | None
        Días del mes a conservar (1-31). ``None`` conserva todos.
    year : int | None
        Filtrar a un año calendario específico. ``None`` conserva todos.

    Returns
    -------
    xr.DataArray
        Subconjunto con los pasos de tiempo que satisfacen los filtros.
    """
    time = daily_out["time"]
    mask = np.ones(time.shape, dtype=bool)

    if months is not None:
        mask &= np.isin(time.dt.month.values, months)
    if days is not None:
        mask &= np.isin(time.dt.day.values, days)
    if year is not None:
        mask &= time.dt.year.values == year

    return daily_out.isel(time=mask)


def get_anchor_dates(year: int) -> list[datetime.date]:
    """Retorna las 12 fechas ancla mensuales (día 15 de cada mes) para ``year``.

    Parameters
    ----------
    year : int
        Año calendario objetivo.

    Returns
    -------
    list[datetime.date]
        12 objetos :class:`datetime.date`, uno por mes, siempre en el día 15.
    """
    return [datetime.date(year, month, 15) for month in range(1, 13)]


def raster_info(da: xr.DataArray) -> None:
    """Imprime un resumen del DataArray similar a ``terra::print(r)`` en R.

    Detecta automáticamente si la dimensión principal es temporal (``time``)
    o mensual (``month``) y adapta el resumen en consecuencia.

    Parameters
    ----------
    da : xr.DataArray
        DataArray con dimensiones espaciales ``y`` y ``x``.
    """
    lines: list[str] = ["clase       : xr.DataArray"]

    spatial_dims = {"y", "x"}
    stack_dims = [d for d in da.dims if d not in spatial_dims]

    ny = da.sizes.get("y", 0)
    nx = da.sizes.get("x", 0)

    if "time" in da.dims:
        n_time = da.sizes["time"]
        lines.append(f"dimensiones : {n_time} pasos x {ny} filas x {nx} cols")
        t0 = str(da["time"].values[0])[:10]
        t1 = str(da["time"].values[-1])[:10]
        lines.append(f"tiempo      : {t0} → {t1}  ({n_time} pasos)")
    elif "month" in da.dims:
        n_layers = da.sizes["month"]
        lines.append(f"dimensiones : {n_layers} capas x {ny} filas x {nx} cols")
        month_vals = list(da["month"].values)
        preview = ", ".join(str(m) for m in month_vals[:6])
        if len(month_vals) > 6:
            preview += ", ..."
        lines.append(f"capas       : {preview}")
    elif stack_dims:
        n_layers = da.sizes[stack_dims[0]]
        lines.append(
            f"dimensiones : {n_layers} capas x {ny} filas x {nx} cols  (dim: {stack_dims[0]})"
        )
    else:
        lines.append(f"dimensiones : {ny} filas x {nx} cols")

    if "x" in da.coords and len(da["x"]) > 1:
        res_x = abs(float(da["x"].values[1]) - float(da["x"].values[0]))
        res_y = (
            abs(float(da["y"].values[1]) - float(da["y"].values[0]))
            if "y" in da.coords and len(da["y"]) > 1
            else res_x
        )
        lines.append(f"resolución  : {res_x:.4f}° lon x {res_y:.4f}° lat")

    if "x" in da.coords and "y" in da.coords:
        xmin = float(da["x"].min())
        xmax = float(da["x"].max())
        ymin = float(da["y"].min())
        ymax = float(da["y"].max())
        lines.append(f"extensión   : lon [{xmin:.4f}, {xmax:.4f}]  lat [{ymin:.4f}, {ymax:.4f}]")

    try:
        crs = da.rio.crs
        if crs is not None:
            epsg = crs.to_epsg()
            crs_str = f"EPSG:{epsg}" if epsg else str(crs)
        else:
            crs_str = "no disponible"
    except Exception:
        crs_str = "no disponible (instalar rioxarray)"
    lines.append(f"CRS         : {crs_str}")

    lines.append(f"tipo        : {da.dtype}")

    if da.name:
        lines.append(f"nombre      : {da.name}")

    print("\n".join(lines))
