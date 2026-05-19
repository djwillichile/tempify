"""Ergonomic API for tempify — terra-like convenience layer.

Exposes three top-level symbols:

    from tempify import rast, tempify, plot

    r  = rast("datos/worldclim_tmax.tif")   # cargar GeoTIFF
    print(r)                                  # info compacta tipo terra
    r.str()                                   # estructura detallada
    plot(r)                                   # grilla de bandas

    r2 = tempify(r, from_freq="monthly", to_freq="daily", method="cubic")
    print(r2)
    plot(r2, sub=range(1, 17))               # subset de las primeras 16 bandas
"""

from __future__ import annotations

import contextlib
import io
import math
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr

from tempify.interpolation import (
    AkimaInterpolator,
    BaseInterpolator,
    CubicSplineInterpolator,
    FourierInterpolator,
    LinearInterpolator,
    PchipInterpolator,
    PchipMeanPreservingInterpolator,
    TemporalAxis,
)
from tempify.io.readers.geotiff import GeoTIFFReader
from tempify.utils import raster_info

_INTERPOLATORS: dict[str, type[BaseInterpolator]] = {
    "linear": LinearInterpolator,
    "cubic": CubicSplineInterpolator,
    "pchip": PchipInterpolator,
    "pchip_mp": PchipMeanPreservingInterpolator,
    "fourier": FourierInterpolator,
    "akima": AkimaInterpolator,
}

_SPATIAL: frozenset[str] = frozenset({"y", "x"})

_MAX_PANELS = 36


class TempifyRast:
    """Wrapper ergonómico de ``xr.DataArray`` con presentación tipo terra.

    Parameters
    ----------
    data : xr.DataArray
        Array subyacente con dimensiones espaciales ``y`` y ``x``.
    """

    def __init__(self, data: xr.DataArray) -> None:
        self._data = data

    @property
    def data(self) -> xr.DataArray:
        """DataArray subyacente sin copia."""
        return self._data

    @property
    def shape(self) -> tuple[int, ...]:
        """Delega a ``data.shape``."""
        return tuple(self._data.shape)

    @property
    def crs(self) -> Any:
        """CRS del stack vía rioxarray. ``None`` si no disponible."""
        try:
            return self._data.rio.crs
        except Exception:
            return None

    def __repr__(self) -> str:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                raster_info(self._data)
            except Exception as exc:
                return f"<TempifyRast shape={self.shape} (error interno: {exc})>"
        return buf.getvalue().rstrip()

    def str(self) -> None:
        """Imprime información extendida del stack (análogo a ``terra::str(r)``)."""
        print(repr(self))
        da = self._data
        vals = da.values
        finite = vals[~np.isnan(vals)]
        if finite.size:
            print(f"rango       : [{float(finite.min()):.4f}, {float(finite.max()):.4f}]")
        nan_count = int(np.isnan(vals).sum())
        print(f"NaN         : {nan_count}")
        if da.attrs:
            print(f"atributos   : {list(da.attrs.keys())}")


def rast(path: str | Path) -> TempifyRast:
    """Carga un GeoTIFF multi-banda como :class:`TempifyRast`.

    Parameters
    ----------
    path : str | Path
        Ruta al archivo GeoTIFF (relativa o absoluta).

    Returns
    -------
    TempifyRast

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe en la ruta indicada.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {p}")
    reader = GeoTIFFReader()
    da = reader.read(p)
    return TempifyRast(da)


def plot(
    r: TempifyRast | xr.DataArray,
    sub: range | list[int] | None = None,
    cmap: str = "viridis",
    figsize: tuple[float, float] | None = None,
) -> None:
    """Visualiza bandas del stack en grilla automática.

    Parameters
    ----------
    r : TempifyRast | xr.DataArray
        Stack a visualizar.
    sub : range | list[int] | None
        Índices 1-based de bandas a mostrar (como el argumento ``sub`` de
        ``terra::plot``). ``None`` muestra todas (máx 36).
    cmap : str
        Colormap de matplotlib. Default ``"viridis"``.
    figsize : tuple[float, float] | None
        Tamaño de figura en pulgadas. ``None`` → automático.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(
            "matplotlib es necesario para plot(). "
            "Instalar con: pip install matplotlib"
        ) from exc

    da = r.data if isinstance(r, TempifyRast) else r
    stack_dims = [d for d in da.dims if d not in _SPATIAL]

    if not stack_dims:
        fig, ax = plt.subplots(figsize=figsize or (5, 4))
        im = ax.imshow(da.values, cmap=cmap)
        fig.colorbar(im, ax=ax)
        plt.tight_layout()
        plt.show()
        return

    dim = stack_dims[0]
    n_total = da.sizes[dim]

    if sub is not None:
        indices = [i - 1 for i in sub if 1 <= i <= n_total]
    else:
        indices = list(range(min(n_total, _MAX_PANELS)))

    if not indices:
        return

    n = len(indices)
    ncols = math.ceil(math.sqrt(n))
    nrows = math.ceil(n / ncols)

    auto_figsize = figsize or (3.5 * ncols, 3.0 * nrows)
    fig, axes = plt.subplots(
        nrows, ncols, figsize=auto_figsize, squeeze=False, constrained_layout=True
    )

    vals_flat = da.values[~np.isnan(da.values)]
    vmin = float(vals_flat.min()) if vals_flat.size else 0.0
    vmax = float(vals_flat.max()) if vals_flat.size else 1.0

    all_axes = axes.ravel().tolist()
    im = None
    for plot_i, band_i in enumerate(indices):
        ax = all_axes[plot_i]
        band_data = da.isel({dim: band_i}).values
        im = ax.imshow(band_data, cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_title(str(band_i + 1), fontsize=8)
        ax.axis("off")

    for ax in all_axes[len(indices):]:
        ax.set_visible(False)

    if im is not None:
        fig.colorbar(im, ax=all_axes, shrink=0.6)

    plt.show()


def tempify(
    stack: TempifyRast | xr.DataArray,
    from_freq: str | int,
    to_freq: str | int,
    method: str = "pchip_mp",
    year: int | None = None,
) -> TempifyRast:
    """Interpola un stack raster a mayor frecuencia temporal (operación en memoria).

    No escribe a disco. Para flujos de producción con validación completa y
    escritura multi-formato, usar :class:`~tempify.pipeline.core.TempifyPipeline`.

    Parameters
    ----------
    stack : TempifyRast | xr.DataArray
        Stack de entrada.
    from_freq : str | int
        Frecuencia de entrada. ``"monthly"`` asume 12 bandas con ciclo
        mensual completo.
    to_freq : str | int
        Frecuencia objetivo. ``"daily"`` genera 365/366 pasos según ``year``.
    method : str
        Nombre del interpolador. Opciones: ``"linear"``, ``"cubic"``,
        ``"pchip"``, ``"pchip_mp"``, ``"fourier"``, ``"akima"``.
        Default: ``"pchip_mp"`` (PCHIP + conservación de media mensual).
    year : int | None
        Año de referencia para el eje temporal. ``None`` → año actual.

    Returns
    -------
    TempifyRast
        Stack interpolado con dimensión ``"time"`` y coordenadas datetime.

    Raises
    ------
    ValueError
        Si ``method`` no es uno de los nombres válidos.
    """
    if method not in _INTERPOLATORS:
        valid = ", ".join(f'"{k}"' for k in sorted(_INTERPOLATORS))
        raise ValueError(
            f"method={method!r} no reconocido. "
            f"Opciones válidas: {valid}"
        )

    da = stack.data if isinstance(stack, TempifyRast) else stack
    ref_year = year if year is not None else datetime.now().year

    if from_freq in ("monthly", 12):
        if "band" in da.dims:
            da = da.rename({"band": "month"})
        da = da.assign_coords(month=list(range(1, 13)))

    axis = TemporalAxis.from_months(ref_year)
    interpolator = _INTERPOLATORS[method]()
    result = interpolator.interpolate(da, axis)

    # Normalizar orden de dims a (time, y, x) para consistencia con raster convencional
    if "time" in result.dims:
        lead = ["time"]
        rest = [d for d in result.dims if d != "time"]
        result = result.transpose(*lead, *rest)

    return TempifyRast(result)
