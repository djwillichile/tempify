# Requirements — validation

**Estado:** Draft
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-15
**Última actualización:** 2026-05-15

## 1. Propósito

Implementar validaciones de coherencia geoespacial pre-procesamiento y validaciones de propiedades estadísticas post-interpolación. Garantizar fail-fast ante inputs inconsistentes y trazabilidad de la calidad del output.

## 2. Alcance

### In-scope

- Validación de coherencia entre archivos: CRS, extent, resolución, nodata.
- Validación de compatibilidad método-variable según perfil.
- Validación post-interpolación: conservación de media, continuidad cíclica, rango físico.
- Generación de estadísticas resumen por banda temporal.

### Out-of-scope

- Reproyección automática (solo se reporta la inconsistencia, no se corrige).
- Imputación de datos faltantes.

## 3. Actores y casos de uso

### Actor: Pipeline interno que necesita certeza sobre la validez de los datos antes y después de procesar.

**Caso de uso típico:** El pipeline pasa los archivos al validator antes de interpolar. Si hay un .tif con CRS distinto al resto, el validator aborta con error claro.

## 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL verify that all input rasters share CRS, spatial extent, spatial resolution, and nodata value within configurable tolerances.

### REQ-002 (Unwanted)

IF any geospatial inconsistency is detected, THEN THE SYSTEM SHALL raise `GeospatialIncoherenceError` with detailed identification of which files differ and on which dimension.

### REQ-003 (Event-driven)

WHEN a method-variable combination is incompatible per the variable profile (e.g., smooth interpolation of precipitation), THE SYSTEM SHALL raise `MethodVariableIncompatibilityError` before processing.

### REQ-004 (Event-driven)

WHEN post-interpolation validation runs on a PCHIP+RM output, THE SYSTEM SHALL verify that the monthly mean is preserved within 1e-4 absolute units.

### REQ-005 (Ubiquitous)

THE SYSTEM SHALL produce a `ValidationReport` dataclass with all checks executed, their result, and any warnings or errors.

## 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Reliability | Todas las decisiones deben ser trazables en el reporte de procesamiento | Inspección manual del reporte generado |
| NFR-002 | Usability | Mensajes de error en español, con código referenciable | Test `test_error_messages_spanish` |

## 6. Criterios de aceptación

- [ ] Todos los REQ cubiertos por tests específicos
- [ ] Cobertura del módulo >= 85%
- [ ] Documentación API completa (docstrings NumPy)
- [ ] CHANGELOG actualizado

## 7. Dependencias y supuestos

### Specs relacionadas

- Bloqueada por: [core-interpolation](../core-interpolation/requirements.md)
- Bloquea: [cli](../cli/requirements.md) (transitivamente)

### Supuestos

- Los inputs son archivos legibles por GDAL via rioxarray.

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Edge cases en formatos no estándar | Media | Bajo | Fixtures extensivas + manejo robusto de excepciones |

## 8. Referencias

- CF Conventions: https://cfconventions.org/
- EARS notation: https://alistairmavin.com/ears/
