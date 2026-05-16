# Requirements — io-handlers

**Estado:** Draft
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-15
**Última actualización:** 2026-05-15

## 1. Propósito

Implementar lectores y escritores para los formatos soportados (GeoTIFF, NetCDF, Zarr), aislando todo conocimiento de formato del resto del sistema. Garantizar preservación de georreferencia y metadatos.

## 2. Alcance

### In-scope

- Lectores: GeoTIFF (single/multi-banda), NetCDF, colección multi-archivo.
- Escritores: NetCDF CF-compliant, colección GeoTIFF, GeoTIFF multi-banda, Zarr (opcional).
- Preservación de CRS, extensión, resolución y nodata.
- Metadatos de procedencia (provenance) en outputs.

### Out-of-scope

- Reproyección o cambio de CRS.
- Reescalamiento o resampling espacial.
- Conversión vectorial-ráster.

## 3. Actores y casos de uso

### Actor: Pipeline interno que necesita una abstracción uniforme sobre formatos.

**Caso de uso típico:** El pipeline llama a `reader.read(source)` sin saber si la fuente es NetCDF, GeoTIFF o multi-archivo. Recibe siempre un `xr.DataArray` con CRS preservado.

## 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL expose readers and writers through the `BaseReader` and `BaseWriter` Protocol interfaces.

### REQ-002 (Ubiquitous)

THE SYSTEM SHALL return all read data as `xr.DataArray` with CRS preserved via the `rio` accessor.

### REQ-003 (Ubiquitous)

THE SYSTEM SHALL include the following provenance metadata in all written outputs: software version, method used, parameters, timestamp, MD5 of input files.

### REQ-004 (Event-driven)

WHEN writing NetCDF, THE SYSTEM SHALL produce CF-compliant output with zlib level 4 compression by default.

### REQ-005 (Event-driven)

WHEN writing a GeoTIFF collection, THE SYSTEM SHALL use configurable filename templates (default: `{var}_{date:%Y%m%d}.tif`).

### REQ-006 (Unwanted)

IF a target file exists and `overwrite=False`, THEN THE SYSTEM SHALL raise `FileExistsError` without modifying the file.

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
