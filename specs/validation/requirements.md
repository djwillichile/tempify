# Requirements — validation

**Estado:** Approved
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-15
**Última actualización:** 2026-05-16

## 1. Propósito

Implementar validaciones de coherencia geoespacial pre-procesamiento y validaciones de propiedades estadísticas post-interpolación. Garantizar fail-fast ante inputs inconsistentes y trazabilidad de la calidad del output mediante un `ValidationReport` serializable.

## 2. Alcance

### In-scope

- Validación de coherencia entre archivos: CRS, extent, resolución, nodata, dentro de tolerancias canónicas definidas en `docs/adr/0009-geospatial-coherence-tolerances.md`.
- Validación de compatibilidad método-variable según el perfil declarado en `docs/schemas/variable-profile.schema.yaml`.
- Validación post-interpolación: conservación de media mensual, continuidad cíclica (diciembre-enero, junio-julio), rango físico por píxel-día.
- Reportería estadística por banda temporal (`StatisticalReporter`).
- Política diferenciada fail-fast (pre) vs warn-and-continue (post).
- Soporte de override `--force-method --i-know-what-i-am-doing` per `docs/adr/0004-precipitation-policy.md`.

### Out-of-scope

- Reproyección automática (se reporta la inconsistencia, no se corrige).
- Imputación de datos faltantes.
- Validación cross-variable (p. ej. `tmin <= tmax`); diferida a v0.2.
- Soporte de calendarios CF no-estándar (`360_day`, `noleap`); diferido.
- Generación dinámica de perfiles de variable; los YAML los provee el proyecto (no se generan en runtime).

## 3. Actores y casos de uso

### Actor: Pipeline interno que necesita certeza sobre la validez de los datos antes y después de procesar.

**Caso de uso típico:** El pipeline pasa los archivos al validator antes de interpolar. Si hay un .tif con CRS distinto al resto, el validator aborta con `PreValidationError(report)`. Tras la interpolación, el post-validator verifica conservación de media, continuidad cíclica y rango físico; las violaciones se reportan como WARN sin abortar.

## 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL verify that all input rasters share CRS, spatial extent, spatial resolution, and nodata value within the canonical tolerances declared in `docs/adr/0009-geospatial-coherence-tolerances.md`.

### REQ-002 (Unwanted)

IF any geospatial inconsistency is detected, THEN THE SYSTEM SHALL raise `GeospatialIncoherenceError` with detailed identification of which files differ and on which dimension (CRS, extent, resolution, nodata).

### REQ-003 (Event-driven)

WHEN a method-variable combination is incompatible per the variable profile (e.g., smooth interpolation of precipitation), THE SYSTEM SHALL raise `MethodVariableIncompatibilityError` before processing.

### REQ-004 (Event-driven)

WHEN post-interpolation validation runs on a PCHIP+RM output, THE SYSTEM SHALL verify that the monthly mean is preserved within the post-validator contractual tolerance `atol=1e-4` and `rtol=1e-6`, per `docs/adr/0010-mean-preservation-tolerance.md` (the tighter `1e-6` is reserved for the RM iterator's internal convergence, not for this check).

### REQ-005 (Ubiquitous)

THE SYSTEM SHALL produce a `ValidationReport` dataclass conformant with `docs/schemas/validation-report.schema.md`, exposing the canonical fields `checks`, `pre_passed`, `post_passed`, `warnings`, `errors`, and `statistics`.

### REQ-006 (Ubiquitous)

WHILE running `PostInterpolationValidator`, THE SYSTEM SHALL verify cyclic continuity by comparing the rolling means across the December-January and June-July boundaries against the tolerance declared in the variable profile.

### REQ-007 (Ubiquitous)

WHILE running `PostInterpolationValidator`, THE SYSTEM SHALL verify that each pixel-day value falls within the `physical_range` (`min`, `max`) declared in the variable profile.

### REQ-008 (Ubiquitous)

THE SYSTEM SHALL expose `StatisticalReporter` that emits per-band statistics with the keys: `min`, `max`, `mean`, `std`, `nan_pct`, `count_valid`.

### REQ-009 (Ubiquitous)

THE SYSTEM SHALL apply a fail-fast policy for pre-process validation (raise `PreValidationError(report)`) and a warn-and-continue policy for post-process validation (emit a `WARN` entry in `ValidationReport.warnings` and log a warning via the standard logger).

### REQ-010 (Optional, WHERE)

WHERE the user passes `--force-method <method> --i-know-what-i-am-doing` for an incompatible `(variable, method)` pair, THE SYSTEM SHALL emit a `COMPAT-003` WARN entry in `ValidationReport.warnings` instead of raising `MethodVariableIncompatibilityError`, AND stamp the output dataset with the attribute `force_method_used = true`.

## 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Reliability | El `ValidationReport` debe ser serializable (JSON) y contener todas las claves canónicas del schema | Test `test_validation_report_serialization_keys` |
| NFR-002 | Usability | Mensajes de error en español, con código referenciable (`GEO-NNN`, `COMPAT-NNN`, `POST-NNN`) | Test `test_error_messages_spanish` |
| NFR-003 | Performance | Validación pre + post sobre un stack `12 x 3000 x 500` debe completarse en `< 10 s` en hardware de referencia | Test `test_validation_performance_stack_12x3000x500` |

## 6. Criterios de aceptación

- [ ] Cada REQ cubierto por un test nombrado, según la siguiente trazabilidad:

| REQ | Test(s) |
|---|---|
| REQ-001 | `test_crs_mismatch_raises`, `test_extent_mismatch_raises`, `test_resolution_mismatch_raises`, `test_nodata_mismatch_raises` |
| REQ-002 | `test_crs_mismatch_raises`, `test_extent_mismatch_raises`, `test_resolution_mismatch_raises`, `test_nodata_mismatch_raises` |
| REQ-003 | `test_method_variable_compat` |
| REQ-004 | `test_post_mean_preservation` |
| REQ-005 | `test_validation_report_serialization_keys` |
| REQ-006 | `test_post_cyclic_continuity` |
| REQ-007 | `test_post_physical_range` |
| REQ-008 | `test_statistical_reporter_keys` |
| REQ-009 | `test_fail_fast_pre_vs_warn_post` |
| REQ-010 | `test_force_method_override_emits_warn` |
| NFR-001 | `test_validation_report_serialization_keys` |
| NFR-002 | `test_error_messages_spanish` |
| NFR-003 | `test_validation_performance_stack_12x3000x500` |

- [ ] Cobertura del módulo `>= 85%`.
- [ ] Documentación API completa (docstrings NumPy + type hints).
- [ ] CHANGELOG actualizado.

## 7. Dependencias y supuestos

### Specs relacionadas

- Bloqueada por: [io-handlers](../io-handlers/requirements.md), [structure-detection](../structure-detection/requirements.md), [core-interpolation](../core-interpolation/requirements.md)
- Bloquea: [pipeline](../pipeline/requirements.md), [cli](../cli/requirements.md), [gui](../gui/requirements.md)

### Documentos de referencia (contratos vinculantes)

- `steering/architecture.md` § Capa 3.
- `docs/methodology/precipitation.md`.
- `docs/adr/0004-precipitation-policy.md` (override `--force-method`).
- `docs/adr/0009-geospatial-coherence-tolerances.md` (tolerancias canónicas).
- `docs/adr/0010-mean-preservation-tolerance.md` (tres niveles de tolerancia: convergencia `1e-6`, post-validator `atol=1e-4 + rtol=1e-6`, perfil YAML).
- `docs/schemas/validation-report.schema.md` (shape de `ValidationReport`).
- `docs/schemas/variable-profile.schema.yaml` (estructura YAML de perfiles).

### Supuestos

- Los inputs son archivos legibles por GDAL via rioxarray.
- La normalización de NaN vs `_FillValue` ocurre en Capa 1 (io-handlers) antes de llegar a Capa 3.
- Los perfiles de variable existen como archivos YAML versionados en el repositorio y conforman al schema.

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Float-imprecision en comparación de extent entre archivos | Media | Medio | Aplicar tolerancias canónicas de `docs/adr/0009-geospatial-coherence-tolerances.md` (rtol/atol) en lugar de igualdad estricta |
| Divergencia entre NaN y sentinel `_FillValue` entre lectores (GeoTIFF vs NetCDF vs Zarr) | Media | Alto | Normalizar a NaN en Capa 1 (io-handlers); el validator asume el dato ya normalizado |
| Ausencia o desactualización del schema YAML de perfil de variable | Baja | Alto | Schema versionado en `docs/schemas/variable-profile.schema.yaml`; validación del perfil al cargar |
| RM no converge en celdas con varianza extrema y la conservación de media falla la tolerancia | Media | Bajo | El iterador retorna la mejor aproximación; el post-validator marca `WARN` (POST-001), no `ERROR` |
| Validación cross-variable (p. ej. `tmin <= tmax`) no contemplada en v1.0 | Alta | Bajo | Declarado explícitamente out-of-scope; diferido a v0.2 |
| Edge cases en formatos no estándar | Media | Bajo | Fixtures extensivas + manejo robusto de excepciones |

## 8. Referencias

- CF Conventions: https://cfconventions.org/
- EARS notation: https://alistairmavin.com/ears/
- ADR-0004 (precipitation policy), ADR-0009 (geo tolerances), ADR-0010 (mean tolerance).
- `docs/schemas/validation-report.schema.md`, `docs/schemas/variable-profile.schema.yaml`.
