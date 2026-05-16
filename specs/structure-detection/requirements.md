# Requirements — structure-detection

**Estado:** Draft
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-15
**Última actualización:** 2026-05-15

## 1. Propósito

Detectar automáticamente si los archivos de entrada constituyen un stack único multicapa, una colección de monocapas en una carpeta, o una lista explícita ordenada, y validar la coherencia de la estructura antes de procesarla.

## 2. Alcance

### In-scope

- Detección de stack único multicapa (NetCDF con dim temporal, GeoTIFF multi-banda).
- Detección de colecciones de monocapas en una carpeta.
- Aceptación de listas explícitas de rutas ordenadas.
- Reporte de la estructura detectada con nivel de confianza.

### Out-of-scope

- Reconocimiento de frecuencia temporal (responsabilidad de `temporal-frequency-resolver`).
- Validación geoespacial (responsabilidad de `validation`).
- Lectura efectiva de los datos (responsabilidad de `io-handlers`).

## 3. Actores y casos de uso

### Actor: Operador de pipeline que necesita procesar carpetas heterogéneas sin saber a priori si contienen un stack o múltiples archivos.

**Caso de uso típico:** El operador apunta a una carpeta con varios .tif; el sistema detecta automáticamente que es una colección de 12 monocapas y procede.

## 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL identify the input structure mode as one of: A (single multi-layer stack), B (collection of single-layer files in a folder), or C (explicit ordered list of file paths).

### REQ-002 (Event-driven)

WHEN the input is a single file with internal time dimension, THE SYSTEM SHALL classify it as mode A.

### REQ-003 (Event-driven)

WHEN the input is a folder containing N homogeneous raster files (same format, same CRS, same extent), THE SYSTEM SHALL classify it as mode B.

### REQ-004 (Event-driven)

WHEN the input is a Python list or sequence of file paths, THE SYSTEM SHALL classify it as mode C and preserve the user-provided order.

### REQ-005 (Unwanted)

IF the folder contains heterogeneous files (mixed formats, multiple variables, or unrelated rasters), THEN THE SYSTEM SHALL raise `AmbiguousStructureError` with a list of detected groups and request user disambiguation.

### REQ-006 (Ubiquitous)

THE SYSTEM SHALL return a `DetectionResult` dataclass with `structure_mode`, ordered `files` list, and `confidence` score between 0 and 1.

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
