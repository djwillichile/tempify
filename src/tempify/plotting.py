"""Helpers de visualización para notebooks y tutoriales de tempify.

matplotlib es dependencia opcional. Instalar con::

    pip install tempify[viz]

Todas las funciones públicas hacen un import diferido de matplotlib y lanzan
``ImportError`` con un mensaje accionable si no está disponible.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import xarray as xr

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from mpl_toolkits.mplot3d import Axes3D


_ETIQUETAS_MESES = [
    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
]


def _require_matplotlib() -> None:
    """Lanza ImportError con hint de instalación si matplotlib no está disponible."""
    try:
        import matplotlib  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "matplotlib es requerido para visualización. "
            "Instalar con: pip install tempify[viz]"
        ) from exc


def plot_monthly_rasters(
    data_dir: Path,
    variable: str = "tavg",
    cmap: str = "turbo",
    cols: int = 4,
    figsize: tuple[float, float] = (14, 9),
    title: str | None = None,
    output_path: Path | None = None,
) -> tuple[Figure, Axes]:
    """Grafica 12 GeoTIFFs mensuales como grilla 3x4 con colorbar compartida.

    Parameters
    ----------
    data_dir : Path
        Directorio con archivos ``wc2.1_2.5m_{variable}_NN.tif``.
    variable : str
        Nombre de la variable climática en los nombres de archivo.
    cmap : str
        Nombre del colormap de matplotlib.
    cols : int
        Columnas en la grilla (filas se calculan automáticamente).
    figsize : tuple[float, float]
        Tamaño de la figura en pulgadas.
    title : str | None
        Supertítulo opcional de la figura.
    output_path : Path | None
        Si se entrega, guarda la figura en esta ruta (PNG/PDF/SVG).

    Returns
    -------
    tuple[Figure, Axes]
        Figura matplotlib y arreglo de axes.
    """
    _require_matplotlib()

    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.gridspec import GridSpec

    from tempify.datasets import read_monthly_stack

    monthly = read_monthly_stack(data_dir, variable=variable)

    rows = -(-12 // cols)  # división de techo

    # Columna dedicada para el colorbar (4% del ancho) — evita superposición
    fig = plt.figure(figsize=figsize, layout="constrained")
    gs = GridSpec(rows, cols + 1, figure=fig, width_ratios=[1] * cols + [0.04], hspace=0.25)

    ax0: plt.Axes | None = None
    axes_list: list[plt.Axes] = []
    for r in range(rows):
        for c in range(cols):
            ax = fig.add_subplot(gs[r, c], sharex=ax0, sharey=ax0)
            if ax0 is None:
                ax0 = ax
            axes_list.append(ax)
    cbar_ax = fig.add_subplot(gs[:, -1])

    vmin = float(monthly.min())
    vmax = float(monthly.max())

    im = None
    for i, ax in enumerate(axes_list):
        raster = monthly.isel(month=i).values
        im = ax.imshow(raster, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
        ax.set_title(_ETIQUETAS_MESES[i], fontsize=10, color="#0d2854")
        ax.set_xticks([])
        ax.set_yticks([])

    if im is not None:
        fig.colorbar(im, cax=cbar_ax, label=variable)

    if title:
        fig.suptitle(title, fontsize=12, fontweight="bold", color="#0d2854")

    axes = np.array(axes_list).reshape(rows, cols)

    if output_path is not None:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")

    return fig, axes


def plot_raster_timeseries(
    daily_out: xr.DataArray,
    monthly_input: xr.DataArray | None = None,
    pixel_yx: tuple[int, int] | None = None,
    figsize: tuple[float, float] = (12, 4.6),
    dpi: int = 110,
    title: str | None = None,
    output_path: Path | None = None,
) -> tuple[Figure, Axes]:
    """Grafica la serie temporal diaria de un píxel con anclas mensuales opcionales.

    Parameters
    ----------
    daily_out : xr.DataArray
        Output diario con coordenada ``time`` (forma ``(time, y, x)``).
    monthly_input : xr.DataArray | None
        Input mensual con coordenada ``month``. Si se entrega, se grafican
        los puntos ancla en el día 15 de cada mes.
    pixel_yx : tuple[int, int] | None
        ``(y_index, x_index)`` del píxel a graficar. Por defecto: píxel central.
    figsize : tuple[float, float]
        Tamaño de la figura en pulgadas.
    dpi : int
        Resolución de la figura.
    title : str | None
        Título opcional del gráfico.
    output_path : Path | None
        Si se entrega, guarda la figura en esta ruta.

    Returns
    -------
    tuple[Figure, Axes]
        Figura matplotlib y axes.
    """
    _require_matplotlib()

    import matplotlib.pyplot as plt

    if pixel_yx is None:
        iy = daily_out.sizes["y"] // 2
        ix = daily_out.sizes["x"] // 2
    else:
        iy, ix = pixel_yx

    series = daily_out.isel(y=iy, x=ix).values
    times = daily_out["time"].values
    doy = np.arange(1, len(times) + 1)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f6faf8")

    ax.plot(doy, series, color="#1d4ed8", linewidth=1.8, label="Diario interpolado", zorder=3)

    if monthly_input is not None:
        import pandas as pd

        year = int(pd.Timestamp(times[0]).year)
        month_values = monthly_input.isel(y=iy, x=ix).values
        month_doy = [
            datetime.date(year, m, 15).timetuple().tm_yday for m in range(1, 13)
        ]
        ax.scatter(
            month_doy, month_values,
            color="#dc2626", s=50, edgecolors="white", linewidth=1.0,
            zorder=4, label="Ancla mensual",
        )

    ax.set_xlim(1, len(times))
    ax.set_ylabel("°C", fontsize=10, color="#4a5b6b")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", loc="left", color="#0d2854")
    ax.grid(True, alpha=0.2, linewidth=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=9, framealpha=0.9)
    plt.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=dpi, bbox_inches="tight")

    return fig, ax


def plot_temporal_stack_3d(
    daily_out: xr.DataArray,
    months: list[int],
    days: tuple[int, ...] = (5, 15, 25),
    year: int | None = None,
    anchor_day: int = 15,
    month_labels: list[str] | None = None,
    cmap: str = "turbo",
    alpha_interp: float = 0.62,
    alpha_anchor: float = 0.92,
    time_spacing: float = 3.0,
    show_title: bool = True,
    show_legend: bool = True,
    show_colorbar: bool = True,
    output_path: Path | None = None,
    figsize: tuple[float, float] = (22, 10),
    dpi: int = 150,
    title: str | None = None,
) -> tuple[Figure, Axes3D]:
    """Grafica un stack ráster 3D de la serie temporal diaria.

    Cada fecha seleccionada se renderiza como un plano ráster vertical.
    Las fechas ancla (día ``anchor_day`` de cada mes) reciben opacidad completa
    y borde rojo; las capas interpoladas se muestran con menor opacidad.

    Parameters
    ----------
    daily_out : xr.DataArray
        Output diario con dims ``(time, y, x)``.
    months : list[int]
        Meses a incluir (1=Ene … 12=Dic).
    days : tuple[int, ...]
        Días del mes a extraer de cada mes.
    year : int | None
        Filtrar a un año específico si el DataArray abarca varios años.
    anchor_day : int
        Día del mes tratado como ancla mensual. Destacado con borde rojo.
    month_labels : list[str] | None
        12 etiquetas para el eje de tiempo. Por defecto: abreviaciones en español.
    cmap : str
        Colormap de matplotlib.
    alpha_interp : float
        Opacidad de capas interpoladas (0-1).
    alpha_anchor : float
        Opacidad de capas ancla (0-1).
    time_spacing : float
        Distancia entre capas consecutivas en el eje de tiempo.
    show_title : bool
        Si renderizar el supertítulo.
    show_legend : bool
        Si renderizar la leyenda ancla/interpolado.
    show_colorbar : bool
        Si renderizar la barra de color.
    output_path : Path | None
        Si se entrega, guarda la figura en esta ruta.
    figsize : tuple[float, float]
        Tamaño de la figura en pulgadas.
    dpi : int
        Resolución de la figura.
    title : str | None
        Texto del supertítulo. Ignorado si ``show_title=False``.

    Returns
    -------
    tuple[Figure, Axes3D]
        Figura matplotlib y axes 3D.
    """
    _require_matplotlib()

    import matplotlib.cm as cm
    import matplotlib.colors as mcolors
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    import pandas as pd
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    from tempify.utils import extract_daily_rasters

    if month_labels is None:
        month_labels = _ETIQUETAS_MESES

    subset = extract_daily_rasters(daily_out, months=months, days=list(days), year=year)
    times = subset["time"].values

    vmin = float(daily_out.min())
    vmax = float(daily_out.max())
    import matplotlib as _mpl
    colormap = _mpl.colormaps[cmap]
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

    fig = plt.figure(figsize=figsize, dpi=dpi)
    fig.patch.set_facecolor("#ffffff")
    ax: Axes3D = fig.add_subplot(111, projection="3d")

    ny = subset.sizes["y"]
    nx = subset.sizes["x"]
    x_idx = np.arange(nx, dtype=float)
    z_idx = np.arange(ny, dtype=float)
    xg, zg = np.meshgrid(x_idx, z_idx)

    anchor_y_positions: list[float] = []
    anchor_month_labels: list[str] = []

    for i, t in enumerate(times):
        y_pos = float(i) * time_spacing
        ts = pd.Timestamp(t)
        is_anchor = ts.day == anchor_day
        alpha = alpha_anchor if is_anchor else alpha_interp

        raster = subset.isel(time=i).values
        rgba = np.array(colormap(norm(raster)), dtype=float)
        rgba[..., 3] = alpha

        yg = np.full_like(xg, y_pos)
        ax.plot_surface(xg, yg, zg, facecolors=rgba, rstride=1, cstride=1, shade=False)

        if is_anchor:
            bx = [0.0, float(nx - 1), float(nx - 1), 0.0, 0.0]
            bz = [0.0, 0.0, float(ny - 1), float(ny - 1), 0.0]
            by = [y_pos] * 5
            ax.plot(bx, by, bz, color="#dc2626", linewidth=1.5, zorder=5)
            if ts.month in months:
                anchor_y_positions.append(y_pos)
                m_idx = ts.month - 1
                anchor_month_labels.append(
                    month_labels[m_idx] if m_idx < len(month_labels) else str(ts.month)
                )

    ax.set_yticks(anchor_y_positions)
    ax.set_yticklabels(anchor_month_labels, fontsize=9, color="#4a5b6b")
    ax.set_xticks([])
    ax.set_zticks([])
    ax.view_init(elev=25, azim=-60)

    if show_title and title:
        fig.suptitle(title, fontsize=13, color="#0d2854", fontweight="bold", y=0.97)

    if show_colorbar:
        sm = cm.ScalarMappable(cmap=colormap, norm=norm)
        sm.set_array(np.array([]))
        fig.colorbar(sm, ax=ax, shrink=0.45, pad=0.01, label="°C")

    if show_legend:
        anchor_patch = mpatches.Patch(
            facecolor="#fee2e2", edgecolor="#dc2626", linewidth=1.5,
            label=f"Ancla mensual (día {anchor_day})",
        )
        interp_patch = mpatches.Patch(facecolor="#dbeafe", alpha=0.6, label="Interpolado")
        ax.legend(
            handles=[anchor_patch, interp_patch], loc="upper left",
            fontsize=9, framealpha=0.9,
        )

    plt.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=dpi, bbox_inches="tight")

    return fig, ax
