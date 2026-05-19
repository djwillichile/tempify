# Design — Ergonomic API (tipo terra)

**Estado:** Approved
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-18

## 1. Visión técnica

Se añade un módulo `src/tempify/api.py` con tres funciones públicas (`rast`,
`tempify`, `plot`) y una clase wrapper (`TempifyRast`). La capa es puramente
ergonómica: no implementa lógica científica nueva, reutiliza `GeoTIFFReader`,
los interpoladores existentes, y `raster_info()` de `utils.py`. Opera en memoria
y no escribe a disco.

## 2. Arquitectura propuesta

```
tempify.__init__
    └─ from tempify.api import rast, tempify, plot

tempify.api
    ├─ TempifyRast          wrapper de xr.DataArray
    ├─ rast(path)           → TempifyRast   (usa GeoTIFFReader)
    ├─ plot(r, sub, ...)    → None          (matplotlib facet grid)
    └─ tempify(stack, ...)  → TempifyRast   (usa interpoladores)

Dependencias internas reutilizadas:
    tempify.io.readers.geotiff.GeoTIFFReader
    tempify.interpolation.*  (6 interpoladores + TemporalAxis)
    tempify.utils.raster_info
```

### Componentes nuevos

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| `TempifyRast` | `src/tempify/api.py` | Wrapper de `xr.DataArray` con repr terra-like |
| `rast()` | `src/tempify/api.py` | Carga ergonómica de GeoTIFF → `TempifyRast` |
| `plot()` | `src/tempify/api.py` | Visualización facet grid simple |
| `tempify()` (función) | `src/tempify/api.py` | Interpolación en memoria → `TempifyRast` |

### Componentes modificados

| Componente | Ubicación | Cambio |
|---|---|---|
| `__init__.py` | `src/tempify/__init__.py` | Agrega exports: `rast`, `tempify`, `plot` |

## 3. Contratos públicos (APIs)

### `TempifyRast`

```python
class TempifyRast:
    def __init__(self, data: xr.DataArray) -> None: ...

    def __repr__(self) -> str:
        """Captura stdout de raster_info() y lo retorna como string."""

    def str(self) -> None:
        """Imprime info extendida: dims, dtype, CRS, rango de valores, attrs."""

    @property
    def data(self) -> xr.DataArray:
        """DataArray subyacente (sin copia; identidad de objeto garantizada)."""

    @property
    def shape(self) -> tuple[int, ...]:
        """Delega a self.data.shape."""

    @property
    def crs(self) -> Any:
        """Delega a self.data.rio.crs (None si rioxarray no disponible)."""
```

**Pre-condiciones:** `data` debe ser `xr.DataArray` con dims espaciales `y` y `x`.
**Post-condiciones:** `repr(r)` nunca lanza excepción (captura errores internamente).

### `rast(path)`

```python
def rast(path: str | Path) -> TempifyRast:
    """Carga un GeoTIFF multi-banda como TempifyRast.

    Parameters
    ----------
    path : str | Path
        Ruta al archivo GeoTIFF. Puede ser relativa o absoluta.

    Returns
    -------
    TempifyRast

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe.
    UnsupportedFormatError
        Si el archivo no es un GeoTIFF legible.
    """
```

**Pre-condiciones:** El archivo existe y es un GeoTIFF válido.
**Post-condiciones:** `result.data` tiene dims `(band, y, x)` con CRS preservado.

### `plot(r, sub=None, cmap="viridis", figsize=None)`

```python
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
    sub : range | list[int] | None
        Índices 1-based de bandas a mostrar. None → todas (máx 36).
    cmap : str
        Colormap de matplotlib.
    figsize : tuple | None
        Tamaño de figura. None → auto según número de paneles.
    """
```

**Pre-condiciones:** `r` tiene al menos una dimensión no espacial (bandas).
**Post-condiciones:** Se muestra una figura matplotlib; no retorna nada.
**Nota:** Si `sub` excede el número real de bandas, se recorta silenciosamente.

### `tempify(stack, from_freq, to_freq, method="pchip_mp", year=None)`

```python
def tempify(
    stack: TempifyRast | xr.DataArray,
    from_freq: str | int,
    to_freq: str | int,
    method: str = "pchip_mp",
    year: int | None = None,
) -> TempifyRast:
    """Interpola un stack raster a mayor frecuencia temporal (en memoria).

    Parameters
    ----------
    stack : TempifyRast | xr.DataArray
    from_freq : str | int
        Frecuencia de entrada. "monthly" = 12 pasos.
    to_freq : str | int
        Frecuencia objetivo. "daily" = 365/366 pasos según year.
    method : str
        Nombre del interpolador: "linear", "cubic", "pchip",
        "pchip_mp", "fourier", "akima". Default: "pchip_mp".
    year : int | None
        Año de referencia para TemporalAxis. None → año actual.

    Returns
    -------
    TempifyRast
        Stack interpolado con dim "time" y coordenadas datetime.

    Raises
    ------
    ValueError
        Si method no es uno de los nombres válidos.
    InvalidMonthlyStackError
        Si from_freq="monthly" pero el stack no tiene 12 bandas.
    """
```

## 4. Modelos de datos

No hay modelos de datos nuevos. `TempifyRast` es un wrapper simple sin estado
adicional más allá del `xr.DataArray` subyacente.

## 5. Algoritmos clave

### `tempify()` — preparación del DataArray para el interpolador

El interpolador espera `dim=month` con coords `1..12`. El GeoTIFF cargado con
`rast()` tiene `dim=band`. Pasos:

1. Extraer el `xr.DataArray` subyacente si es `TempifyRast`
2. Si `from_freq="monthly"`: renombrar `band` → `month`; asignar coord `month=[1..12]`
3. Construir `TemporalAxis.from_months(year)` para el año de referencia
4. Instanciar el interpolador correspondiente (ver tabla de despacho)
5. Llamar `.interpolate(source, target_axis)`
6. Envolver resultado en `TempifyRast`

**Tabla de despacho** (nombre → clase):

```python
_INTERPOLATORS = {
    "linear":   LinearInterpolator,
    "cubic":    CubicSplineInterpolator,
    "pchip":    PchipInterpolator,
    "pchip_mp": PchipMeanPreservingInterpolator,
    "fourier":  FourierInterpolator,
    "akima":    AkimaInterpolator,
}
```

### `plot()` — layout automático de facets

```
n = número de bandas a mostrar (respetando sub y máx 36)
ncols = ceil(sqrt(n))
nrows = ceil(n / ncols)
```

Un colorbar global se añade al costado derecho de la figura usando
`fig.colorbar(im, ax=axes.ravel().tolist())`.

### `__repr__` de `TempifyRast`

Captura stdout de `raster_info()` usando `io.StringIO` + `contextlib.redirect_stdout`
para retornar la cadena sin imprimir directamente (permite que `print(r)` la
muestre y que `repr(r)` funcione en notebooks).

## 6. Decisiones de diseño

### Decisión 1: Wrapper vs subclase de xr.DataArray

**Opciones consideradas:**
1. Subclase de `xr.DataArray` — frágil, xarray desaconseja herencia directa
2. Wrapper limpio con `.data` como propiedad — estable, explícito
3. Accessor xarray (`.tempify`) — pierdo `print(r)` natural

**Decisión:** Opción 2 (wrapper).
**Razón:** xarray oficialmente desaconseja subclassing; el wrapper da control total
sobre `__repr__` sin riesgo de romper operaciones internas de xarray.

### Decisión 2: `tempify()` solo en memoria

**Decisión:** No reutilizar `TempifyPipeline` (que escribe a disco y tiene fases
de validación). Llamar al interpolador directamente.
**Razón:** El caso de uso es exploración rápida; la latencia de validación + I/O
del pipeline completo sería contraproducente.

### Decisión 3: Año de referencia en `tempify()`

**Decisión:** Default `year=None` → `datetime.now().year`.
**Razón:** Las fechas absolutas en el resultado son más útiles que índices enteros;
el año actual es el default más intuitivo para exploración.

## 7. Estrategia de testing

### Tests unitarios (`tests/unit/test_api.py`)

- `test_import_toplevel` — `from tempify import rast, tempify, plot` sin error
- `test_rast_returns_tempifyrast` — tipo del objeto retornado
- `test_rast_missing_file_raises` — `FileNotFoundError`
- `test_rast_data_identity` — `r.data is da` (sin copia)
- `test_repr_contains_expected_fields` — campos clave en repr
- `test_str_method_extended_info` — método `.str()` no lanza
- `test_plot_all_bands_no_error` — `plot(r)` sin excepción (matplotlib `Agg` backend)
- `test_plot_sub_range` — `plot(r, sub=range(1, 4))` genera 3 paneles
- `test_plot_sub_exceeds_bands` — `plot(r, sub=range(1, 1000))` recorta silenciosamente
- `test_tempify_monthly_to_daily` — shape resultante tiene 365/366 en dim 0
- `test_tempify_assigns_month_coords` — coords `month` presentes antes de interpolar
- `test_tempify_returns_tempifyrast` — tipo del retorno
- `test_tempify_invalid_method_raises` — `ValueError` con método desconocido
- `test_full_workflow_seven_lines` — flujo completo sin error

### Fixtures necesarios

- `synthetic_monthly_geotiff` — TIF de 12 bandas 4×4 px (generado en conftest)

## 8. Plan de migración

No hay migración: la API es estrictamente aditiva. Ningún símbolo existente
cambia su interfaz.

## 9. Métricas de calidad

| Métrica | Umbral |
|---|---|
| Coverage de `api.py` | ≥ 85% |
| Tiempo de `rast()` en TIF ≤ 10 MB | < 2 s |
| Tiempo de `plot()` (12 bandas) | < 5 s |

## 10. Trazabilidad requirements → design

| Requirement | Componente que lo implementa |
|---|---|
| REQ-001 | `tempify/__init__.py` — exports |
| REQ-002 | `rast()` + `GeoTIFFReader` |
| REQ-003 | `TempifyRast.__repr__` + `raster_info()` |
| REQ-004 | `TempifyRast.str()` |
| REQ-005 | `plot()` sin `sub` |
| REQ-006 | `plot()` con `sub` |
| REQ-007 | `tempify()` función |
| REQ-008 | `tempify()` — renombre band→month |
| REQ-009 | `tempify()` — validación de método |
| REQ-010 | `rast()` — FileNotFoundError |
