# ADR-0016: Climatological wraparound como feature de primer orden

**Estado:** Accepted
**Fecha:** 2026-05-16
**Deciders:** Guillermo Fuentes-Jaque
**Contexto técnico:** core-interpolation Sub-fase 2

## Contexto

Cuando el input es una climatología de 12 meses (sin año contextual) o un único año calendario completo, los interpoladores suaves (Linear, PCHIP, Fourier) operan sobre un dominio finito y discreto: 12 puntos anclados en los midpoints canónicos (ADR-0015). Esto produce dos problemas:

1. **Pobre contexto en las fronteras del año.** Una interpolación PCHIP usando solo enero..diciembre no "sabe" que enero del año siguiente vuelve a ser similar a enero del año actual. Sin información extra, los métodos producen extrapolación arbitraria o cierre forzado.

2. **Sub-utilización de la naturaleza cíclica del clima.** Físicamente, los ciclos anuales son periódicos por construcción: la temperatura media de enero es estructuralmente similar de año a año. Tratar diciembre y enero como puntos aislados, sin compartir contexto, es subóptimo.

La práctica común en interpolación climatológica es **extender artificialmente** el dominio antes de interpolar: tratar el último mes (diciembre, índice 12) como si fuera el último mes del año anterior y el primer mes (enero, índice 1) como el primer mes del año siguiente. Esto da, como mínimo, 14 puntos anclados (en lugar de 12) y, dependiendo del método, padding adicional.

## Decisión

`tempify` adopta **climatological wraparound** como feature de primer orden, **activado por defecto** para todos los interpoladores que operan sobre 12 meses. La implementación es transparente al usuario salvo cuando solicita explícitamente desactivarla.

### Reglas formales

1. **Wraparound mínimo (default ON).** Para todo input con `n_months == 12` y `wraparound=True` (default), antes de invocar el kernel se añade al dominio:
   - Un nodo izquierdo con valor `m[11]` y `x` desplazado a `x_in[11] - period`.
   - Un nodo derecho con valor `m[0]` y `x` desplazado a `x_in[0] + period`.

   `period` es el número total de días del año destino (365 o 366 per REQ-003).

2. **Wraparound extendido por método.** Los métodos que se benefician de más contexto pueden extender el padding:
   - **Linear:** padding mínimo (1 nodo por lado → 14 puntos efectivos).
   - **PCHIP / PCHIP+RM:** padding ampliado (2 nodos por lado → 16 puntos efectivos, asegura C¹ continuity).
   - **Fourier:** no requiere padding explícito; la FFT trata implícitamente al input como periódico con `n=12` muestras. La feature "wraparound" para Fourier se manifiesta como `attrs["tempify_wraparound"] = "fft_implicit"`.

3. **Opt-out explícito.** El parámetro `wraparound: bool = True` controla el comportamiento. Con `wraparound=False`:
   - Linear aplica extrapolación constante (`m[0]` antes de `x_in[0]`; `m[11]` después de `x_in[11]`).
   - PCHIP aplica extrapolación polinomial natural de SciPy.
   - Fourier mantiene `fft_implicit` (no se puede "apagar" la naturaleza periódica del FFT; documentar como excepción).

4. **Coexistencia con `cyclic`.** El parámetro existente `cyclic: bool = True` se mantiene como sinónimo retrocompatible de `wraparound` y será deprecado en v0.2.0. En v0.1.0, ambos parámetros son aceptados; si se pasan contradictoriamente, raise `ValueError("cyclic and wraparound must agree")`.

5. **Stamping de procedencia.** El output `DataArray` incluye `attrs["tempify_wraparound"]` con valor:
   - `"climatological_2pt"`: padding mínimo 2 puntos extra (Linear default).
   - `"climatological_4pt"`: padding extendido 4 puntos extra (PCHIP default).
   - `"fft_implicit"`: Fourier.
   - `"off"`: usuario forzó `wraparound=False`.

## Alternativas consideradas

| Alternativa | Razón de rechazo |
|---|---|
| Mantener implícito en `cyclic` (status quo) | El usuario que llamó esto "feature de primer orden" tiene razón: el comportamiento es valioso pero invisible. Formalizar mejora documentación y API. |
| Padding fijo de 4 puntos para todos los métodos | Linear y Fourier no se benefician de tanto padding; PCHIP necesita C¹ que requiere 2 nodos. Decisión por-método es óptima. |
| Replicar todo el ciclo (24 puntos) | Sobreajuste de contexto. Los métodos suaves solo necesitan información local de las fronteras. |
| Hacer `wraparound=False` el default | Pierde calidad significativa en climatologías. La mayoría de inputs reales son climatológicos o anuales únicos. |

## Consecuencias

### Positivas

- **API más expresiva:** el usuario que lee `tempify` entiende explícitamente que la extensión cíclica es un feature, no un detalle interno.
- **Documentación verificable:** el reporte de procesamiento muestra el modo de wraparound aplicado.
- **Compatibilidad retrocompatible:** ningún usuario pierde funcionalidad; `cyclic=True` (default) sigue funcionando idéntico.
- **Trazabilidad científica:** los outputs llevan stamping suficiente para reproducir.

### Negativas

- **Más parámetros visibles:** la firma `interpolate(..., cyclic=True, wraparound=True)` puede confundir hasta que `cyclic` se deprecie en v0.2.0.
- **Tests duplicados:** cada método ahora necesita cubrir wraparound on/off (≥4 tests adicionales por método).

### Riesgos

- **Drift entre `cyclic` y `wraparound`:** si el usuario pasa valores inconsistentes (`cyclic=True, wraparound=False`), el comportamiento debe ser determinista. La regla: raise `ValueError` per Decisión 4.

## Notas de implementación

- En `tempify.interpolation._kernels`, los kernels `linear_kernel`, `pchip_kernel` ya implementan padding cíclico cuando `cyclic=True`. No requiere reescritura del kernel: el cambio es semántico/de naming en las fachadas.
- En `tempify.interpolation.base.BaseInterpolator.interpolate`, añadir parámetro `wraparound: bool = True` con validación de consistencia con `cyclic`.
- En `BaseInterpolator._postprocess`, añadir attribute `tempify_wraparound` con el modo aplicado.
- Para v0.2.0: deprecar `cyclic` con `DeprecationWarning` y migrar tests a `wraparound`.

## Referencias

- [ADR-0015](0015-monthly-value-temporal-placement.md) — Convención midpoint para el posicionamiento temporal.
- [REQ-004 en core-interpolation/requirements.md](../../specs/core-interpolation/requirements.md) — Comportamiento cíclico actual (será actualizado para citar este ADR).
- Práctica común en climatología: Cleveland, W. S. (1979). Robust locally weighted regression. *JASA*, 74(368), 829-836 — discute extensión de dominio para suavizadores en series temporales.
- CF Conventions §7.4 — Climatological time coordinates (relevante para semántica del wrap).
