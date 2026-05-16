# ADR-0009: Tolerancias canónicas de coherencia geoespacial

**Status:** Accepted
**Date:** 2026-05-16
**Decision-makers:** Guillermo Fuentes-Jaque

## Contexto

La Capa 3 (`tempify.validation`, `GeospatialCoherenceValidator`) y la Capa 2 (`tempify.detection`, `StructureDetector` en modo B) necesitan decidir si un conjunto de archivos ráster es "homogéneo" (mismo CRS, mismo extent, misma resolución, mismo nodata, mismas dimensiones) antes de procesarlo. La spec `structure-detection` REQ-003 menciona "same CRS, same extent, same format" sin definir tolerancia numérica, y la spec `validation` REQ-001 habla de "configurable tolerances" sin fijar valores.

Una comparación estricta byte-a-byte de extent y resolución es inviable en la práctica:

1. **Redondeo en metadata GeoTIFF.** GDAL escribe coordenadas en `GeoTransform` como `double` y diferentes drivers (GTiff, COG, NetCDF→GTiff) pueden diferir en el último dígito significativo aun cuando el grid lógico es idéntico.
2. **Reproyecciones internas.** Productos como WorldClim distribuyen tiles con extent calculado por GDAL a partir del CRS source, lo que introduce errores de orden 1e-9 a 1e-7 grados decimales.
3. **Distintas convenciones de origen.** Algunos drivers reportan extent como esquina del píxel y otros como centro; aunque rioxarray normaliza, persisten diferencias subpíxel.
4. **CRS expresado de formas distintas.** `EPSG:4326`, `OGC:CRS84` y un WKT explícito pueden representar el mismo sistema geográfico con orden de ejes diferente.

Necesitamos un contrato numérico explícito, único en todo el proyecto, no configurable en v1.0, para que el comportamiento sea reproducible (ver ADR-0007) y trazable en el reporte.

## Decisión

Definir **tolerancias canónicas** centralizadas en `tempify.validation.geocoherence.CANONICAL_TOLERANCES` (dataclass `frozen`). Toda comparación de homogeneidad geoespacial en el proyecto las usa.

| Atributo | Tolerancia | Justificación |
|---|---|---|
| **CRS** | Match estricto vía `pyproj.CRS.equals(other, ignore_axis_order=True)`. | EPSG distintos (aunque representen el mismo datum, por ejemplo `4326` vs `4979`) se consideran heterogéneos. `ignore_axis_order=True` evita falsos negativos por discrepancia lon-lat vs lat-lon entre productos. Reproyección no está in-scope (ver `validation` § Out-of-scope). |
| **Extent (bounds)** | `rtol=1e-6` y `atol = 0.01 * pixel_size` (proporcional al tamaño de píxel). | Tolerancia inferior al 1% del píxel evita falsos positivos por redondeo en metadata GeoTIFF, y al mismo tiempo detecta desplazamientos reales del orden de un píxel completo. Usar `atol` constante (por ejemplo 1e-6 grados) falla en proyecciones métricas, por eso se acopla al `pixel_size`. |
| **Resolución (pixel size)** | `rtol=1e-6` en cada dimensión (x e y por separado). | Detecta 30 m vs 30.1 m (rtol ≈ 3e-3) como heterogéneo, pero acepta 30.0 vs 30.0000003 (errores de doble precisión). Comparación independiente por eje porque productos como CHELSA tienen pixel anisotrópico (px ≠ py). |
| **Nodata** | Match estricto. Si ambos archivos tienen `_FillValue`/`nodata`, deben ser iguales (con `NaN == NaN` aceptado). Si uno lo tiene y el otro no, heterogéneo. | El nodata cambia la semántica de la interpolación; mezclar `-9999` con `NaN` produce artefactos. La verificación `NaN == NaN` se hace vía `numpy.isnan` para evitar la asimetría del operador `==`. |
| **Dimensiones (height × width)** | Match estricto (mismo número de píxeles enteros en cada eje). | El número de píxeles es un entero, no admite tolerancia. Diferente shape implica diferente grid lógico. |

## Alternativas consideradas

### A. Match estricto byte-a-byte (sin tolerancia)

Comparar extent y resolución con `==` exacto.
**Descartado:** falsos positivos sistemáticos en GeoTIFFs reales del ecosistema (WorldClim, CHELSA, CHIRPS) que son lógicamente idénticos pero difieren en el bit 52 del double. Forzaría preprocesamiento manual de los inputs, contradiciendo el contrato de detección automática.

### B. Tolerancias laxas (`rtol=1e-3`)

Aceptar diferencias del orden 0.1%.
**Descartado:** un raster de 30 m y otro de 30.1 m (diferencia real de 3.3e-3) se considerarían homogéneos y el pipeline produciría salida silenciosamente incorrecta. La tolerancia laxa enmascara errores reales de configuración del usuario.

### C. Tolerancias configurables por el usuario

Exponer las tolerancias en `PipelineConfig`.
**Descartado para v1.0:** introduce un grado de libertad que rompe la reproducibilidad declarada en ADR-0007 (mismos inputs + parámetros = mismo output, pero ahora "parámetros" incluiría las tolerancias). Se difiere a una versión futura con justificación de caso de uso real; por ahora cambiar las tolerancias requiere un nuevo ADR.

## Consecuencias

### Positivas

- **Contrato único.** `GeospatialCoherenceValidator` y `StructureDetector` (modo B) comparten exactamente la misma noción de homogeneidad; no hay duplicación ni drift.
- **Mensajes de error precisos.** Cada inconsistencia se reporta con código (`GEO-001` a `GEO-005`) y la magnitud numérica de la diferencia detectada, lo que facilita el diagnóstico al usuario.
- **Reproducibilidad preservada.** Al no ser configurable, el comportamiento es determinista entre máquinas y versiones.

### Negativas

- **Rigidez en v1.0.** Casos extremos (productos con `pixel_size` extremadamente pequeño donde `atol = 0.01 * pixel_size` se acerca al épsilon del double) podrían requerir excepciones manuales. Mitigación: limitar inicialmente a productos estándar listados en `profiles/`.

### Riesgos

- Si `pyproj` o `rioxarray` cambian la semántica de `CRS.equals` en versiones futuras, la verificación de CRS podría comportarse distinto. Mitigación: pin de `rioxarray>=0.15` en `pyproject.toml` y test de regresión con fixtures de CRS conocidas.

## Notas de implementación

- Definir `tempify.validation.geocoherence.CANONICAL_TOLERANCES: Final[Tolerances]` como dataclass `frozen=True`.
- Exponer helper `is_homogeneous(rasters: list[Raster]) -> tuple[bool, list[Inconsistency]]` que compara todos los archivos contra el primero (referencia) y devuelve la lista completa de inconsistencias encontradas, no solo la primera.
- Reportar inconsistencias con códigos de error:
  - `GEO-001` CRS distinto
  - `GEO-002` Extent fuera de tolerancia
  - `GEO-003` Resolución fuera de tolerancia
  - `GEO-004` Nodata inconsistente
  - `GEO-005` Dimensiones (shape) distintas
- `GeospatialIncoherenceError` (Capa 3) y `AmbiguousStructureError` (Capa 2) deben referenciar estos códigos en sus mensajes.
- Las comparaciones se implementan con `math.isclose` (escalar) y `numpy.isclose` (arrays), nunca con `==` directo sobre floats.
- Cambiar cualquiera de estas tolerancias requiere un nuevo ADR que reemplace el presente.

## Referencias

- ADR-0001: xarray como abstracción central
- ADR-0007: Política de reproducibilidad
- rioxarray: https://corteva.github.io/rioxarray/
- pyproj `CRS.equals`: https://pyproj4.github.io/pyproj/stable/api/crs/crs.html
- GDAL `GeoTransform` precision: https://gdal.org/tutorials/geotransforms_tut.html
- CF Conventions: https://cfconventions.org/
