# Requirements — io-handlers

**Estado:** Approved
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-15
**Última actualización:** 2026-05-16

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

THE SYSTEM SHALL expose readers and writers through the `BaseReader` and `BaseWriter` Protocol interfaces, declaring at minimum the methods `read(source) -> xr.DataArray` and `metadata() -> dict` on `BaseReader`, and `write(data, target) -> None` on `BaseWriter`.

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

### REQ-007 (Event-driven)

WHEN writing NetCDF output, THE SYSTEM SHALL include CF-compliant attributes: `units`, `calendar`, `_FillValue`, `standard_name`, `long_name`, and `grid_mapping` referencing the CRS.

### REQ-008 (Ubiquitous)

THE SYSTEM SHALL preserve the CRS across multi-file concat operations and in any write operation, using the `rio` accessor.

### REQ-009 (Optional)

WHERE the optional extra `[zarr]` is installed, THE SYSTEM SHALL expose `ZarrWriter` for chunked out-of-core writing.

### REQ-010 (Ubiquitous)

THE SYSTEM SHALL serialize provenance metadata as NetCDF attributes (`tempify_version`, `tempify_method`, `tempify_params`, `tempify_md5_inputs`, `tempify_timestamp_utc`) for NetCDF/Zarr outputs, and as a sidecar `.json` file alongside each GeoTIFF output.

## 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Reliability | Roundtrip bit-exact lectura→escritura→lectura preserva datos y metadata | Test `test_roundtrip_netcdf_preserves_attrs_and_values` |
| NFR-002 | Performance | Lectura de stack 12×3000×500 GeoTIFF en <5s sobre SSD | Benchmark `bench_read_geotiff_stack_12x3000x500` |
| NFR-003 | Maintainability | Cobertura del módulo ≥85% | `pytest --cov=tempify.io --cov-fail-under=85` |
| NFR-004 | Usability | Mensajes de error en español, con código referenciable | Test `test_error_messages_spanish` |

## 6. Criterios de aceptación

- [ ] REQ-001 cubierto por test `test_base_reader_protocol_signature`
- [ ] REQ-002 cubierto por test `test_read_returns_dataarray_with_crs`
- [ ] REQ-003 cubierto por test `test_provenance_metadata_present_in_output`
- [ ] REQ-004 cubierto por test `test_netcdf_writer_cf_compliant_zlib_default`
- [ ] REQ-005 cubierto por test `test_geotiff_collection_filename_template`
- [ ] REQ-006 cubierto por test `test_writer_raises_file_exists_when_overwrite_false`
- [ ] REQ-007 cubierto por test `test_netcdf_writer_includes_cf_attributes`
- [ ] REQ-008 cubierto por test `test_crs_preserved_across_concat_and_write`
- [ ] REQ-009 cubierto por test `test_zarr_writer_available_when_extra_installed`
- [ ] REQ-010 cubierto por test `test_provenance_serialization_netcdf_and_sidecar_json`
- [ ] NFR-001 cubierto por test `test_roundtrip_netcdf_preserves_attrs_and_values`
- [ ] NFR-002 medido por benchmark `bench_read_geotiff_stack_12x3000x500` (<5s)
- [ ] NFR-003 verificado por `pytest --cov=tempify.io --cov-fail-under=85`
- [ ] NFR-004 cubierto por test `test_error_messages_spanish`
- [ ] Documentación API completa (docstrings NumPy)
- [ ] CHANGELOG actualizado

## 7. Dependencias y supuestos

### Specs relacionadas

- Bloqueada por: ninguna (I/O es Capa 1 base de la arquitectura).
- Bloquea: [pipeline](../pipeline/requirements.md), [validation](../validation/requirements.md), [structure-detection](../structure-detection/requirements.md), [temporal-frequency-resolver](../temporal-frequency-resolver/requirements.md), [cli](../cli/requirements.md) (todas las consumen).

### Supuestos

- Los inputs son archivos legibles por GDAL via rioxarray.
- El hashing de inputs (MD5) sigue la política definida en [ADR-0007](../../docs/adr/0007-reproducibility-policy.md).
- El payload de procedencia sigue el shape definido en [processing-report.schema](../../docs/schemas/processing-report.schema.md).

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Pérdida de CRS en concat multi-archivo | Media | Alto | Tests roundtrip por formato y uso explícito de `rio.write_crs()` tras cada concat |
| Encoding NetCDF: cast silencioso de `_FillValue` al dtype destino | Media | Medio | Test parametrizado por dtype (`float32`, `float64`, `int16`) validando `_FillValue` post-roundtrip |
| Costo de MD5 sobre archivos multi-GB | Alta | Medio | Streaming hash con chunks de 64KB; medir overhead en benchmark dedicado |
| Dependencia opcional Zarr no instalada | Media | Bajo | Import lazy en `ZarrWriter`; al instanciar sin la dep, lanzar `MissingOptionalDependencyError` con mensaje accionable |
| GeoTIFF multi-banda con >65535 bandas | Baja | Medio | Validar `count` en reader y lanzar `UnsupportedBandCountError` antes de cargar |

## 8. Referencias

- CF Conventions: https://cfconventions.org/
- EARS notation: https://alistairmavin.com/ears/
- ADR-0007: [Política de reproducibilidad](../../docs/adr/0007-reproducibility-policy.md)
- Schema: [processing-report.schema](../../docs/schemas/processing-report.schema.md)
