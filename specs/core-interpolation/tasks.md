# Tasks — core-interpolation

**Estado:** Approved
**Owner:** Guillermo Fuentes-Jaque
**Design doc:** [design.md](design.md)
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-16

## Reglas para tasks

Cada task debe ser:

- **Atómica:** completable en ≤ 4h, en un commit, tocando ≤ 3 archivos no relacionados.
- **Verificable:** tiene un criterio de done observable.
- **TDD estricto:** test (rojo) → impl (verde) → refactor opcional. No se mezclan en la misma task.
- **Trazable:** declara REQ/NFR/ADR cubierto cuando aplica.

Convención de IDs: `task-<fase>.<n>`. Bloqueos explícitos por ID.

## Trazabilidad cruzada (cobertura mandatoria)

| Elemento | Cubierto por tasks |
|---|---|
| REQ-001 | task-2.1.2, task-2.2.2, task-2.3.2, task-2.4.2 |
| REQ-002 | task-1.6, task-1.7 |
| REQ-003 | task-1.3, task-1.4, task-2.1.3 |
| REQ-004 | task-2.2.4, task-2.4.3 |
| REQ-005a | task-2.1.4 |
| REQ-005b | task-2.2.5 |
| REQ-005c | task-2.4.3 |
| REQ-006 | task-2.3.2, task-2.3.3 |
| REQ-007 | task-2.3.4 |
| REQ-008 | task-2.5.1, task-2.5.2 |
| REQ-009 | task-1.5, task-2.6.1 |
| REQ-010 | task-2.7.1, task-2.7.2 |
| REQ-011 | task-1.5, task-2.6.2 |
| REQ-012 | task-1.5, task-2.6.1 |
| REQ-013 | task-1.4 |
| REQ-014 | task-1.4b, task-2.6.3 |
| NFR-001 | task-3.3 |
| NFR-002 | task-2.3.5 |
| NFR-003 | task-3.4, task-3.5 |
| NFR-004 | task-3.6 |
| NFR-005 | task-2.6.4 |
| ADR-0001 | task-2.7.1 (xarray.DataArray central) |
| ADR-0002 | task-2.7.1 (Dask vía apply_ufunc) |
| ADR-0004 | (out-of-scope; enforced en Capa 3) — nota en task-1.1 README |
| ADR-0007 | task-3.4, task-3.5 |
| ADR-0010 | task-1.2 (constantes Nivel 1), task-2.3.2 (criterio de parada) |
| ADR-0015 | task-1.4, task-1.4b |

---

## Fase 1 — Fundamentos

### task-1.1: Scaffolding del paquete `tempify.interpolation`

**Tipo:** chore
**Estimación:** 1h
**Bloquea:** task-1.2, task-1.3, task-1.5, task-1.6
**Bloqueada por:** —

**Descripción:** Crear estructura del paquete con `__init__.py` que exporta los símbolos públicos (placeholders no implementados aún). Crear módulos vacíos `linear.py`, `pchip.py`, `pchip_mp.py`, `fourier.py`, `_kernels.py`, `base.py`, `exceptions.py`. Configurar `src/tempify/interpolation/py.typed` para PEP 561.

**Criterio de done:**
- [ ] `from tempify.interpolation import LinearInterpolator, PchipInterpolator, PchipMeanPreservingInterpolator, FourierInterpolator, BaseInterpolator, TemporalAxis` importa (clases pueden ser stubs `class X: pass`).
- [ ] `ruff check` clean.
- [ ] `mypy --strict` no reporta errores en el paquete (stubs vacíos OK).
- [ ] Comentario al inicio de `__init__.py` referencia ADR-0004 (precipitación se rechaza en Capa 3, no aquí).

**Archivos:**
- `src/tempify/interpolation/__init__.py`
- `src/tempify/interpolation/{base,linear,pchip,pchip_mp,fourier,_kernels,exceptions}.py`
- `src/tempify/interpolation/py.typed`

### task-1.2: Constantes del paquete

**Tipo:** impl
**Estimación:** 0.5h
**Bloquea:** task-1.6, task-2.3.2, task-2.4.2
**Bloqueada por:** task-1.1

**Descripción:** Definir constantes en `tempify.constants` con tipo `Final` per design §4.2. Incluye `DEFAULT_CHUNK_SIZE`, `DEFAULT_RM_CONVERGENCE_TOL` (ADR-0010 Nivel 1), `DEFAULT_RM_MAX_ITER`, `FOURIER_MIN_HARMONICS`, `FOURIER_MAX_HARMONICS`.

**Criterio de done:**
- [ ] Todas las constantes tipadas `Final`.
- [ ] Test `test_constants_are_final_and_have_expected_values` cubre los 5 valores.
- [ ] Docstring del módulo cita ADR-0010 para `DEFAULT_RM_CONVERGENCE_TOL`.

**Archivos:**
- `src/tempify/constants.py`
- `tests/unit/test_constants.py`

### task-1.3 (test): `TemporalAxis` — esqueleto y `n_days` (REQ-003)

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-1.4
**Bloqueada por:** task-1.1

**Descripción:** Escribir tests que verifican: (a) construcción mínima con `start`/`end`; (b) `n_days == 365` para año no bisiesto (2023); (c) `n_days == 366` para bisiesto (2024); (d) `dataclass` frozen + slots; (e) `start > end` → `ValueError`.

**Criterio de done:**
- [ ] 5 tests rojos (la clase aún es stub).
- [ ] Tests parametrizados por año bisiesto/no bisiesto.

**Archivos:**
- `tests/unit/interpolation/test_temporal_axis.py`

### task-1.4 (impl): `TemporalAxis.from_months` con anchor `midpoint` (REQ-013, ADR-0015)

**Tipo:** impl
**Estimación:** 3h
**Bloquea:** task-1.4b, task-2.1.2, task-2.2.2, task-2.4.2
**Bloqueada por:** task-1.3

**Descripción:** Implementar `TemporalAxis` (dataclass frozen+slots), `from_months(year, anchor='midpoint')`, `n_days`, `to_cftime_index()`, y helper interno `monthly_midpoint(year, month) -> datetime` per ADR-0015 tabla canónica. Incluye ajuste de febrero en bisiesto (día 15 entero per ADR-0015 §bisiestos).

**Criterio de done:**
- [ ] Tests de task-1.3 pasan.
- [ ] Nuevo test `test_monthly_midpoint_canonical_table_2023` cubre los 12 valores contra tabla ADR-0015.
- [ ] Nuevo test `test_february_midpoint_2024_is_day_15` (REQ-013).
- [ ] `mypy --strict`, `ruff` clean.
- [ ] Docstring NumPy completa con citas a ADR-0015 y CF §7.4.

**Archivos:**
- `src/tempify/interpolation/base.py` (TemporalAxis + monthly_midpoint)
- `tests/unit/interpolation/test_temporal_axis.py` (extensión)

### task-1.4b (impl): `monthly_anchor` `start` / `end` / `custom` (REQ-014)

**Tipo:** impl
**Estimación:** 2h
**Bloquea:** task-2.6.3
**Bloqueada por:** task-1.4

**Descripción:** Extender `TemporalAxis` con `monthly_anchor: Literal["midpoint","start","end","custom"]` y `custom_dates: list[datetime] | None`. Validaciones en `__post_init__`: `custom` exige `custom_dates is not None`, `len == 12`, estrictamente creciente.

**Criterio de done:**
- [ ] Tests rojos→verdes: `test_anchor_start_returns_day_1`, `test_anchor_end_returns_last_day_of_month`, `test_custom_without_dates_raises_ValueError`, `test_custom_wrong_length_raises`, `test_custom_non_increasing_raises`.
- [ ] Tabla de DOYs accesible vía `TemporalAxis.monthly_anchor_doys()`.

**Archivos:**
- `src/tempify/interpolation/base.py`
- `tests/unit/interpolation/test_temporal_axis_anchors.py`

### task-1.5: Excepciones tipadas con mensajes en español (REQ-009, REQ-011, REQ-012, NFR-005)

**Tipo:** impl
**Estimación:** 1h
**Bloquea:** task-2.6.1, task-2.6.2, task-2.6.4
**Bloqueada por:** task-1.1

**Descripción:** Implementar `InterpolationError`, `InvalidMonthlyStackError`, `UnsupportedCalendarError`, `PartialNanPixelError` per design §3.3. Cada una con factory de mensaje en español que incluye contexto (calendario detectado, índice del píxel, conteo de meses).

**Criterio de done:**
- [ ] 4 clases existen y heredan correctamente.
- [ ] Tests `test_each_exception_has_spanish_message` y `test_exceptions_carry_context_payload`.
- [ ] Códigos de error tipo `TEMPIFY-INT-001..004` documentados como atributo de clase `code: ClassVar[str]` (NFR-005).

**Archivos:**
- `src/tempify/interpolation/exceptions.py`
- `tests/unit/interpolation/test_exceptions.py`

### task-1.6 (test): `BaseInterpolator` — protocolo ABC (REQ-002)

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** task-1.7
**Bloqueada por:** task-1.1, task-1.2

**Descripción:** Tests que verifican: (a) `BaseInterpolator` no es instanciable directamente; (b) firma exacta de `interpolate(source, target_axis, *, cyclic, nan_policy, chunk_size)`; (c) cualquier subclase concreta sin `interpolate` levanta `TypeError`.

**Criterio de done:**
- [ ] 3 tests rojos.

**Archivos:**
- `tests/unit/interpolation/test_base_interpolator.py`

### task-1.7 (impl): `BaseInterpolator` ABC + validaciones comunes

**Tipo:** impl
**Estimación:** 2.5h
**Bloquea:** todas las task-2.*
**Bloqueada por:** task-1.5, task-1.6

**Descripción:** Implementar ABC con `interpolate` abstracto y métodos protegidos `_validate_month_count`, `_validate_month_contiguity`, `_validate_calendar`, `_validate_nan_policy` (firma; lógica concreta en task-2.5/2.6). Stamping de `attrs["tempify_method"]` en hook `_postprocess`.

**Criterio de done:**
- [ ] Tests task-1.6 pasan.
- [ ] Test `test_base_postprocess_stamps_method_attr`.
- [ ] `mypy --strict` clean.

**Archivos:**
- `src/tempify/interpolation/base.py`
- `tests/unit/interpolation/test_base_interpolator.py` (extensión)

### task-1.8: Fixtures sintéticos compartidos

**Tipo:** chore
**Estimación:** 1.5h
**Bloquea:** task-2.1.1+ (todas las fases test)
**Bloqueada por:** task-1.4

**Descripción:** Crear `conftest.py` con fixtures session-scoped: `monthly_3x3_smooth` (ciclo sinusoidal sintético), `monthly_3x3_partial_nan`, `monthly_3x3_all_nan_pixel`, `monthly_3x3_constant`, `temporal_axis_2023` (no bisiesto), `temporal_axis_2024` (bisiesto). Determinismo con `np.random.default_rng(seed=42)`.

**Criterio de done:**
- [ ] 6 fixtures disponibles desde `tests/unit/interpolation/`.
- [ ] Test `test_fixtures_are_deterministic` corre dos veces y compara MD5.

**Archivos:**
- `tests/unit/interpolation/conftest.py`

---

## Fase 2 — Métodos incrementales

### Sub-fase 2.1 — `LinearInterpolator`

#### task-2.1.1 (test): kernel lineal 1D — caso constante y caso lineal exacto

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.1.2
**Bloqueada por:** task-1.8

**Descripción:** Tests del kernel `_kernels.linear_kernel(m, x_in, x_out, cyclic)`: (a) input constante 12 → output 365 constantes; (b) input lineal en `m` → output lineal en `x_out` (error L∞ < 1e-12 atol).

**Archivos:**
- `tests/unit/interpolation/test_linear.py`

#### task-2.1.2 (impl): kernel + fachada `LinearInterpolator` (REQ-001, ciclo cíclico)

**Tipo:** impl
**Estimación:** 2.5h
**Bloquea:** task-2.1.3, task-2.1.4
**Bloqueada por:** task-2.1.1, task-1.7

**Descripción:** Implementar `_kernels.linear_kernel` (NumPy puro) y `LinearInterpolator` que vectoriza vía `apply_ufunc`. Caso `cyclic=True` por defecto.

**Criterio de done:**
- [ ] Tests task-2.1.1 pasan (verde).
- [ ] Test `test_linear_basic` cubre fixture `monthly_3x3_smooth`.
- [ ] Docstring NumPy completa.

**Archivos:**
- `src/tempify/interpolation/_kernels.py`
- `src/tempify/interpolation/linear.py`
- `tests/unit/interpolation/test_linear.py`

#### task-2.1.3 (test+impl): días de salida — 365/366 según bisiesto (REQ-003)

**Tipo:** test+impl
**Estimación:** 1.5h
**Bloquea:** —
**Bloqueada por:** task-2.1.2

**Descripción:** Tests `test_output_has_365_days_in_non_leap_year` (2023) y `test_output_has_366_days_in_leap_year` (2024). Ajustar `LinearInterpolator` si necesario para usar `target_axis.n_days`.

**Archivos:**
- `tests/unit/interpolation/test_linear.py`
- `src/tempify/interpolation/linear.py`

#### task-2.1.4 (test+impl): extrapolación constante `cyclic=False` (REQ-005a)

**Tipo:** test+impl
**Estimación:** 1h
**Bloquea:** —
**Bloqueada por:** task-2.1.2

**Descripción:** Tests `test_non_cyclic_linear_constant`: para `t < DOY(1)` el output equals `m[0]`; para `t > DOY(12)` equals `m[11]`.

**Archivos:**
- `tests/unit/interpolation/test_linear.py`
- `src/tempify/interpolation/_kernels.py`, `linear.py`

### Sub-fase 2.2 — `PchipInterpolator`

#### task-2.2.1 (test): kernel PCHIP 1D — suavidad y monotonicidad

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.2.2
**Bloqueada por:** task-1.8

**Descripción:** Tests: (a) input puramente sinusoidal anual → error L∞ < 0.01; (b) input monótono → output monótono local en cada tramo.

**Archivos:**
- `tests/unit/interpolation/test_pchip.py`

#### task-2.2.2 (impl): `_kernels.pchip_kernel` + fachada `PchipInterpolator` (REQ-001)

**Tipo:** impl
**Estimación:** 2.5h
**Bloquea:** task-2.2.3, task-2.2.4, task-2.2.5
**Bloqueada por:** task-2.2.1, task-1.4, task-1.7

**Descripción:** Wrap `scipy.interpolate.PchipInterpolator` por píxel con extensión cíclica de 2 nodos a cada lado (design §5.2). Fachada vía `apply_ufunc`.

**Archivos:**
- `src/tempify/interpolation/_kernels.py`
- `src/tempify/interpolation/pchip.py`

#### task-2.2.3 (test+impl): PCHIP extensión cíclica — construcción del vector extendido

**Tipo:** test+impl
**Estimación:** 1h
**Bloquea:** task-2.2.4
**Bloqueada por:** task-2.2.2

**Descripción:** Test `test_pchip_cyclic_extension_uses_2_pad_nodes` (verifica `m_ext = [m[10], m[11], m[0..11], m[0], m[1]]`) y DOYs correspondientes con desplazamientos `+/- 12 meses`.

**Archivos:**
- `tests/unit/interpolation/test_pchip.py`

#### task-2.2.4 (test): continuidad C¹ frontera Dic/Ene (REQ-004)

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** —
**Bloqueada por:** task-2.2.3

**Descripción:** Test `test_cyclic_boundary_continuity` (PCHIP variant): `|d[N-1] - d[0]| < 1e-6` y derivada numérica izquierda ≈ derivada derecha en el cierre.

**Archivos:**
- `tests/unit/interpolation/test_pchip.py`

#### task-2.2.5 (test+impl): extrapolación polinomial `cyclic=False` (REQ-005b)

**Tipo:** test+impl
**Estimación:** 1h
**Bloquea:** —
**Bloqueada por:** task-2.2.2

**Descripción:** Test `test_non_cyclic_pchip_polynomial`: `cyclic=False` → scipy aplica extrapolación Fritsch-Carlson natural; verificar derivada continua en bordes.

**Archivos:**
- `tests/unit/interpolation/test_pchip.py`
- `src/tempify/interpolation/pchip.py`

### Sub-fase 2.3 — `PchipMeanPreservingInterpolator` (Rymes-Myers)

#### task-2.3.1 (test): iterator Rymes-Myers — caso constante

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.3.2
**Bloqueada por:** task-2.2.2

**Descripción:** Test `test_rm_iterator_constant_converges_immediately`: input constante, espera convergencia en k=1 con `delta == 0`.

**Archivos:**
- `tests/unit/interpolation/test_pchip_mp.py`

#### task-2.3.2 (impl): kernel `pchip_rm_kernel` con loop iterativo (REQ-001, REQ-006)

**Tipo:** impl
**Estimación:** 3.5h
**Bloquea:** task-2.3.3, task-2.3.4, task-2.3.5
**Bloqueada por:** task-2.3.1, task-1.2

**Descripción:** Implementar algoritmo Rymes-Myers per design §5.3: init con PCHIP, loop hasta `max(|delta|) < convergence_tol` o `k == max_iterations`. Kernel `smooth_distribute` 3-point moving average.

**Criterio de done:**
- [ ] Test task-2.3.1 pasa.
- [ ] Test `test_rymes_myers_converges` (REQ-006): caso sinusoidal converge en `k < max_iterations` con tol 1e-6.
- [ ] Test `test_pchip_mp_basic` reconstruye media mensual exacta dentro de `convergence_tol`.

**Archivos:**
- `src/tempify/interpolation/_kernels.py`
- `src/tempify/interpolation/pchip_mp.py`

#### task-2.3.3 (test+impl): tope `max_iterations` con warning (REQ-006)

**Tipo:** test+impl
**Estimación:** 1h
**Bloquea:** task-2.3.4
**Bloqueada por:** task-2.3.2

**Descripción:** Construir caso patológico (input que no converge en 5 iter), `max_iterations=5`. Test `test_rymes_myers_hits_max_iterations` verifica: (a) no raise; (b) `warnings.warn` capturado con `UserWarning`; (c) `attrs["rymes_myers_converged"] == False`.

**Archivos:**
- `tests/unit/interpolation/test_pchip_mp.py`
- `src/tempify/interpolation/pchip_mp.py`

#### task-2.3.4 (test): `attrs["rymes_myers_iterations"]` stamping (REQ-007)

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** —
**Bloqueada por:** task-2.3.3

**Descripción:** Test `test_rymes_myers_records_iterations`: `da.attrs["rymes_myers_iterations"]` es int ≥ 1 tras corrida.

**Archivos:**
- `tests/unit/interpolation/test_pchip_mp.py`

#### task-2.3.5 (property test): conservación de la media (NFR-002)

**Tipo:** test
**Estimación:** 2h
**Bloquea:** —
**Bloqueada por:** task-2.3.2

**Descripción:** Property test con `hypothesis` (mín. 100 ejemplos): para cualquier `m ∈ R^12` con `|m_i| < 1e3`, `assert_allclose(rebuilt_monthly_mean, m, atol=DEFAULT_RM_CONVERGENCE_TOL)`. Strategy con `floats(min_value=-1e3, max_value=1e3, allow_nan=False)`.

**Archivos:**
- `tests/unit/interpolation/test_properties.py`

### Sub-fase 2.4 — `FourierInterpolator`

#### task-2.4.1 (test): kernel Fourier — armónico puro

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.4.2
**Bloqueada por:** task-1.8

**Descripción:** Test `test_fourier_pure_harmonic_recovered`: input `m[i] = cos(2π·k·i/12)` con `k ∈ {1,2,3}` → reconstrucción exacta (`atol=1e-12`) con `n_harmonics >= k`.

**Archivos:**
- `tests/unit/interpolation/test_fourier.py`

#### task-2.4.2 (impl): kernel + fachada `FourierInterpolator` (REQ-001)

**Tipo:** impl
**Estimación:** 2.5h
**Bloquea:** task-2.4.3, task-2.4.4
**Bloqueada por:** task-2.4.1, task-1.2, task-1.4

**Descripción:** Implementar `_kernels.fourier_kernel` per design §5.4 (rfft + truncamiento). Validar `n_harmonics ∈ [FOURIER_MIN_HARMONICS, FOURIER_MAX_HARMONICS]` en `__init__` → `ValueError`.

**Archivos:**
- `src/tempify/interpolation/_kernels.py`
- `src/tempify/interpolation/fourier.py`

#### task-2.4.3 (test+impl): boundary periódica natural (REQ-004, REQ-005c)

**Tipo:** test+impl
**Estimación:** 0.5h
**Bloquea:** —
**Bloqueada por:** task-2.4.2

**Descripción:** Tests `test_non_cyclic_fourier_periodic` (no diferencia con cyclic=True para Fourier) y `test_fourier_cyclic_boundary_continuity` (frontera C∞).

**Archivos:**
- `tests/unit/interpolation/test_fourier.py`

#### task-2.4.4 (test): validación `n_harmonics` fuera de rango

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** —
**Bloqueada por:** task-2.4.2

**Descripción:** Test `test_fourier_n_harmonics_out_of_range` con `n_harmonics ∈ {0, 6, 100, -1}` → `ValueError`. Cubre prohibición explícita del armónico 6 (Nyquist folded).

**Archivos:**
- `tests/unit/interpolation/test_fourier.py`

### Sub-fase 2.5 — Política NaN transversal (REQ-008)

#### task-2.5.1 (test): tres políticas NaN

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-2.5.2
**Bloqueada por:** task-1.5

**Descripción:** Tests parametrizados sobre los 4 métodos: `test_nan_all_propagation` (todos NaN → todos NaN, no raise); `test_partial_nan_raises` con `nan_policy='raise'`; `test_nan_policy_propagate_all`; `test_nan_policy_skip_pixel`.

**Archivos:**
- `tests/unit/interpolation/test_nan_policy.py`

#### task-2.5.2 (impl): `_validate_nan_policy` en `BaseInterpolator`

**Tipo:** impl
**Estimación:** 2h
**Bloquea:** —
**Bloqueada por:** task-2.5.1, task-2.1.2, task-2.2.2, task-2.3.2, task-2.4.2

**Descripción:** Implementar lógica común de detección de píxeles all-NaN vs partial-NaN. Hook llamado por las 4 fachadas antes de `apply_ufunc`. Property test `test_all_nan_propagation_property` (hypothesis).

**Archivos:**
- `src/tempify/interpolation/base.py`
- `tests/unit/interpolation/test_nan_policy.py`
- `tests/unit/interpolation/test_properties.py` (extensión)

### Sub-fase 2.6 — Validación de stack y calendario

#### task-2.6.1 (test+impl): conteo y contigüidad de meses (REQ-009, REQ-012)

**Tipo:** test+impl
**Estimación:** 1.5h
**Bloquea:** —
**Bloqueada por:** task-1.5, task-1.7

**Descripción:** Tests `test_invalid_monthly_count_raises` (11 y 13 meses) y `test_duplicate_or_noncontiguous_months_raises` (`[1,3,4,...]`, `[1,1,2,...]`). Implementar `_validate_month_count` y `_validate_month_contiguity` en `BaseInterpolator`.

**Archivos:**
- `tests/unit/interpolation/test_validation.py`
- `src/tempify/interpolation/base.py`

#### task-2.6.2 (test+impl): calendarios no gregorianos (REQ-011)

**Tipo:** test+impl
**Estimación:** 1.5h
**Bloquea:** —
**Bloqueada por:** task-1.5, task-1.7

**Descripción:** Parametrizado sobre `noleap`, `360_day`, `julian`, `all_leap` → `UnsupportedCalendarError` con mensaje que identifica el calendario. Implementar `_validate_calendar`.

**Archivos:**
- `tests/unit/interpolation/test_validation.py`
- `src/tempify/interpolation/base.py`

#### task-2.6.3 (test+impl): `monthly_anchor='custom'` end-to-end (REQ-014)

**Tipo:** test+impl
**Estimación:** 1.5h
**Bloquea:** —
**Bloqueada por:** task-1.4b, task-2.1.2

**Descripción:** Tests `test_monthly_anchor_start_shifts_nodes` (Linear con `start` vs `midpoint` muestra desfase esperado) y `test_custom_anchor_requires_explicit_dates`.

**Archivos:**
- `tests/unit/interpolation/test_anchors_integration.py`

#### task-2.6.4 (test): mensajes en español (NFR-005)

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** —
**Bloqueada por:** task-2.6.1, task-2.6.2

**Descripción:** Test `test_error_messages_spanish`: itera sobre las 4 excepciones, verifica presencia de marcadores castellanos (e.g., "calendario no soportado", "stack mensual inválido", "píxel con NaN parcial") y código `TEMPIFY-INT-*`.

**Archivos:**
- `tests/unit/interpolation/test_exceptions.py` (extensión)

### Sub-fase 2.7 — Vectorización Dask

#### task-2.7.1 (test+impl): `apply_ufunc` con `dask='parallelized'` (REQ-010, ADR-0001, ADR-0002)

**Tipo:** test+impl
**Estimación:** 2.5h
**Bloquea:** task-2.7.2, task-3.3, task-3.4
**Bloqueada por:** task-2.1.2, task-2.2.2, task-2.3.2, task-2.4.2

**Descripción:** Refactor de las 4 fachadas para invocar `xr.apply_ufunc(..., dask='parallelized', dask_gufunc_kwargs={'output_sizes': {'time': target_days}})`. Default `chunk_size` desde `tempify.constants.DEFAULT_CHUNK_SIZE`.

**Criterio de done:**
- [ ] Test `test_vectorized_with_dask`: salida es lazy (`isinstance(da.data, dask.array.Array)`).
- [ ] Test `test_eager_vs_lazy_match` (`.compute() == eager`) para los 4 métodos.
- [ ] Cobertura ≥ 85% en `interpolation/*`.

**Archivos:**
- `src/tempify/interpolation/{linear,pchip,pchip_mp,fourier}.py`
- `tests/unit/interpolation/test_dask_vectorization.py`

#### task-2.7.2 (test): `chunk_size` configurable + override

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** —
**Bloqueada por:** task-2.7.1

**Descripción:** Test `test_chunk_size_override_applied`: pasar `chunk_size=128` → chunks resultantes coherentes.

**Archivos:**
- `tests/unit/interpolation/test_dask_vectorization.py`

---

## Fase 3 — Documentación, integración y NFRs

### task-3.1: Docstrings NumPy completas para todas las clases públicas

**Tipo:** docs
**Estimación:** 2h
**Bloquea:** —
**Bloqueada por:** task-2.7.1

**Descripción:** Revisión de docstrings de `BaseInterpolator`, `TemporalAxis`, 4 interpoladores, 4 excepciones. Formato NumPy completo (Parameters, Returns, Raises, Notes, References, Examples). Verificar con `pydocstyle --convention=numpy`.

**Criterio de done:**
- [ ] `pydocstyle` sin warnings en `src/tempify/interpolation/*`.
- [ ] Cada método público tiene ejemplo ejecutable en `Examples`.

**Archivos:**
- `src/tempify/interpolation/{base,linear,pchip,pchip_mp,fourier,exceptions}.py`

### task-3.2: Notebook tutorial — comparación de 4 métodos

**Tipo:** docs
**Estimación:** 3h
**Bloquea:** —
**Bloqueada por:** task-2.7.1

**Descripción:** Notebook que: (1) carga stack sintético; (2) corre los 4 métodos; (3) genera plot 2x2 con series diarias; (4) calcula RMSE vs daily reference de Quinta Normal 2020; (5) muestra reconstrucción de media mensual (PCHIP+RM exacta, otros con sesgo).

**Criterio de done:**
- [ ] Notebook ejecuta end-to-end sin error.
- [ ] Enlazado desde README.
- [ ] CI: `nbmake` o `jupyter nbconvert --execute` pasa.

**Archivos:**
- `docs/tutorials/01_interpolation_methods_comparison.ipynb`

### task-3.3: Benchmark Chile 2.5 arc-min (NFR-001)

**Tipo:** test
**Estimación:** 2h
**Bloquea:** —
**Bloqueada por:** task-2.7.1

**Descripción:** Benchmark `pytest-benchmark` con stack `12×3000×500`, `scheduler='threaded'`, 8 cores. Umbral `< 60 s` per NFR-001 (ADR-0007 modo `parallel`). Reporte JSON en `tests/benchmark/results/`.

**Criterio de done:**
- [ ] Benchmark corre y reporta tiempos < 60 s en máquina target.
- [ ] Resultado serializado a JSON por método.

**Archivos:**
- `tests/benchmark/test_perf_chile_2.5min.py`
- `tests/benchmark/results/.gitkeep`

### task-3.4: Test reproducibilidad strict (NFR-003, ADR-0007)

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** —
**Bloqueada por:** task-2.7.1

**Descripción:** Test `test_reproducibility_strict_md5_match`: `dask.config.set(scheduler='synchronous')`, MD5 hash del output contra baseline por plataforma (Linux/macOS/Win). Baselines en `tests/data/reproducibility_baselines/`.

**Archivos:**
- `tests/integration/interpolation/test_reproducibility.py`
- `tests/data/reproducibility_baselines/*.md5`

### task-3.5: Test reproducibilidad parallel (NFR-003, ADR-0007)

**Tipo:** test
**Estimación:** 1h
**Bloquea:** —
**Bloqueada por:** task-2.7.1

**Descripción:** Test `test_reproducibility_parallel_allclose`: 10 ejecuciones consecutivas con `scheduler='threaded'`; verificar `assert_allclose(outputs[0], outputs[i], rtol=1e-12, atol=1e-15)`.

**Archivos:**
- `tests/integration/interpolation/test_reproducibility.py`

### task-3.6: Memory profiling con memray (NFR-004)

**Tipo:** test
**Estimación:** 1h
**Bloquea:** —
**Bloqueada por:** task-3.3

**Descripción:** Script `tests/benchmark/profile_memory.py` corre los 4 métodos con `memray` y verifica peak memory < 1 GB por chunk con `chunk_size=512`. Reporte HTML en `tests/benchmark/results/`.

**Archivos:**
- `tests/benchmark/profile_memory.py`

### task-3.7: CHANGELOG + README example

**Tipo:** docs
**Estimación:** 0.5h
**Bloquea:** —
**Bloqueada por:** task-3.1, task-3.2

**Descripción:** Entrada `## [0.1.0] — 2026-??-??` en CHANGELOG con: 4 interpoladores, `TemporalAxis`, política NaN, validaciones, ADRs referenciados. Snippet "Quick start" en README usando `LinearInterpolator`.

**Archivos:**
- `CHANGELOG.md`
- `README.md`

---

## Resumen

| Fase | # tasks | Estimación total |
|---|---|---|
| Fase 1 — Fundamentos | 9 | 13.5h |
| Fase 2 — Métodos incrementales | 21 | 35h |
| Fase 3 — Docs, NFRs, integración | 7 | 11h |
| **Total** | **37** | **~59.5h** |

Distribución Fase 2 por sub-fase: Linear (4), PCHIP (5), PCHIP+RM (5), Fourier (4), NaN (2), Validación (4), Dask (2).

## Cobertura final REQ/NFR/ADR

- **REQ-001..014:** todos cubiertos por al menos una task de impl + una de test (ver tabla §Trazabilidad cruzada).
- **NFR-001..005:** todos con task de benchmark/property/integration dedicada.
- **ADR-0001, 0002, 0004, 0007, 0010, 0015:** referenciados explícitamente en las tasks que materializan la decisión.

No quedan REQ/NFR sin task asignada.
