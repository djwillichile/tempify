"""tempify: temporal densification for geospatial raster stacks.

Generate more data between your existing data. Given a low-frequency
raster stack (e.g., monthly), produces a high-frequency stack (e.g.,
daily) while preserving statistical properties such as monthly mean
conservation.

Ergonomic API (v0.1.6)::

    from tempify import rast, tempify, plot

    r  = rast("datos/worldclim_tmax.tif")
    print(r)
    plot(r)

    r2 = tempify(r, from_freq="monthly", to_freq="daily", method="cubic")
    plot(r2, sub=range(1, 17))
"""

from tempify.api import plot, rast, tempify

__version__ = "0.1.6"

__all__ = ["rast", "tempify", "plot", "__version__"]
