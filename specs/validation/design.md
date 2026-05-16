# Design — validation

**Estado:** Draft
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-15

## 1. Visión técnica

La Capa 3 (`tempify.validation`) actúa como contrato de calidad entre la lectura I/O (Capa 1), la detección estructural (Capa 2) y los interpoladores (Capa 4). Implementa dos políticas diferenciadas: **fail-fast** para invariantes pre-procesamiento (incoherencia geoespacial, incompatibilidad método-variable), y **warn-and-continue** para verificaciones post-interpolación (preservación de media, continuidad cíclica, rango físico).

El paquete se diseña como una colección de validadores stateless con un contrato común: reciben datos y un contexto (`Tolerances`, `VariableProfile`) y devuelven un `ValidationReport` serializable conforme al schema `docs/schemas/validation-report.schema.md`. No realiza I/O ni cálculos de interpolación; consume `xarray.DataArray` ya normalizado por la Capa 1.

## 2. Arquitectura propuesta

### Diagrama de componentes

```
tempify.validation
├── geocoherence.py        # GeospatialCoherenceValidator + Tolerances
├── compatibility.py       # MethodVariableCompatibilityChecker
├── post.py                # PostInterpolationValidator
├── statistics.py          # StatisticalReporter
├── profiles.py            # VariableProfileMatcher + VariableProfile
├── report.py              # CheckResult, ValidationReport, builders
├── errors.py              # PreValidationError, GeospatialIncoherenceError,
│                          # MethodVariableIncompatibilityError
└── _codes.py              # registro de códigos GEO-*, COMPAT-*, POST-*
```

Flujo del Pipeline (referencia, no implementado aquí):

```
Capa 1 (io)  →  GeospatialCoherenceValidator  →  [fail-fast: PreValidationError]
              ↓
            MethodVariableCompatibilityChecker  →  [fail-fast: salvo --force-method]
              ↓
            Capa 4 (interpolation)
              ↓
            PostInterpolationValidator  →  [warn-and-continue]
              ↓
            StatisticalReporter
              ↓
            ValidationReport (JSON-serializable)
```

### Componentes nuevos

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| `GeospatialCoherenceValidator` | `tempify/validation/geocoherence.py` | Verifica CRS, extent, resolución, nodata, shape entre rasters. |
| `Tolerances`, `CANONICAL_TOLERANCES` | `tempify/validation/geocoherence.py` | Dataclass frozen con tolerancias canónicas de ADR-0009. |
| `MethodVariableCompatibilityChecker` | `tempify/validation/compatibility.py` | Aplica política de `allowed_methods` con override `--force-method`. |
| `PostInterpolationValidator` | `tempify/validation/post.py` | Verifica conservación de media, continuidad cíclica, rango físico, NaN integrity. |
| `StatisticalReporter` | `tempify/validation/statistics.py` | Calcula min/max/mean/std/nan_pct/count_valid por banda temporal. |
| `VariableProfileMatcher` | `tempify/validation/profiles.py` | Resuelve `VariableProfile` a partir de `DetectionResult` (CF, alias, unidades). |
| `VariableProfile` | `tempify/validation/profiles.py` | Modelo cargado vía `pyyaml` + validación `jsonschema` contra el schema canónico. |
| `CheckResult`, `ValidationReport` | `tempify/validation/report.py` | Modelos del schema canónico. |
| `PreValidationError` y subclases | `tempify/validation/errors.py` | Excepciones que portan el `ValidationReport`. |

### Componentes modificados

Ninguno en este alcance. La Capa 5 (Pipeline) consumirá estos contratos en su propia spec.

## 3. Contratos públicos (APIs)

### `GeospatialCoherenceValidator`

```python
class GeospatialCoherenceValidator:
    def __init__(self, tolerances: Tolerances = CANONICAL_TOLERANCES) -> None: ...

    def check(self, rasters: Sequence[xr.DataArray]) -> ValidationReport:
        """Validate homogeneity across a sequence of rasters.

        Returns a ValidationReport with PRE_PROCESS checks. Does not raise;
        the caller (Pipeline) decides whether to raise PreValidationError
        from `report.pre_passed`.
        """
```

**Pre-condiciones:** cada raster expone `rio.crs`, `rio.transform()`, `rio.nodata`, `shape`.
**Post-condiciones:** report contiene una `CheckResult` por dimensión verificada (CRS, extent, resolución, nodata, shape), con código `GEO-001..005`.
**Excepciones:** no lanza; errores semánticos de los inputs (e.g. raster sin CRS) producen `CheckResult` con `severity=ERROR`.

### `MethodVariableCompatibilityChecker`

```python
class MethodVariableCompatibilityChecker:
    def check(
        self,
        variable_profile: VariableProfile,
        method: Literal["linear", "pchip", "pchip_mp", "fourier"],
        *,
        force: bool = False,
    ) -> CheckResult:
        """Validate that `method` is allowed for the variable profile."""
```

**Pre-condiciones:** `variable_profile` ya validado contra el schema.
**Post-condiciones:**
- Si `method in profile.allowed_methods`: `CheckResult(COMPAT-001, passed=True, INFO)`.
- Si `method ∉ allowed_methods` y `force=False`: `CheckResult(COMPAT-001 o COMPAT-002 si precipitación, passed=False, ERROR)`. El caller debe lanzar `MethodVariableIncompatibilityError`.
- Si `force=True`: `CheckResult(COMPAT-003, passed=True, WARN)` y el caller marca `output.attrs["force_method_used"] = True`.

### `PostInterpolationValidator`

```python
class PostInterpolationValidator:
    def __init__(self, profile: VariableProfile) -> None: ...

    def check(
        self,
        input_da: xr.DataArray,
        output_da: xr.DataArray,
        profile: VariableProfile,
    ) -> ValidationReport:
        """Validate POST_PROCESS invariants on the interpolated output."""
```

**Pre-condiciones:** `input_da` con eje temporal de baja frecuencia (típicamente 12 meses); `output_da` con eje temporal denso (365/366 días) cubriendo el mismo span.
**Post-condiciones:** report contiene `POST-001..004`, todos con `phase=POST_PROCESS`. `POST-001..003` son WARN; `POST-004` (NaN inesperado donde input tenía valor) es ERROR. Nunca lanza.

### `StatisticalReporter`

```python
class StatisticalReporter:
    def report(self, da: xr.DataArray) -> dict[str, dict[str, float]]:
        """Return per-time-band statistics."""
```

**Pre-condiciones:** `da` con dim temporal (`time`).
**Post-condiciones:** dict cuya clave es la representación ISO del timestamp de cada banda y valor es `{"min", "max", "mean", "std", "nan_pct", "count_valid"}` en `float`.

### `VariableProfileMatcher`

```python
class VariableProfileMatcher:
    def __init__(self, profiles_path: Path | None = None) -> None: ...

    def match(self, detection_result: DetectionResult) -> VariableProfile:
        """Resolve a VariableProfile from detection signals (CF, alias, units)."""
```

**Pre-condiciones:** `detection_result` provee al menos uno de: `standard_name`, `variable_name`, `units`.
**Post-condiciones:** retorna el `VariableProfile` con mayor score de coincidencia (CF standard_name > alias exacto > unidades + alias parcial). Si no hay match: `UnknownVariableProfileError`.

## 4. Modelos de datos

### `CheckSeverity`, `CheckPhase`, `CheckResult`, `ValidationReport`

Definidos en `docs/schemas/validation-report.schema.md` y replicados literalmente en `tempify/validation/report.py`. `ValidationReport` expone helpers `failed_errors()`, `has_warnings()`, y `to_json() -> str` para serialización (NFR-001).

### `Tolerances`

```python
@dataclass(frozen=True)
class Tolerances:
    extent_rtol: float = 1e-6
    extent_atol_pixel_fraction: float = 0.01  # atol = fraction * pixel_size
    resolution_rtol: float = 1e-6
    crs_ignore_axis_order: bool = True
    nodata_strict: bool = True

CANONICAL_TOLERANCES: Final[Tolerances] = Tolerances()
```

Cualquier mutación requiere ADR sucesor (ADR-0009).

### `VariableProfile`

Pydantic v2 `BaseModel` con `model_config = ConfigDict(frozen=True, extra="forbid")`. Carga desde YAML vía `yaml.safe_load` + validación cruzada con `jsonschema` contra `variable-profile.schema.yaml` (single source of truth). Campos derivados del schema: `name`, `canonical_name`, `aliases`, `units`, `allowed_methods`, `default_method`, `physical_range` (`min`, `max`, `strict`), `acceptable_mean_error`, `acceptable_relative_error`, `monotonicity`, `default_chunk_size`, `references`, `version`.

Los perfiles concretos viven en el paquete `tempify.profiles` (archivos `profiles/*.yaml`) y se cargan vía `importlib.resources.files("tempify.profiles")`.

### Excepciones

```python
class PreValidationError(Exception):
    def __init__(self, report: ValidationReport): ...

class GeospatialIncoherenceError(PreValidationError): ...
class MethodVariableIncompatibilityError(PreValidationError): ...
class UnknownVariableProfileError(PreValidationError): ...
```

## 5. Algoritmos clave

### 5.1 GeospatialCoherenceValidator

Toma el primer raster como referencia y compara cada uno contra él. Para cada eje:

- **CRS (GEO-001):** `pyproj.CRS.from_user_input(a).equals(pyproj.CRS.from_user_input(b), ignore_axis_order=True)`.
- **Extent (GEO-002):** `numpy.isclose(bounds_a, bounds_b, rtol=1e-6, atol=0.01 * pixel_size)`. El `pixel_size` se toma del raster de referencia.
- **Resolución (GEO-003):** `math.isclose(res_x_a, res_x_b, rel_tol=1e-6)` y mismo test sobre `res_y`.
- **NoData (GEO-004):** `nodata_a is None and nodata_b is None` o `numpy.isnan` para ambos o `nodata_a == nodata_b`. Heterogeneidad si solo uno tiene `_FillValue`.
- **Shape (GEO-005):** comparación entera estricta de `(height, width)`.

Devuelve **todas** las inconsistencias encontradas, no solo la primera. Complejidad O(n) donde n es número de rasters.

### 5.2 MethodVariableCompatibilityChecker

Tabla derivada del `VariableProfile.allowed_methods`. Reglas:

1. `method in allowed_methods` → COMPAT-001 INFO `passed=True`.
2. `method ∉ allowed_methods` y `allowed_methods == []` (caso precipitación) → COMPAT-002 ERROR `passed=False`.
3. `method ∉ allowed_methods` y `allowed_methods != []` → COMPAT-001 ERROR `passed=False`.
4. Cualquier (2) o (3) con `force=True` → degrada a COMPAT-003 WARN `passed=True` y `details["force_method"] = method`. El Pipeline es responsable de estampar `output.attrs["force_method_used"] = True`.

### 5.3 Preservación de media mensual (POST-001)

Para cada píxel `(y, x)`:

1. Agrupar `output_da` por mes calendario (`output_da.groupby("time.month").mean("time")` ajustado para usar el mes calendario real, no el índice de mes).
2. Comparar contra `input_da.values` posicional.
3. Aplicar `|reconstructed - original| <= atol + rtol * |original|` con `atol = profile.acceptable_mean_error or POST_VALIDATION_ABS_TOL` (1e-4) y `rtol = profile.acceptable_relative_error or POST_VALIDATION_REL_TOL` (1e-6), conforme a ADR-0010.
4. Si cualquier píxel-mes falla: `POST-001 WARN passed=False` con `details={"pixel_failure_pct": ..., "max_abs_error": ..., "tol_source": "profile"|"default"}`.

Vectorizado con `xr.apply_ufunc(dask="parallelized")` para soportar inputs lazy.

### 5.4 Continuidad cíclica (POST-002)

Para los bordes diciembre→enero y junio→julio:

1. Calcular rolling mean de 31 días centrado: `output_da.rolling(time=31, center=True).mean()`.
2. Para cada par de bordes, comparar la dispersión (`std`) de la ventana que cruza el borde contra la dispersión de ventanas interiores del mismo mes. Si la dispersión del borde excede en `> factor * median_interior_std` (factor declarado por la spec; default `3.0`), reportar POST-002 WARN.
3. Agregar por píxel; reportar porcentaje de píxeles con discontinuidad.

### 5.5 Rango físico (POST-003)

`(output_da < profile.physical_range.min) | (output_da > profile.physical_range.max)`. Si hay violaciones:

- `profile.physical_range.strict == False` → POST-003 WARN.
- `profile.physical_range.strict == True` → POST-003 ERROR (eleva severidad; sigue siendo POST y no aborta el Pipeline; el Pipeline decide si trata strict como fail según política propia).

### 5.6 Integridad de NaN (POST-004)

Verificación: para todo `(t_input, y, x)` donde `input_da.isel(time=t)` no es NaN, todos los días de `output_da` que caen en ese mes deben ser numéricos. Aparición de NaN nuevo en output donde el input era válido es POST-004 ERROR (no WARN).

### 5.7 StatisticalReporter

Por cada banda temporal, calcula `min, max, mean, std, nan_pct, count_valid` con `xarray` reductions (`skipna=True`). Resultado serializable como `dict[str, dict[str, float]]` indexado por timestamp ISO 8601.

## 6. Decisiones de diseño

### Decisión 1: fail-fast pre vs warn post

**Opciones consideradas:**
1. Toda validación abort-on-error.
2. Toda validación warn-and-continue.
3. Mixta: pre fail-fast, post warn (elegida).

**Decisión:** Opción 3, conforme a `steering/architecture.md` § Capa 3.
**Razón:** las inconsistencias pre-procesamiento (CRS distinto) producen outputs sin sentido; abortar es la única respuesta defendible. Las inconsistencias post (mean preservation marginalmente fuera de tolerancia) son informativas, no invalidantes; abortar destruiría trabajo computacional caro.
**Trade-offs:** el usuario debe consultar el reporte para enterarse de warnings. Mitigado por logging estándar y por el campo `pre_passed` / `post_passed` en el reporte.

### Decisión 2: VariableProfile carga vía pydantic + jsonschema

**Opciones consideradas:**
1. Solo `pyyaml` con validación ad-hoc.
2. Solo `pydantic` con sus propios validators.
3. `pyyaml` + `jsonschema` contra el schema canónico + `pydantic` para tipado en runtime (elegida).

**Decisión:** Opción 3.
**Razón:** el schema YAML es el contrato versionado (ADR-0004, ADR-0010); validar contra él garantiza que perfiles externos del usuario cumplan el contrato. Pydantic da tipos estáticos para el resto del código.
**Trade-offs:** doble dependencia (pydantic + jsonschema), pero ambas ya están en el stack tech.

### Decisión 3: stamping `force_method_used` es responsabilidad del Pipeline

El validator emite el `CheckResult` con `details["force_method"]`. El Pipeline (Capa 5) lee el reporte y aplica el `attrs` al output antes de pasarlo al writer (Capa 1). El validator no muta DataArrays.

## 7. Estrategia de testing

### Tests unitarios (uno por código de error)

- **GEO-001..005**: `test_crs_mismatch_raises`, `test_extent_mismatch_raises`, `test_resolution_mismatch_raises`, `test_nodata_mismatch_raises`, `test_shape_mismatch_raises`. Fixtures: rasters sintéticos homogéneos y heterogéneos generados en setup.
- **COMPAT-001..003**: `test_method_variable_compat` (matriz de combinaciones), `test_precipitation_rejects_smooth_methods` (COMPAT-002), `test_force_method_override_emits_warn` (COMPAT-003 + stamping).
- **POST-001..004**: `test_post_mean_preservation` (tolerancia respetada y violada), `test_post_cyclic_continuity` (perfil discontinuo en dic-ene), `test_post_physical_range` (overshoot temperatura), `test_post_nan_integrity`.
- **Reporte**: `test_validation_report_serialization_keys` (NFR-001), `test_error_messages_spanish` (NFR-002).
- **Perfiles**: `test_profile_yaml_validates_against_schema`, `test_profile_matcher_cf_first`, `test_profile_matcher_alias_fallback`, `test_unknown_variable_raises`.

### Tests property-based (hypothesis)

- `test_mean_preservation_invariant`: para arrays sintéticos `(12, h, w)` con valores en rango físico de temperatura, si el output es construido por agregación inversa exacta del input, la verificación POST-001 nunca falla.
- `test_tolerance_monotonicity`: incrementar `acceptable_mean_error` nunca convierte un PASS en FAIL.
- `test_statistics_keys_invariant`: la salida de `StatisticalReporter` siempre contiene las 6 claves canónicas, para cualquier DataArray no vacío.

### Tests de integración

- `test_end_to_end_pre_then_post`: rasters homogéneos + perfil temperatura + interpolación PCHIP+RM mock-up → `pre_passed=True`, `post_passed=True`.
- `test_fail_fast_pre_vs_warn_post` (REQ-009): heterogeneidad CRS lanza `PreValidationError`; tras corregir, una violación de POST-001 produce solo WARN.
- `test_validation_performance_stack_12x3000x500` (NFR-003): assert `< 10 s`.

### Fixtures necesarios

- `tests/fixtures/rasters/homogeneous_3x3_12bands.tif` — generado en `conftest.py`.
- `tests/fixtures/rasters/crs_mismatch.tif`, `extent_mismatch.tif`, etc. — variantes sintéticas con una sola dimensión alterada.
- `tests/fixtures/profiles/valid/`: copias de `profiles/temperature.yaml`, `profiles/precipitation.yaml`, `profiles/relative_humidity.yaml`.
- `tests/fixtures/profiles/invalid/`: perfiles que violan el schema (missing required, default_method no en allowed_methods).
- `tests/fixtures/series/discontinuous_dec_jan.nc` — serie diaria con escalón artificial dic→ene para POST-002.

## 8. Plan de migración

No aplica. Spec de feature nueva sobre módulos vacíos.

## 9. Métricas de calidad

| Métrica | Umbral |
|---|---|
| Coverage del módulo `tempify.validation.*` | ≥ 85% (guardrail 1) |
| Performance pre+post sobre `12 x 3000 x 500` | < 10 s (NFR-003) |
| Memoria peak sobre `12 x 3000 x 500` | < 4 GB |
| Tiempo de carga de un `VariableProfile` desde YAML | < 50 ms |

## 10. Trazabilidad requirements → design

| Requirement | Componente que lo implementa | Test principal |
|---|---|---|
| REQ-001 | `GeospatialCoherenceValidator.check` con `CANONICAL_TOLERANCES` | `test_crs/extent/resolution/nodata_mismatch_raises` |
| REQ-002 | `GeospatialIncoherenceError` + códigos GEO-001..005 en `_codes.py` | mismos que REQ-001 |
| REQ-003 | `MethodVariableCompatibilityChecker.check` (`force=False`) | `test_method_variable_compat`, `test_precipitation_rejects_smooth_methods` |
| REQ-004 | `PostInterpolationValidator._check_mean_preservation` con `atol=1e-4`, `rtol=1e-6` | `test_post_mean_preservation` |
| REQ-005 | `report.py` (`CheckResult`, `ValidationReport`) | `test_validation_report_serialization_keys` |
| REQ-006 | `PostInterpolationValidator._check_cyclic_continuity` (rolling 31d) | `test_post_cyclic_continuity` |
| REQ-007 | `PostInterpolationValidator._check_physical_range` | `test_post_physical_range` |
| REQ-008 | `StatisticalReporter.report` | `test_statistical_reporter_keys` |
| REQ-009 | `PreValidationError` (pre) + WARN en report (post) | `test_fail_fast_pre_vs_warn_post` |
| REQ-010 | `MethodVariableCompatibilityChecker.check(force=True)` + COMPAT-003 + stamping en Pipeline | `test_force_method_override_emits_warn` |
| NFR-001 | `ValidationReport.to_json` | `test_validation_report_serialization_keys` |
| NFR-002 | mensajes en `_codes.py` (catálogo) | `test_error_messages_spanish` |
| NFR-003 | vectorización con `xr.apply_ufunc(dask="parallelized")` | `test_validation_performance_stack_12x3000x500` |
