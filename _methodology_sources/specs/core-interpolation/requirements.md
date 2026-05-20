# Requirements — core-interpolation

**Estado:** Approved
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-15
**Última actualización:** 2026-05-16

## 1. Propósito

Implementar los cuatro métodos de interpolación temporal mensual → diaria (Lineal, PCHIP, PCHIP + Rymes-Myers mean-preserving, Fourier multi-armónico) validados experimentalmente sobre datos reales (Quinta Normal 2020) y sintéticos (stack 3×3). Esta spec es el corazón funcional del software; todas las demás specs orbitan alrededor de ella.

El posicionamiento de los nodos de entrada sobre el eje temporal sigue la convención **midpoint** (punto medio canónico de cada mes calendario) per [ADR-0015](../../docs/adr/0015-monthly-value-temporal-placement.md). Esta convención preserva la semántica "valor mensual = promedio del mes" y evita el sesgo sistemático introducido por anchors de inicio/fin.

## 2. Alcance

### In-scope

- Cuatro métodos de interpolación temporal mensual → diaria.
- Soporte para nodos cíclicos (cierre del año).
- Vectorización píxel a píxel sobre `xr.DataArray` con `(month, y, x)`.
- Conservación de la media mensual exacta en el método PCHIP+RM.
- Manejo correcto de años bisiestos vs no bisiestos (365 vs 366 días).
- Propagación correcta de NoData.

### Out-of-scope

- Otras transiciones de frecuencia (anual → mensual, daily → horario). Diferidos a futuras specs.
- Interpolación espacial (la resolución no cambia).
- Métodos estocásticos / weather generators.
- Interpolación de precipitación con métodos suaves (rechazada por diseño). El rechazo de precipitación es enforced por `MethodVariableCompatibilityChecker` en `validation` per ADR-0004; esta spec solo provee los algoritmos.
- Métodos basados en redes neuronales pre-entrenadas (ClimaX, Pangu-Weather, GraphCast, FourCastNet, etc.). Diferidos a v0.2.0 en una spec separada `neural-interpolation`. El ABC `BaseInterpolator` es deliberadamente abierto para soportarlos cuando se aborde. Ver [ADR-0017](../../docs/adr/0017-neural-interpolator-extensibility.md).

## 3. Actores y casos de uso

### Actor 1: Investigador en climatología aplicada

> Como investigador, quiero convertir un stack mensual WorldClim a diario preservando la media mensual, para alimentar modelos de fenología que requieren temperatura diaria sin introducir sesgo en agregados mensuales.

**Caso de uso típico:** El investigador carga el stack mensual con `xarray`, llama a `interpolate(stack, target_freq="daily", method="pchip_mp")`, y obtiene un `DataArray` diario que al re-agregar por mes coincide con el original.

### Actor 2: Docente

> Como docente, quiero mostrar a estudiantes las diferencias entre métodos de interpolación temporal, para enseñar conceptos de conservación de propiedades estadísticas en agregaciones.

**Caso de uso típico:** El docente compara visualmente los 4 métodos sobre un dataset pequeño y muestra las métricas de error.

## 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL provide four interpolation methods: linear, PCHIP, PCHIP+Rymes-Myers (mean-preserving), and Fourier with configurable number of harmonics (1 to 5).

### REQ-002 (Ubiquitous)

THE SYSTEM SHALL expose all interpolation methods through a common interface `BaseInterpolator.interpolate(source: xr.DataArray, target_axis: TemporalAxis) -> xr.DataArray`.

### REQ-003 (Event-driven)

WHEN the user invokes any interpolation method on a monthly stack, THE SYSTEM SHALL return a daily stack with dimensions `(time, y, x)`, where `time` is a CF-compliant daily index covering either 365 or 366 days according to whether the target year is a leap year.

### REQ-004 (Ubiquitous)

THE SYSTEM SHALL handle cyclic boundary conditions by default: December connects smoothly to January without extrapolation artifacts. Esta continuidad es alcanzada vía el mecanismo de **climatological wraparound** formalizado en REQ-015 y ADR-0016, no como un detalle interno del kernel.

### REQ-005a (Optional)

WHERE `cyclic=False` AND method=`linear`, THE SYSTEM SHALL apply constant extrapolation at boundaries.

### REQ-005b (Optional)

WHERE `cyclic=False` AND method ∈ {`pchip`, `pchip_mp`}, THE SYSTEM SHALL apply Fritsch-Carlson polynomial extrapolation.

### REQ-005c (Optional)

WHERE `cyclic=False` AND method=`fourier`, THE SYSTEM SHALL use the natural Fourier periodic boundary (no special handling).

### REQ-006 (State-driven)

WHILE applying PCHIP+Rymes-Myers, THE SYSTEM SHALL iterate until the maximum absolute difference between the reconstructed monthly mean and the original monthly value is below a configurable tolerance (`convergence_tol`, default `1e-6` in the variable's units, configurable via `PchipMeanPreservingInterpolator(convergence_tol=...)`; this is the iterator's stopping criterion, NOT the contractual post-validation tolerance which lives in ADR-0010 nivel 2) or until reaching a maximum number of iterations (default 50).

### REQ-007 (Event-driven)

WHEN PCHIP+Rymes-Myers converges, THE SYSTEM SHALL record the number of iterations used in the output `DataArray.attrs["rymes_myers_iterations"]`.

### REQ-008 (Unwanted)

IF the input has NaN values:
- When ALL 12 months are NaN for a pixel: propagate NaN to all output days.
- When SOME months are NaN for a pixel: raise `PartialNanPixelError` with the pixel index OR (configurable via `nan_policy: Literal['raise', 'propagate_all', 'skip_pixel']`) propagate accordingly.

Default: `nan_policy='raise'` (fail-fast, conservative).

### REQ-009 (Unwanted)

IF the input stack does not contain exactly 12 months (e.g., has 11 or 13), THEN THE SYSTEM SHALL raise `InvalidMonthlyStackError` with a clear message identifying the issue.

### REQ-010 (Ubiquitous)

THE SYSTEM SHALL vectorize over spatial dimensions using `xr.apply_ufunc(..., dask='parallelized', dask_gufunc_kwargs={'output_sizes': {'time': target_days}})` with default chunk size from `tempify.constants.DEFAULT_CHUNK_SIZE` (configurable per call).

### REQ-011 (Unwanted)

IF the input stack has a non-Gregorian CF calendar (`noleap`, `360_day`, `julian`, `all_leap`), THEN THE SYSTEM SHALL raise `UnsupportedCalendarError` with a clear message in Spanish indicating which calendar was detected and that v0.1.0 supports only Gregorian/standard calendars.

### REQ-012 (Unwanted)

IF the input stack has duplicate or non-contiguous month coordinates (e.g., `[1,3,4,...,12]` or `[1,1,2,...]`), THEN THE SYSTEM SHALL raise `InvalidMonthlyStackError` identifying the issue.

### REQ-013 (Ubiquitous)

THE SYSTEM SHALL position each monthly input value at the canonical midpoint of its calendar month (per ADR-0015) when constructing the X-coordinate axis for the smooth interpolators (Linear, PCHIP, Fourier). The PCHIP+Rymes-Myers mean-preserving algorithm operates on monthly aggregates and the midpoint convention applies only to the auxiliary node initialization of the iterator.

### REQ-014 (Optional)

WHERE the caller provides `monthly_anchor='start'`, `'end'`, or `'custom'` instead of the default `'midpoint'`, THE SYSTEM SHALL position monthly values at the requested anchor. With `'custom'`, the caller must additionally provide an explicit `time_axis: list[datetime]` of length 12 (or matching the input length).

### REQ-015 (Ubiquitous)

THE SYSTEM SHALL apply **climatological wraparound** by default when the input has exactly 12 monthly values: month 12 (December) is duplicated as the implicit "month 0" positioned at `x_in[11] - period` (December of the previous year) and month 1 (January) is duplicated as the implicit "month 13" positioned at `x_in[0] + period` (January of the next year). This expands the effective interpolation domain from 12 to at minimum 14 anchor points (per ADR-0016). Individual methods MAY extend the padding further to gain additional context:

- **Linear:** exact 14 effective points (1 padding per side).
- **PCHIP / PCHIP+RM:** 16 effective points (2 padding per side) to ensure C¹ continuity at the December-January boundary.
- **Fourier:** no explicit padding required; the FFT implicitly treats the 12 monthly inputs as periodic samples and the wraparound semantics are inherent. The output is stamped with `attrs["tempify_wraparound"] = "fft_implicit"`.

The output `DataArray` always carries `attrs["tempify_wraparound"]` with one of the canonical values: `"climatological_2pt"`, `"climatological_4pt"`, `"fft_implicit"`, or `"off"`.

### REQ-016 (Optional)

WHERE the caller passes `wraparound=False`, THE SYSTEM SHALL disable the artificial domain extension and treat the 12 monthly inputs as a bare finite sequence. Out-of-range positions (before `x_in[0]` or after `x_in[11]`) are then handled per REQ-005a/b/c by method. Fourier remains periodic by construction (FFT inherent) regardless of `wraparound`; in that case the stamp `attrs["tempify_wraparound"] = "fft_implicit"` is preserved with a `DataArray.attrs["tempify_wraparound_user_request"] = "off"` note for traceability.

### REQ-017 (Unwanted)

IF the caller passes contradictory values of `cyclic` and `wraparound` (e.g., `cyclic=True, wraparound=False`), THEN THE SYSTEM SHALL raise `ValueError("cyclic and wraparound must agree; in v0.2.0 cyclic will be deprecated in favor of wraparound")`. `cyclic` is preserved in v0.1.0 as a retrocompatible synonym of `wraparound` and is scheduled for deprecation in v0.2.0.

## 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Performance | Procesar un stack 12×3000×500 (Chile a 2.5min) en <60s, máquina 8 cores, `scheduler='threaded'` (modo `parallel` per ADR-0007) | Benchmark `tests/benchmark/test_perf_chile_2.5min.py` |
| NFR-002 | Reliability | Conservación de media mensual exacta en PCHIP+RM | Property test `test_rymes_myers_preserves_mean` con hypothesis |
| NFR-003 | Reliability | Reproducibilidad bit-exact en modo `strict` (single-thread, seeded); modo `parallel` garantiza `allclose(rtol=1e-12, atol=1e-15)` per ADR-0007 | Tests separados: `test_reproducibility_strict_md5_match`, `test_reproducibility_parallel_allclose` |
| NFR-004 | Memory | No cargar más de 1GB en RAM por chunk con default chunk_size=512 | Profiling con memray |
| NFR-005 | Usability | Mensajes de error en español por defecto, con código de error referenciable | Test `test_error_messages_spanish` |

## 6. Criterios de aceptación

- [ ] REQ-001 cubierto por tests `test_linear_basic`, `test_pchip_basic`, `test_pchip_mp_basic`, `test_fourier_basic`
- [ ] REQ-002 cubierto por test `test_base_interpolator_protocol`
- [ ] REQ-003 cubierto por test `test_output_has_366_days_in_leap_year` y `test_output_has_365_days_in_non_leap_year`
- [ ] REQ-004 cubierto por test `test_cyclic_boundary_continuity`
- [ ] REQ-005a/b/c cubiertos por tests `test_non_cyclic_linear_constant`, `test_non_cyclic_pchip_polynomial`, `test_non_cyclic_fourier_periodic`
- [ ] REQ-006 cubierto por test `test_rymes_myers_converges`
- [ ] REQ-007 cubierto por test `test_rymes_myers_records_iterations`
- [ ] REQ-008 cubierto por tests `test_nan_all_propagation`, `test_partial_nan_raises`, `test_nan_policy_propagate_all`, `test_nan_policy_skip_pixel`
- [ ] REQ-009 cubierto por test `test_invalid_monthly_count_raises`
- [ ] REQ-010 cubierto por test `test_vectorized_with_dask`
- [ ] REQ-011 cubierto por test `test_non_gregorian_calendar_raises`
- [ ] REQ-012 cubierto por test `test_duplicate_or_noncontiguous_months_raises`
- [ ] REQ-013 cubierto por tests `test_temporal_axis_midpoint_table`, `test_linear_input_nodes_at_midpoint`
- [ ] REQ-014 cubierto por tests `test_monthly_anchor_start_shifts_nodes`, `test_custom_anchor_requires_explicit_dates`
- [ ] REQ-015 cubierto por tests `test_climatological_wraparound_adds_2pt_linear`, `test_climatological_wraparound_adds_4pt_pchip`, `test_wraparound_attr_stamped`
- [ ] REQ-016 cubierto por tests `test_wraparound_false_disables_extension_linear`, `test_wraparound_false_disables_extension_pchip`
- [ ] REQ-017 cubierto por test `test_contradictory_cyclic_wraparound_raises`
- [ ] NFR-001 medido y dentro del umbral
- [ ] NFR-002 verificado con 100+ casos de hypothesis
- [ ] NFR-003 verificado en ambos modos (`strict` y `parallel`) per ADR-0007
- [ ] Documentación: notas metodológicas en `docs/methodology/` para cada método con referencias
- [ ] Tutorial: notebook `docs/tutorials/01_interpolation_methods_comparison.ipynb`
- [ ] CHANGELOG actualizado

## 7. Dependencias y supuestos

### Specs relacionadas

- Bloqueada por: ninguna (es la spec fundacional).
- Bloquea: pipeline, [io-handlers](../io-handlers/requirements.md), [validation](../validation/requirements.md), [cli](../cli/requirements.md).
- Independiente de: [structure-detection](../structure-detection/requirements.md) (los `BaseInterpolator` reciben `xr.DataArray` ya detectado y validado).

### Supuestos

- El usuario entiende que ningún método mensual→diario puede recuperar la varianza sinóptica diaria real. Esto se comunica claramente en la documentación.
- Para v1.0 solo se soporta transición 12 meses → 365/366 días. Otras transiciones diferidas.

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Pérdida de varianza diaria interpretada como "bug" por usuarios sin contexto | Media | Medio | Documentación clara + reporte automático que comunica la limitación intrínseca |
| Rymes-Myers no converge en casos patológicos | Baja | Medio | Tope de iteraciones + log warning; retornar mejor aproximación |
| Performance Dask pobre por chunks mal dimensionados | Media | Bajo | chunk_size configurable + recomendación en docs |

## 8. Referencias

- Fritsch, F. N., & Carlson, R. E. (1980). Monotone piecewise cubic interpolation. *SIAM Journal on Numerical Analysis*, 17(2), 238-246.
- Rymes, M. D., & Myers, D. R. (2001). Mean preserving algorithm for smoothly interpolating averaged data. *Solar Energy*, 71(4), 225-231.
- Validación experimental previa: experimento Quinta Normal 2020 (ver `docs/methodology/empirical-validation-quinta-normal.md`).
- [ADR-0015](../../docs/adr/0015-monthly-value-temporal-placement.md) — Convención midpoint para el posicionamiento temporal de valores mensuales.
- [ADR-0016](../../docs/adr/0016-climatological-wraparound.md) — Climatological wraparound como feature de primer orden, parámetro `wraparound` y semántica por método.
- [ADR-0017](../../docs/adr/0017-neural-interpolator-extensibility.md) — Extensibilidad para métodos basados en redes neuronales (deferred a v0.2.0).
- CF Conventions §7.4 — Climatological statistics y semántica de celdas de tiempo (https://cfconventions.org/Data/cf-conventions/cf-conventions-1.11/cf-conventions.html#climatological-statistics).
