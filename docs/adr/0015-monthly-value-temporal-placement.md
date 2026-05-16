# ADR-0015: Posicionamiento temporal de valores agregados (midpoint convention)

**Status:** Accepted
**Date:** 2026-05-16
**Decision-makers:** Guillermo Fuentes-Jaque
**Contexto técnico:** core-interpolation, temporal-frequency-resolver, io-handlers

## Context

Un valor agregado temporalmente (media mensual, total mensual de precipitación) representa un periodo, no un instante. En el eje `time` de un `xr.DataArray`, ese valor debe colocarse en una marca temporal concreta. Las opciones son:

1. **Inicio del periodo** (ej. enero 2020 -> 2020-01-01).
2. **Fin del periodo** (ej. enero 2020 -> 2020-01-31).
3. **Centroide del periodo** (ej. enero 2020 -> 2020-01-16, midpoint).

La elección no es cosmética: afecta directamente la interpolación temporal. Si los valores mensuales se colocan al inicio del mes, los días de fin de mes quedan sistemáticamente sub-representados (la curva interpolada subestima el valor real del periodo) y se rompe la propiedad mean-preserving en métodos como PCHIP+RM.

**CF Conventions 7.4 (Climatological Statistics)** establece: *"For time-averaged data, the time coordinate is the midpoint of the averaging period."* Es el estándar de referencia para datos climáticos.

Productos reales del ecosistema climático no son uniformes:

- **ISIMIP:** día 15 fijo para todos los meses.
- **NEX-GDDP-CMIP6:** día 16 fijo.
- **ERA5 monthly mean:** midpoint exacto por mes (variable según días).
- **WorldClim:** no especifica; archivos GeoTIFF sin coordenada temporal explícita.
- **CHELSA, CRU-TS:** mezclan convenciones según versión.

tempify necesita una política única y explícita, con overrides controlados, para no propagar ambigüedad aguas abajo.

## Decision

Los valores agregados mensuales se posicionan en el **centroide del periodo de agregación (midpoint)** por defecto, conforme a CF Conventions 7.4. La política se concreta en cuatro reglas:

### 1. Default = midpoint

Fórmula: `month_start + timedelta(days=days_in_month / 2)`, con redondeo half-to-even cuando `days_in_month` es par.

Tabla canónica (calendario gregoriano):

| Mes | Días | Midpoint (día del mes) |
|---|---|---|
| Enero | 31 | 16 |
| Febrero (común) | 28 | 14 |
| Febrero (bisiesto) | 29 | 15 |
| Marzo | 31 | 16 |
| Abril | 30 | 15 |
| Mayo | 31 | 16 |
| Junio | 30 | 15 |
| Julio | 31 | 16 |
| Agosto | 31 | 16 |
| Septiembre | 30 | 15 |
| Octubre | 31 | 16 |
| Noviembre | 30 | 15 |
| Diciembre | 31 | 16 |

### 2. `time_bnds` obligatorio en output CF

Todo output con coordenada `time` mensual declara la variable auxiliar `time_bnds` con celdas `[first_day, first_day_next_month)`. Esto permite a consumidores downstream reconstruir que el `time` es el centroide y no asumir convenciones implícitas.

### 3. Override por archivo (auto-detección)

- Si el input declara `time:bounds` (CF), se respeta y se infiere el anchor real (no se reposiciona).
- Si el filename codifica un día específico parseable (ej. `tas_20150115.tif`), se respeta ese timestamp.
- Solo si ambas señales están ausentes se aplica el default midpoint.

### 4. Override por usuario

`PipelineConfig` expone:

```python
monthly_anchor: Literal["midpoint", "start", "end", "custom"] = "midpoint"
time_axis: list[datetime] | None = None  # requerido si anchor == "custom"
```

La opción `"custom"` exige `time_axis` explícito con longitud igual al número de slices del stack; se valida en construcción del `PipelineConfig`.

## Rationale

### Por qué midpoint y no las alternativas

- **Inicio del mes (`"start"`):** descartado por defecto. Introduce sesgo sistemático: la interpolación entre 2020-01-01 y 2020-02-01 atribuye el valor "enero" al instante 2020-01-01, no al periodo enero completo. Disponible como override por compatibilidad.
- **Fin del mes (`"end"`):** descartado por defecto. Mismo problema en sentido inverso. Disponible como override.
- **Día 15 fijo para todos los meses (ISIMIP):** descartado. Incoherente con febrero (28/29 días) y con meses de 30 días. Adopta una falsa uniformidad a costa de la corrección CF.
- **Centroide en fracción de día (timestamp con hora 12:00):** descartado. Complica interoperabilidad con formatos que solo aceptan resolución diaria (GeoTIFF metadata, nombres de archivo), sin ganancia práctica en interpolación.

### Por qué `time_bnds` obligatorio

Sin `time_bnds`, un consumidor downstream que recibe `time = 2020-01-16` no puede saber si es un instante, un centroide, o un día 16 arbitrario. Declarar `bounds = [2020-01-01, 2020-02-01)` elimina la ambigüedad y es lo que CF exige para datos agregados.

## Consequences

### Positive

- Rigurosamente correcto CF (compatible con xclim, cdo, nco).
- Interpolación sin sesgo: la curva pasa por el valor promedio real del periodo.
- Conservación de media exacta es alcanzable en métodos mean-preserving (PCHIP+RM) sin correcciones ad-hoc.
- Output legible por cualquier herramienta CF-aware sin reinterpretación.

### Negative

- Febrero requiere lógica especial (28 vs 29 días) en la función helper.
- La tabla no es uniforme: usuarios acostumbrados a ISIMIP/NEX-GDDP (día fijo) deben configurar `monthly_anchor` explícitamente para reproducir esos productos.
- `time_bnds` añade complejidad menor a los writers.

### Risks

- Inputs sin metadata temporal explícita (WorldClim típico) requieren asumir midpoint, que puede no coincidir con la intención original del productor. Mitigación: documentar en `impl-log.md` la asunción aplicada y exponerla en logs del pipeline.

## Implementation notes

- Helper: `tempify.constants.monthly_midpoint(year: int, month: int) -> datetime.date`.
- Factory: `tempify.core.temporal.TemporalAxis.from_months(year: int, anchor: Literal["midpoint","start","end"] = "midpoint") -> TemporalAxis`.
- Writers (`io-handlers`): emitir `time_bnds` siempre que el stride de `time` sea mensual.
- Reader (`temporal-frequency-resolver`): si detecta `time:bounds` CF, no reposicionar; si detecta filename con fecha parseable, no reposicionar; si nada, aplicar default.
- Tests obligatorios:
  - `test_midpoint_table_matches_cf_convention` — verifica los 12 valores de la tabla.
  - `test_leap_year_february_day_15` — febrero bisiesto = día 15.
  - `test_time_bnds_emitted_on_monthly_output` — writer produce `time_bnds`.
  - `test_custom_anchor_requires_time_axis` — validación de `PipelineConfig`.

## References

- CF Conventions 7.4 (Climatological Statistics): https://cfconventions.org/Data/cf-conventions/cf-conventions-1.10/cf-conventions.html#climatological-statistics
- ISIMIP protocol §2.3 (Temporal conventions).
- NEX-GDDP-CMIP6 metadata convention.
- ADR-0001: Use xarray.DataArray as central data abstraction.
- specs/core-interpolation/design.md (sección mean-preserving).
- specs/temporal-frequency-resolver/design.md (cascada de inferencia).
