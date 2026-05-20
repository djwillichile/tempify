# ADR-0001: Use xarray.DataArray as central data abstraction

**Status:** Accepted
**Date:** 2026-05-15
**Decision-makers:** Guillermo Fuentes-Jaque

## Context

tempify needs an internal data abstraction to represent raster stacks across all layers (I/O, detection, validation, interpolation, pipeline). Several candidates exist in the Python geospatial ecosystem:

1. **NumPy arrays** with separate metadata
2. **pandas DataFrame** (long format)
3. **geopandas GeoDataFrame** (vector-oriented)
4. **xarray DataArray** (N-dim labeled arrays)
5. **Raw rasterio Dataset** objects

## Decision

Use **`xarray.DataArray`** as the central data abstraction across all layers.

## Rationale

### Pros of xarray

- **Labeled dimensions and coordinates** native: `(time, y, x)` with proper coordinate values, essential for climate data.
- **CF-conventions support** via rioxarray and built-in attrs handling.
- **Dask integration** native: `chunks={"time": 1, "x": 512, "y": 512}` is one parameter away.
- **Out-of-core processing** essential for stacks larger than RAM (Chile complete at 30 arc-sec).
- **De facto standard** in climate / geospatial Python (xclim, climakitae, climpyrical, intake-xarray all depend on it).
- **CRS preservation** via rioxarray `rio` accessor.
- **Ufunc vectorization** with `xr.apply_ufunc(..., dask="parallelized")` eliminates manual loops.

### Cons of xarray

- Heavier dependency than raw numpy.
- Learning curve for users not familiar with labeled arrays.
- Some operations (e.g., complex indexing) slower than equivalent numpy.

### Why not the alternatives

- **NumPy** alone: would force us to carry metadata separately (CRS, time axis, units), reinventing xarray.
- **pandas**: long format requires reshape for every spatial operation; not idiomatic for raster.
- **geopandas**: vector-oriented, wrong tool for raster stacks.
- **rasterio Dataset**: low-level, single-file oriented; doesn't handle multi-temporal naturally.

## Consequences

### Positive

- All layers communicate via a single, well-understood type.
- Parallelism via Dask is "free" once chunking is set.
- Users familiar with xarray (the target audience: climate scientists) feel immediately at home.

### Negative

- Mandatory dependency on xarray + rioxarray + (optionally) dask.
- Test fixtures must be xarray objects, not raw arrays.

### Risks

- xarray API has evolved over years; we pin to `>= 2024.1` to use modern features. If xarray makes breaking changes in the future, we may need migration work.

## Implementation notes

- All I/O readers return `xr.DataArray`.
- All I/O writers accept `xr.DataArray`.
- Internal functions type-hint with `xr.DataArray`.
- CRS preserved via `rioxarray` accessor (`.rio.crs`, `.rio.write_crs`).
- Time coordinate follows CF-conventions: `units="days since YYYY-MM-DD"`, `calendar` attribute.

## References

- xarray documentation: https://docs.xarray.dev/
- rioxarray: https://corteva.github.io/rioxarray/
- CF Conventions: https://cfconventions.org/
- Pangeo project (Climate Python ecosystem): https://pangeo.io/
