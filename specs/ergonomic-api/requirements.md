# Requirements — Ergonomic API (tipo terra)

**Estado:** Approved
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-18
**Última actualización:** 2026-05-18

## 1. Propósito

Proveer una capa de conveniencia de alto nivel que permita cargar, inspeccionar,
visualizar e interpolar stacks raster geoespaciales en pocas líneas, análoga al
paquete `terra` de R. Reduce la barrera de entrada para nuevos usuarios sin
reemplazar el pipeline completo de producción.

## 2. Alcance

### In-scope

- Función `rast(path)` para cargar un GeoTIFF multi-banda
- Clase `TempifyRast` con representación textual tipo terra y método `.str()`
- Función `plot(r, sub=None)` para visualizar bandas en grilla automática
- Función `tempify(stack, from_freq, to_freq, method)` para interpolación en memoria
- Exportación pública desde `tempify.__init__`

### Out-of-scope

- Soporte de NetCDF, Zarr u otros formatos (solo GeoTIFF en esta versión)
- Escritura a disco (el pipeline completo sigue disponible para eso)
- Detección automática de frecuencia de entrada (el usuario debe especificarla)
- Procesamiento Dask out-of-core (operación in-memory únicamente)

## 3. Actores y casos de uso

### Actor 1: Investigador o técnico nuevo en tempify

> Como investigador, quiero cargar un TIF mensual, visualizarlo, interpolarlo a diario
> y ver el resultado en pocas líneas, para evaluar rápidamente si tempify es útil
> para mis datos.

**Caso de uso típico:**
```python
from tempify import rast, tempify, plot
r = rast("worldclim_tmax_2023.tif")
print(r)
plot(r)
r2 = tempify(r, from_freq="monthly", to_freq="daily", method="cubic")
plot(r2, sub=range(1, 17))
```

## 4. Requisitos funcionales (formato EARS)

### REQ-001
THE SYSTEM SHALL expose `rast`, `tempify`, and `plot` as top-level symbols
importable directly from the `tempify` package (`from tempify import rast,
tempify, plot`).

### REQ-002
WHEN `rast(path)` is called with a valid GeoTIFF path, THE SYSTEM SHALL return
a `TempifyRast` object wrapping the loaded `xr.DataArray` with CRS preserved.

### REQ-003
WHEN `print(r)` is called on a `TempifyRast`, THE SYSTEM SHALL display a
compact summary including: class name, dimensions (bands × rows × cols),
spatial resolution, geographic extent, CRS, and data type.

### REQ-004
WHEN `r.str()` is called on a `TempifyRast`, THE SYSTEM SHALL print an extended
summary including dims, dtype, CRS, value range (min/max), NaN count, and
attribute names.

### REQ-005
WHEN `plot(r)` is called, THE SYSTEM SHALL render a facet grid with one panel
per band in automatic layout, shared colorbar, and band index as panel title.

### REQ-006
WHEN `plot(r, sub=range(a, b))` is called with a 1-based index range,
THE SYSTEM SHALL render only the bands in that range (analogous to terra's
`sub` argument).

### REQ-007
WHEN `tempify(stack, from_freq="monthly", to_freq="daily", method=m)` is called,
THE SYSTEM SHALL apply the named interpolation method in memory and return a
`TempifyRast` with the densified daily series.

### REQ-008
WHEN `tempify()` is called with `from_freq="monthly"`, THE SYSTEM SHALL assume
the input `TempifyRast` has exactly 12 bands and assign month coordinates 1..12
before invoking the interpolator.

### REQ-009
WHEN `tempify()` is called with an unsupported `method` string, THE SYSTEM SHALL
raise a `ValueError` listing the accepted method names.

### REQ-010
IF `rast(path)` is called with a non-existent file, THEN THE SYSTEM SHALL raise
a `FileNotFoundError` with the offending path in the message.

## 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Usabilidad | El flujo completo (rast→plot→tempify→plot) debe funcionar en ≤ 7 líneas | Ejemplo en docstring de `api.py` ejecutable en test |
| NFR-002 | Compatibilidad | `TempifyRast.data` debe devolver el `xr.DataArray` subyacente sin copia | `r.data is da` (identidad de objeto) |
| NFR-003 | Robustez | `plot()` no debe fallar si `sub` excede el número real de bandas; debe recortar silenciosamente | Test con `sub=range(1, 1000)` sobre stack de 12 bandas |

## 6. Criterios de aceptación

- [ ] REQ-001 cubierto por `test_import_toplevel`
- [ ] REQ-002 cubierto por `test_rast_returns_tempifyrast`
- [ ] REQ-003 cubierto por `test_repr_contains_expected_fields`
- [ ] REQ-004 cubierto por `test_str_method_extended_info`
- [ ] REQ-005 cubierto por `test_plot_all_bands_no_error`
- [ ] REQ-006 cubierto por `test_plot_sub_range`
- [ ] REQ-007 cubierto por `test_tempify_monthly_to_daily`
- [ ] REQ-008 cubierto por `test_tempify_assigns_month_coords`
- [ ] REQ-009 cubierto por `test_tempify_invalid_method_raises`
- [ ] REQ-010 cubierto por `test_rast_missing_file_raises`
- [ ] NFR-001 cubierto por `test_full_workflow_seven_lines`
- [ ] NFR-003 cubierto por `test_plot_sub_exceeds_bands`
- [ ] Tests en `tests/unit/test_api.py` con cobertura ≥ 85% del módulo `api.py`
- [ ] CHANGELOG actualizado con sección [0.1.6]

## 7. Dependencias y supuestos

### Specs relacionadas

- [io-handlers](../io-handlers/requirements.md) — `GeoTIFFReader` ya implementado
- [core-interpolation](../core-interpolation/requirements.md) — 6 interpoladores ya implementados

### Supuestos

- El GeoTIFF de entrada tiene exactamente 12 bandas cuando `from_freq="monthly"`
- La dimensión de banda se llama `band` al leer con `GeoTIFFReader`
- El año de referencia para `TemporalAxis` se infiere del `time.now()` si no se especifica

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Colisión del nombre `tempify` (función vs paquete) | Baja | Bajo | Exportar desde `tempify.api`; `from tempify import tempify` funciona sin ambigüedad en Python |
| Rendimiento lento con stacks grandes (>50 bandas) | Media | Medio | `plot()` recorta a 36 paneles máx; documentar límite en docstring |

## 8. Referencias

- R `terra` package: `?terra::rast`, `?terra::plot`
- ADR-0018: catálogo de interpoladores clásicos
