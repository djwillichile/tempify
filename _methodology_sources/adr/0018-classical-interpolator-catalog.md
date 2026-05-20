# ADR-0018: Catálogo extensible de interpoladores clásicos

**Estado:** Approved
**Fecha:** 2026-05-18
**Deciders:** Guillermo Fuentes-Jaque
**Contexto técnico:** core-interpolation (extensibilidad clásica, no-NN)

## Contexto

La v0.1.0 quedó con 4 métodos de interpolación temporal (`linear`, `pchip`, `pchip_mp`, `fourier`). En la práctica existen varias familias clásicas adicionales que la literatura climatológica usa rutinariamente y que tempify podría incorporar **sin recurrir a redes neuronales** (eso queda para [ADR-0017](0017-neural-interpolator-extensibility.md)).

Tras revisión bibliográfica 2026-05-18 sobre densificación temporal mensual→diaria en clima/teledetección, identificamos las siguientes familias candidatas y su estado relativo respecto a tempify v0.1.x:

| Familia | Mean preserving | Smooth | Coste | Lib | Veredicto |
|---|---|---|---|---|---|
| **Cubic spline natural** | No | C² | bajo | `scipy.interpolate.CubicSpline` | Adoptar en v0.1.4 |
| **Akima 1970** | No | C¹ menos oscilación | bajo | `scipy.interpolate.Akima1DInterpolator` | Adoptar en v0.1.4 |
| **Modified Akima (Makima)** | No | C¹ mejor regiones planas | bajo | SciPy ≥ 1.13 | Considerar v0.1.x |
| **Lai & Kaplan 2022 (Fast MP-spline)** | **Sí** + bounded | C¹ | medio | propio | Adoptar en v0.2.0 |
| **Savitzky-Golay** | No, suaviza | C∞ local | bajo | `scipy.signal.savgol_filter` | Post-procesador opcional v0.2.x |
| **Whittaker-Henderson** | Sí (momentos) | penalizado | medio | propio | Considerar v0.2.x |
| **Gaussian process / Kriging** | No directo | C∞ | alto O(N³) | `gpflow`/`gpytorch` | Diferido (ver ADR-0017) |
| **STL + interp** | Compuesto | dep. método | medio | `statsmodels` | Diferido |

## Decisión

1. **v0.1.4 — adopción rápida de dos métodos de SciPy** (este ADR cubre la implementación):
   - `akima` (`AkimaInterpolator` envuelve `scipy.interpolate.Akima1DInterpolator`)
   - `cubic` (`CubicSplineInterpolator` envuelve `scipy.interpolate.CubicSpline`, condición `not-a-knot` por defecto, periódica si `cyclic=True`)

   Ambos siguen el contrato `BaseInterpolator` existente. Quedan **rechazados para precipitación** vía perfil de variable (per [ADR-0004](0004-precipitation-policy.md)) por ser métodos suaves que pueden producir negativos.

2. **v0.1.4 NO incluye un sabor mean-preserving de estos métodos.** La razón es que `pchip_mp` ya cumple ese rol (Rymes-Myers + PCHIP). Añadir un `cubic_mp` requeriría justificación adicional; se difiere al estudio del paper Lai & Kaplan 2022 que provee una construcción explícita superior.

3. **v0.2.0 — `cubic_mp_lai_kaplan`.** Implementación basada en [Lai & Kaplan 2022, JTECH](https://journals.ametsoc.org/view/journals/atot/39/4/JTECH-D-21-0154.1.xml). Características:
   - Preservación exacta de medias mensuales (∫ raster_diario = raster_mensual sobre cada mes).
   - Bounds opcionales (e.g. `min=0` para precipitación, `max=100` para humedad relativa).
   - C¹ sin overshoots por construcción.

   La nueva spec dedicada `specs/lai-kaplan-interpolation/` se redactará junto con la GUI v0.2.0.

4. **v0.2.x — Savitzky-Golay como capa de post-procesamiento.** Nueva fase opcional del pipeline (después de `interpolate`, antes de `validate_post`):
   - `SavitzkyGolayPostProcessor` con ventana y orden polinómico configurables (defaults `window=15, polyorder=3`).
   - No reemplaza ningún método, suaviza el output diario para reducir esquinas en los nodos.
   - Conmutable por `PipelineConfig.smoothing="savgol" | None`.

5. **v0.2.x — Whittaker-Henderson como `whittaker` interpolator.** Alternativa a `fourier` cuando la señal anual no es estrictamente armónica. Implementación a partir de [Eilers 2003 / Steinacker 2023](https://rmets.onlinelibrary.wiley.com/doi/full/10.1002/joc.8089) usando matrices sparse (O(N) por píxel). Preserva primeros p momentos (incluyendo media si p≥1).

6. **GPR / Kriging y wavelets — diferidos a una futura revisión.** El coste computacional O(N³) los hace inviables para rásters de N≥10⁶ píxeles sin GPU; cuando se aborden, será junto con la integración NN ([ADR-0017](0017-neural-interpolator-extensibility.md)).

## Plan formal por release

### v0.1.4 (esta release)

**In-scope:**

- `src/tempify/interpolation/akima.py` → `AkimaInterpolator`
- `src/tempify/interpolation/cubic.py` → `CubicSplineInterpolator`
- `src/tempify/interpolation/_kernels.py` → `akima_kernel`, `cubic_kernel`
- Update `PipelineConfig.method` Literal con `"akima"` y `"cubic"`
- Update `PipelineCore` dispatcher en `tempify/pipeline/core.py`
- Update perfiles YAML (`profiles/temperature.yaml`, etc.) para aceptar/rechazar los nuevos métodos según la variable
- Update CLI: `tempify convert --method akima|cubic ...`
- Tests unitarios + property tests (hypothesis): `tests/unit/interpolation/test_akima.py`, `test_cubic.py`
- Update docs: README (tabla), landing `docs/index.html` (sección Métodos extendida a 6 filas), notebook tutorial (loop de comparación incluye los 6)
- CHANGELOG `[0.1.4]`

**Out-of-scope para v0.1.4:** mean-preserving variants, Savitzky-Golay, Whittaker, GPR.

### v0.2.0

- `cubic_mp_lai_kaplan` con spec dedicada
- GUI PySide6 (per spec `gui/`)
- Instalador Windows (per spec `packaging/`)
- Integración NN baseline + híbrido (per ADR-0017)

### v0.2.x

- Post-procesador Savitzky-Golay
- Whittaker-Henderson interpolator

## Consecuencias

- **API estable preservada.** Los 4 métodos existentes (`linear`, `pchip`, `pchip_mp`, `fourier`) siguen byte-idénticos. Los nuevos son aditivos.
- **Contrato `BaseInterpolator` validado.** Que dos métodos nuevos entren en v0.1.4 con cero cambios al ABC confirma el supuesto de v0.1.0 sobre extensibilidad clásica.
- **Política de precipitación amplía cobertura.** Los perfiles de variable (`profiles/precipitation.yaml`) rechazan ahora 5 métodos en vez de 3 (`linear`, `pchip`, `pchip_mp`, `fourier`, `akima`, `cubic`), siempre permitiendo override con `--force-method`.
- **Reproducibilidad.** El `tempify_method` attr de los outputs identifica unívocamente el método. Outputs producidos antes de v0.1.4 siguen reproducibles bit-exact.

## Referencias

- Akima, H. (1970). *A New Method of Interpolation and Smooth Curve Fitting Based on Local Procedures.* J. ACM 17(4): 589-602.
- Lai, C.-Y., & Kaplan, J. O. (2022). *A Fast Mean-Preserving Spline for Interpolating Interval Data.* J. Atmos. Oceanic Tech. 39(4): 503-512.
- Steinacker, R. (2023). *Mean value splines and their use for climatological time series.* Int. J. Climatology 43(4): 1842-1856.
- Hofstra, N., et al. (2008). *Comparison of six methods for the interpolation of daily, European climate data.* JGR Atmospheres 113: D21110.
- Fritsch, F. N., & Carlson, R. E. (1980). *Monotone piecewise cubic interpolation.* SIAM J. Numer. Anal. 17(2): 238-246.
- Rymes, M. D., & Myers, D. R. (2001). *Mean preserving algorithm for smoothly interpolating averaged data.* Solar Energy 71(4): 225-231.
- Savitzky, A., & Golay, M. J. E. (1964). *Smoothing and Differentiation of Data by Simplified Least Squares Procedures.* Anal. Chem. 36(8): 1627-1639.
- Eilers, P. H. C. (2003). *A perfect smoother.* Anal. Chem. 75(14): 3631-3636.
