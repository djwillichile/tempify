# Tasks — io-handlers

**Estado:** Approved
**Design doc:** [design.md](design.md)
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-15

## Reglas para tasks

- Atómica (un commit, ≤4h).
- Verificable (criterio de done observable).
- TDD estricto: el test precede a la implementación.
- Independiente en lo posible: declarar bloqueos.
- Trazable a REQ/NFR donde aplique.

Formato base por task:

```
### task-N.M: <título>
**Tipo:** test | impl | refactor | docs | chore
**Estimación:** <horas>h
**Bloquea:** task-X.Y
**Bloqueada por:** task-W.V
**REQ/NFR:** REQ-NNN, NFR-NNN
**Descripción:** ...
**Criterio de done:** ...
**Archivos:** ...
```

## Fase 1: Fundamentos

### task-1.1: Scaffolding del paquete `tempify.io`

**Tipo:** chore
**Estimación:** 0.5h
**Bloquea:** task-1.2, task-1.3, task-1.5, task-1.7
**Bloqueada por:** —
**REQ/NFR:** —

**Descripción:** Crear la estructura de directorios y `__init__.py` vacíos para `tempify.io`, `tempify.io.readers`, `tempify.io.writers`. Añadir el módulo `common.py` y `provenance.py` con docstrings de paquete. Registrar el módulo en `pyproject.toml` (sin nuevas deps).

**Criterio de done:**
- [ ] `python -c "import tempify.io"` no falla
- [ ] `python -c "import tempify.io.readers, tempify.io.writers"` no falla
- [ ] `ruff check src/tempify/io` pasa sin errores
- [ ] `mypy --strict src/tempify/io` pasa (módulos casi vacíos)

**Archivos:**
- `src/tempify/io/__init__.py`
- `src/tempify/io/common.py`
- `src/tempify/io/provenance.py`
- `src/tempify/io/readers/__init__.py`
- `src/tempify/io/writers/__init__.py`

---

### task-1.2: Test para Protocols `BaseReader` y `BaseWriter`

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-1.3
**Bloqueada por:** task-1.1
**REQ/NFR:** REQ-001

**Descripción:** Tests que verifiquen que los Protocols son `runtime_checkable`, exponen las firmas correctas, y que clases dummy con `read/metadata` y `write` los satisfacen estructuralmente.

**Criterio de done:**
- [ ] `test_base_reader_protocol_signature` falla con `ImportError`/`AttributeError` (red)
- [ ] `test_base_writer_protocol_signature` falla análogamente
- [ ] Tests cubren `isinstance(dummy, BaseReader)` truthy y `__protocol_attrs__` esperados

**Archivos:**
- `tests/unit/io/test_protocols.py`

---

### task-1.3: Implementación de Protocols `BaseReader`/`BaseWriter`

**Tipo:** impl
**Estimación:** 1h
**Bloquea:** task-2.1, task-2.5
**Bloqueada por:** task-1.2
**REQ/NFR:** REQ-001

**Descripción:** Implementar los dos Protocols en `common.py` con `@runtime_checkable`, type hints estrictos y docstrings NumPy completos. Reexportar desde `tempify.io.__init__`.

**Criterio de done:**
- [ ] Tests de task-1.2 pasan (verde)
- [ ] `mypy --strict` 0 errores
- [ ] `ruff` 0 warnings
- [ ] Docstring NumPy en cada Protocol

**Archivos:**
- `src/tempify/io/common.py`
- `src/tempify/io/__init__.py`

---

### task-1.4: Jerarquía de excepciones tipadas + tests

**Tipo:** test + impl
**Estimación:** 1.5h
**Bloquea:** task-2.2, task-2.4, task-2.10, task-2.14
**Bloqueada por:** task-1.1
**REQ/NFR:** NFR-004

**Descripción:** Definir `IOTempifyError` y subclases (`UnsupportedFormatError`, `MissingOptionalDependencyError`, `UnsupportedBandCountError`, `CRSPreservationError`). Cada excepción acepta un código `[IO-NNN]` y mensaje en español. Tests verifican: jerarquía (`issubclass`), formato del mensaje (regex `^\[IO-\d{3}\]`), y que contiene al menos un término en español (lista accionable).

**Criterio de done:**
- [ ] Test `test_error_messages_spanish` pasa (NFR-004)
- [ ] Test `test_exception_hierarchy` pasa
- [ ] Catálogo de códigos documentado en docstring del módulo `common.py`
- [ ] `mypy --strict` y `ruff` pasan

**Archivos:**
- `src/tempify/io/common.py`
- `tests/unit/io/test_exceptions.py`

---

### task-1.5: `Provenance` dataclass + tests

**Tipo:** test + impl
**Estimación:** 2h
**Bloquea:** task-1.6, task-2.8, task-2.11
**Bloqueada por:** task-1.1
**REQ/NFR:** REQ-003, REQ-010

**Descripción:** Definir `Provenance` como `dataclass(frozen=True, slots=True)` con campos del schema (`tempify_version`, `tempify_method`, `tempify_params`, `tempify_md5_inputs`, `tempify_timestamp_utc`, `reproducibility_mode`, `platform`, `python_version`). Métodos `to_netcdf_attrs()` (dict[str,str] con JSON strings serializados) y `to_json()` (string indent=2 estable). Tests: inmutabilidad, serialización determinista, roundtrip JSON, alineación con `processing-report.schema.md` §9.

**Criterio de done:**
- [ ] Test `test_provenance_immutability` pasa
- [ ] Test `test_provenance_to_netcdf_attrs_deterministic` pasa
- [ ] Test `test_provenance_to_json_matches_schema` pasa
- [ ] Docstring NumPy completo

**Archivos:**
- `src/tempify/io/provenance.py`
- `tests/unit/io/test_provenance.py`

---

### task-1.6: Helper `compute_provenance_md5` streaming + tests

**Tipo:** test + impl
**Estimación:** 1.5h
**Bloquea:** task-2.8, task-2.11
**Bloqueada por:** task-1.5
**REQ/NFR:** REQ-003

**Descripción:** Implementar `compute_provenance_md5(path, chunk_size=65536) -> str` con streaming chunked. Tests: idempotencia, equivalencia contra `hashlib.md5` one-shot para archivos de 1 KB, 1 MB y 100 MB sintéticos (`numpy.random.default_rng(42).bytes`), y property-based con hypothesis (`test_md5_idempotent`).

**Criterio de done:**
- [ ] Test `test_compute_provenance_md5_streaming` pasa
- [ ] Test `test_md5_idempotent` (hypothesis) pasa
- [ ] Memoria peak medida < 1 MB para archivo de 100 MB
- [ ] Docstring incluye complejidad O(N) tiempo / O(1) memoria

**Archivos:**
- `src/tempify/io/provenance.py`
- `tests/unit/io/test_provenance_md5.py`

---

### task-1.7: Helpers `attach_provenance_attrs` y `write_provenance_sidecar` + tests

**Tipo:** test + impl
**Estimación:** 1.5h
**Bloquea:** task-2.8, task-2.11, task-2.13
**Bloqueada por:** task-1.5
**REQ/NFR:** REQ-010

**Descripción:** `attach_provenance_attrs(da, provenance) -> xr.DataArray` retorna copia con attrs `tempify_*` poblados (sin mutar). `write_provenance_sidecar(provenance, target_geotiff) -> Path` escribe `<target>.provenance.json`. Tests: attrs presentes con valores esperados, archivo sidecar válido JSON, path retornado es `<target.parent>/<target.stem>.provenance.json`.

**Criterio de done:**
- [ ] Test `test_attach_provenance_attrs_does_not_mutate` pasa
- [ ] Test `test_write_provenance_sidecar_path_and_content` pasa
- [ ] Sidecar es parseable con `json.loads`
- [ ] `mypy --strict` pasa

**Archivos:**
- `src/tempify/io/provenance.py`
- `tests/unit/io/test_provenance_helpers.py`

---

## Fase 2: Implementación incremental

### task-2.1: Test `GeoTIFFReader` single/multi-band + CRS

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-2.2
**Bloqueada por:** task-1.3
**REQ/NFR:** REQ-001, REQ-002, REQ-008

**Descripción:** Crear fixture sintético `synthetic_monthly_3x3.tif` (single-band) y un fixture multi-banda. Tests: `test_geotiff_reader_returns_dataarray_with_crs`, `test_geotiff_reader_preserves_dims`, `test_geotiff_reader_multiband_dims`, `test_geotiff_reader_satisfies_base_reader_protocol`. Genera fixture vía script en `tests/fixtures/io/_gen_geotiff_fixtures.py`.

**Criterio de done:**
- [ ] Tests fallan con `ImportError` o `AttributeError`
- [ ] Script de generación de fixtures determinista (`seed=42`)
- [ ] Fixtures committeados (<50 KB)

**Archivos:**
- `tests/unit/io/test_geotiff_reader.py`
- `tests/fixtures/io/_gen_geotiff_fixtures.py`
- `tests/fixtures/io/synthetic_monthly_3x3.tif`

---

### task-2.2: Impl `GeoTIFFReader`

**Tipo:** impl
**Estimación:** 2h
**Bloquea:** task-2.6, task-2.16
**Bloqueada por:** task-2.1, task-1.4
**REQ/NFR:** REQ-001, REQ-002, REQ-008

**Descripción:** Implementar `GeoTIFFReader` usando `rioxarray.open_rasterio` con `masked=True` por defecto. Soporte single y multi-banda. Validar `count <= 65535` (lanzar `UnsupportedBandCountError` si excede). Implementar `metadata()` con dims, dtype, CRS, nodata.

**Criterio de done:**
- [ ] Tests de task-2.1 pasan
- [ ] CRS preservado vía `rio.crs is not None`
- [ ] mypy/ruff pasan
- [ ] Docstring NumPy con ejemplos

**Archivos:**
- `src/tempify/io/readers/geotiff.py`
- `src/tempify/io/readers/__init__.py`

---

### task-2.3: Test `NetCDFReader` + decodificación CF

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-2.4
**Bloqueada por:** task-1.3
**REQ/NFR:** REQ-001, REQ-002

**Descripción:** Fixture `synthetic_monthly_3x3.nc` con coord `time` (calendar `proleptic_gregorian`, `units="days since 1970-01-01"`). Tests: `test_netcdf_reader_returns_dataarray_with_crs`, `test_netcdf_reader_decodes_cf_time`, `test_netcdf_reader_calendar_handling` (parametrize `noleap`, `360_day`), `test_netcdf_reader_variable_selection`.

**Criterio de done:**
- [ ] Tests fallan (red) sin implementación
- [ ] Fixture committeado (<10 KB)
- [ ] Script generador en `tests/fixtures/io/_gen_netcdf_fixtures.py`

**Archivos:**
- `tests/unit/io/test_netcdf_reader.py`
- `tests/fixtures/io/_gen_netcdf_fixtures.py`
- `tests/fixtures/io/synthetic_monthly_3x3.nc`

---

### task-2.4: Impl `NetCDFReader`

**Tipo:** impl
**Estimación:** 2h
**Bloquea:** task-2.6, task-2.9, task-2.16
**Bloqueada por:** task-2.3, task-1.4
**REQ/NFR:** REQ-001, REQ-002

**Descripción:** Implementar `NetCDFReader` con `xarray.open_dataset(decode_times=True)`, selección de variable (auto si única, explícita si `variable=` provista), engine configurable. Inyectar CRS desde atributo `grid_mapping` o `crs_wkt` si está presente. Lanzar `UnsupportedFormatError` si no es NetCDF/HDF5.

**Criterio de done:**
- [ ] Tests de task-2.3 pasan
- [ ] mypy/ruff pasan
- [ ] Docstring NumPy con ejemplos de selección de variable

**Archivos:**
- `src/tempify/io/readers/netcdf.py`
- `src/tempify/io/readers/__init__.py`

---

### task-2.5: Test `MultiFileCollectionReader` concat + orden

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-2.6
**Bloqueada por:** task-1.3
**REQ/NFR:** REQ-008

**Descripción:** Tests: `test_multifile_reader_concat_preserves_crs` (12 GeoTIFFs monthly), `test_multifile_reader_lexicographic_order_is_deterministic`, `test_multifile_reader_time_coord_order`, `test_multifile_reader_raises_on_heterogeneous_crs` (mezcla EPSG:4326 y EPSG:3857 → `CRSPreservationError`). Fixture `tests/fixtures/io/heterogeneous_crs/`.

**Criterio de done:**
- [ ] Tests fallan inicialmente
- [ ] Fixture de CRS heterogéneo generado via script

**Archivos:**
- `tests/unit/io/test_multifile_reader.py`
- `tests/fixtures/io/_gen_heterogeneous_crs.py`

---

### task-2.6: Impl `MultiFileCollectionReader`

**Tipo:** impl
**Estimación:** 2.5h
**Bloquea:** task-2.16, task-3.3
**Bloqueada por:** task-2.5, task-2.2, task-2.4
**REQ/NFR:** REQ-008

**Descripción:** Implementar algoritmo §5.2 del design: leer cada archivo con `underlying`, verificar CRS uniforme, ordenar (`sort_by="name"` o `"time_coord"`), `xr.concat(..., combine_attrs="override")`, re-escribir CRS con `rio.write_crs(ref_crs, inplace=False)`, validar `rio.crs is not None` post-concat. Lanzar `CRSPreservationError` con código `[IO-...]` en cualquier inconsistencia.

**Criterio de done:**
- [ ] Tests de task-2.5 pasan
- [ ] Orden ASCII estable en `md5_inputs`
- [ ] Docstring NumPy describe `sort_by` y excepciones

**Archivos:**
- `src/tempify/io/readers/multi.py`
- `src/tempify/io/readers/__init__.py`

---

### task-2.7: Test `NetCDFWriter` CF + zlib + overwrite

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-2.8
**Bloqueada por:** task-1.3
**REQ/NFR:** REQ-001, REQ-004, REQ-006, REQ-007

**Descripción:** Tests: `test_netcdf_writer_cf_compliant_zlib_default` (verifica `complevel=4` reabriendo y leyendo `encoding`), `test_netcdf_writer_includes_cf_attributes` (`units`, `calendar`, `_FillValue`, `standard_name`, `long_name`, `grid_mapping`), `test_writer_raises_file_exists_when_overwrite_false` (verifica md5 pre/post sin cambio), `test_writer_overwrites_when_overwrite_true`, `test_netcdf_writer_satisfies_base_writer_protocol`.

**Criterio de done:**
- [ ] Tests fallan inicialmente
- [ ] Parametrización por dtype (`float32`, `float64`, `int16`) para `_FillValue`

**Archivos:**
- `tests/unit/io/test_netcdf_writer.py`

---

### task-2.8: Impl `NetCDFWriter`

**Tipo:** impl
**Estimación:** 3h
**Bloquea:** task-2.13, task-2.15, task-2.16, task-3.3
**Bloqueada por:** task-2.7, task-1.7, task-1.6
**REQ/NFR:** REQ-003, REQ-004, REQ-006, REQ-007, REQ-010

**Descripción:** Implementar `NetCDFWriter._build_encoding`, inyección de atributos CF, llamada a `attach_provenance_attrs` antes de `to_netcdf`, manejo de `overwrite`, `unlimited_dims`. Atributos `tempify_*` van como string JSON donde corresponda. Validar CRS de entrada y escribir `grid_mapping`/`spatial_ref` vía `rio.write_crs`.

**Criterio de done:**
- [ ] Tests de task-2.7 pasan
- [ ] `_FillValue` correcto post-roundtrip por dtype
- [ ] mypy/ruff pasan
- [ ] Docstring NumPy con ejemplo end-to-end

**Archivos:**
- `src/tempify/io/writers/netcdf.py`
- `src/tempify/io/writers/__init__.py`

---

### task-2.9: Test `GeoTIFFCollectionWriter` filename template + sidecar

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-2.10
**Bloqueada por:** task-1.3
**REQ/NFR:** REQ-005, REQ-006, REQ-010

**Descripción:** Tests: `test_geotiff_collection_filename_template` (default `{name}_{date:%Y%m%d}.tif` y custom), `test_geotiff_collection_filename_template_invalid_token` (mensaje accionable), `test_geotiff_collection_creates_sidecar_provenance_json` (uno por archivo), `test_geotiff_collection_overwrite_behavior`, property `test_filename_template_collisions` (hypothesis, fechas únicas → nombres únicos).

**Criterio de done:**
- [ ] Tests fallan
- [ ] Hypothesis strategy para fechas pseudo-aleatorias dentro de 1900-2100

**Archivos:**
- `tests/unit/io/test_geotiff_collection_writer.py`

---

### task-2.10: Impl `GeoTIFFCollectionWriter`

**Tipo:** impl
**Estimación:** 2.5h
**Bloquea:** task-2.16, task-3.3
**Bloqueada por:** task-2.9, task-1.7, task-1.4
**REQ/NFR:** REQ-005, REQ-006, REQ-010

**Descripción:** Implementar render de filename template con `str.format` y validación de tokens, iteración sobre coord temporal, escritura individual de bandas vía `rio.to_raster`, sidecar JSON por archivo. Check de `overwrite` previo a cualquier escritura para evitar estados parciales.

**Criterio de done:**
- [ ] Tests de task-2.9 pasan
- [ ] Sidecar JSON parseable; filename y md5 incluidos
- [ ] mypy/ruff pasan

**Archivos:**
- `src/tempify/io/writers/geotiff.py`
- `src/tempify/io/writers/__init__.py`

---

### task-2.11: Test `MultiBandGeoTIFFWriter` + band-count guard

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.12
**Bloqueada por:** task-1.3
**REQ/NFR:** REQ-006, REQ-010

**Descripción:** Tests: `test_multiband_geotiff_writer_roundtrip`, `test_multibandgeotiff_writer_rejects_excessive_bands` (mock con shape `(65536, 3, 3)` → `UnsupportedBandCountError`), `test_multiband_writer_overwrite_behavior`, `test_multiband_writer_creates_provenance_sidecar`.

**Criterio de done:**
- [ ] Tests fallan inicialmente
- [ ] Mock no requiere ocupar memoria real (usar `dask.array.zeros` o `np.empty` lazy)

**Archivos:**
- `tests/unit/io/test_multiband_geotiff_writer.py`

---

### task-2.12: Impl `MultiBandGeoTIFFWriter`

**Tipo:** impl
**Estimación:** 1.5h
**Bloquea:** task-2.16
**Bloqueada por:** task-2.11, task-1.7, task-1.4
**REQ/NFR:** REQ-006, REQ-010

**Descripción:** Implementar escritor multi-banda en un único TIFF; verificar `data.sizes[time_dim] <= 65535`. Reutilizar helpers de procedencia. Compresión `deflate` con `predictor=2`.

**Criterio de done:**
- [ ] Tests de task-2.11 pasan
- [ ] mypy/ruff pasan
- [ ] Docstring NumPy con caveat sobre límite TIFF

**Archivos:**
- `src/tempify/io/writers/geotiff.py`

---

### task-2.13: Test `ZarrWriter` (extra opcional)

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.14
**Bloqueada por:** task-1.3
**REQ/NFR:** REQ-009

**Descripción:** Tests: `test_zarr_writer_available_when_extra_installed` (skip si `pytest.importorskip('zarr')` falla), `test_zarr_writer_raises_missing_dependency_when_extra_absent` (monkeypatch `sys.modules['zarr'] = None`, esperar `MissingOptionalDependencyError`), `test_zarr_writer_consolidated_metadata`.

**Criterio de done:**
- [ ] Tests fallan inicialmente
- [ ] Tests skip elegante cuando `zarr` no instalado

**Archivos:**
- `tests/unit/io/test_zarr_writer.py`

---

### task-2.14: Impl `ZarrWriter` con import lazy

**Tipo:** impl
**Estimación:** 1.5h
**Bloquea:** task-2.16
**Bloqueada por:** task-2.13, task-1.4, task-2.8
**REQ/NFR:** REQ-009, REQ-010

**Descripción:** Implementar `ZarrWriter` con import diferido de `zarr` dentro de `__init__` (capturar `ImportError` → `MissingOptionalDependencyError` con mensaje en español). Atributos de procedencia idénticos a NetCDF. Soporte `consolidated=True`. Documentar en `pyproject.toml` el extra `[zarr]` si no existe.

**Criterio de done:**
- [ ] Tests de task-2.13 pasan
- [ ] `import tempify.io` no requiere `zarr`
- [ ] mypy/ruff pasan

**Archivos:**
- `src/tempify/io/writers/zarr.py`
- `pyproject.toml` (registro del extra)

---

### task-2.15: Preservación de Dask lazy en lectura/escritura

**Tipo:** test + impl
**Estimación:** 1.5h
**Bloquea:** task-3.2
**Bloqueada por:** task-2.2, task-2.4, task-2.8
**REQ/NFR:** REQ-002, NFR-002

**Descripción:** Tests: `test_geotiff_reader_lazy_when_chunks_provided` (verifica `da.chunks is not None`), `test_netcdf_reader_lazy_when_chunks_provided`, `test_netcdf_writer_accepts_dask_backed_array` (no `compute` implícito antes del encoding). Ajustar implementaciones si compute prematuro detectado.

**Criterio de done:**
- [ ] Tests pasan
- [ ] No regresiones en tests previos

**Archivos:**
- `tests/unit/io/test_lazy_dask.py`
- `src/tempify/io/readers/*.py`, `src/tempify/io/writers/netcdf.py`

---

### task-2.16: Roundtrip bit-exact por formato

**Tipo:** test
**Estimación:** 2.5h
**Bloquea:** task-3.3
**Bloqueada por:** task-2.2, task-2.4, task-2.6, task-2.8, task-2.10, task-2.12, task-2.14
**REQ/NFR:** NFR-001, REQ-003, REQ-008, REQ-010

**Descripción:** Tests parametrizados por formato: `test_roundtrip_netcdf_preserves_attrs_and_values`, `test_roundtrip_geotiff_collection_preserves_attrs_and_values`, `test_roundtrip_multiband_geotiff_preserves_attrs_and_values`, `test_roundtrip_zarr_preserves_attrs_and_values` (skip si ausente). Usar `np.testing.assert_array_equal` + comparación CRS WKT + attrs. Incluir `test_crs_preserved_across_concat_and_write`.

**Criterio de done:**
- [ ] Todos los roundtrips pasan bit-exact
- [ ] Provenance reabrible y equivalente al original
- [ ] Test de concat→write→reabrir pasa (REQ-008)

**Archivos:**
- `tests/integration/io/test_roundtrips.py`

---

## Fase 3: Documentación e integración

### task-3.1: Docstrings NumPy en API pública

**Tipo:** docs
**Estimación:** 2h
**Bloquea:** task-3.4
**Bloqueada por:** Fase 2 completa
**REQ/NFR:** —

**Descripción:** Auditar todas las clases y funciones públicas de `tempify.io`, completar docstrings formato NumPy (Parameters, Returns, Raises, Examples). Validar con `pydocstyle --convention=numpy` y ejecutar `python -m doctest` sobre ejemplos críticos.

**Criterio de done:**
- [ ] 100% API pública con docstring NumPy
- [ ] `pydocstyle` pasa
- [ ] Doctests pasan donde se incluyeron

**Archivos:**
- `src/tempify/io/**/*.py`

---

### task-3.2: Benchmark NFR-002 lectura GeoTIFF stack

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-3.4
**Bloqueada por:** task-2.15
**REQ/NFR:** NFR-002

**Descripción:** Implementar `bench_read_geotiff_stack_12x3000x500` con `pytest-benchmark` o `time.perf_counter` controlado. Fixture generado en `setup` (no committeado). Asserción: tiempo < 5s en SSD. Marcador `@pytest.mark.benchmark` excluido del CI por convención. Reporte impreso a stdout.

**Criterio de done:**
- [ ] Benchmark ejecuta y reporta tiempo
- [ ] `pytest -m benchmark` aislado del run normal
- [ ] Documentar comando en `tests/benchmarks/README` (sección dentro del archivo de bench)

**Archivos:**
- `tests/benchmarks/test_io_bench.py`

---

### task-3.3: Integration test WorldClim mini

**Tipo:** test
**Estimación:** 2h
**Bloquea:** task-3.4
**Bloqueada por:** task-2.6, task-2.8, task-2.10
**REQ/NFR:** REQ-002, REQ-008, NFR-001

**Descripción:** Fixture `worldclim_tiny.tif` (BBOX pequeño, 10 arc-min, 12 archivos). Test `test_integration_worldclim_read_write_reopen`: lee con `GeoTIFFReader`, concat con `MultiFileCollectionReader`, escribe con `NetCDFWriter`, reabre con `NetCDFReader`, verifica equivalencia bit-exact y CRS EPSG:4326 preservado.

**Criterio de done:**
- [ ] Test pasa
- [ ] Fixture <100 KB committeado
- [ ] Tiempo de ejecución <5s

**Archivos:**
- `tests/integration/io/test_worldclim_mini.py`
- `tests/fixtures/io/worldclim_tiny/*.tif`

---

### task-3.4: CHANGELOG + impl-log + cobertura final

**Tipo:** docs
**Estimación:** 1h
**Bloquea:** —
**Bloqueada por:** task-3.1, task-3.2, task-3.3
**REQ/NFR:** NFR-003

**Descripción:** Añadir entrada `## [Unreleased] - Capa 1: io-handlers` al `CHANGELOG.md`. Cerrar `specs/io-handlers/impl-log.md` con resumen, decisiones revisitadas y métricas. Ejecutar `pytest --cov=tempify.io --cov-fail-under=85` y adjuntar reporte al impl-log.

**Criterio de done:**
- [ ] CHANGELOG actualizado
- [ ] `pytest --cov=tempify.io --cov-fail-under=85` pasa
- [ ] impl-log cierra con timestamp y firma del autor

**Archivos:**
- `CHANGELOG.md`
- `specs/io-handlers/impl-log.md`

---

## Resumen

| Fase | # tasks | Estimación total |
|---|---|---|
| Fase 1: Fundamentos | 7 | 9.0h |
| Fase 2: Implementación incremental | 16 | 29.0h |
| Fase 3: Documentación e integración | 4 | 6.5h |
| **Total** | **27** | **44.5h** |

## Trazabilidad REQ/NFR → tasks

| Requirement | Tasks que lo cubren |
|---|---|
| REQ-001 | task-1.2, task-1.3, task-2.1, task-2.2, task-2.3, task-2.4, task-2.7 |
| REQ-002 | task-2.1, task-2.2, task-2.3, task-2.4, task-2.15, task-3.3 |
| REQ-003 | task-1.5, task-1.6, task-2.8, task-2.16 |
| REQ-004 | task-2.7, task-2.8 |
| REQ-005 | task-2.9, task-2.10 |
| REQ-006 | task-2.7, task-2.8, task-2.9, task-2.10, task-2.11, task-2.12 |
| REQ-007 | task-2.7, task-2.8 |
| REQ-008 | task-2.1, task-2.5, task-2.6, task-2.16, task-3.3 |
| REQ-009 | task-2.13, task-2.14 |
| REQ-010 | task-1.5, task-1.7, task-2.8, task-2.10, task-2.11, task-2.14, task-2.16 |
| NFR-001 | task-2.16, task-3.3 |
| NFR-002 | task-2.15, task-3.2 |
| NFR-003 | task-3.4 |
| NFR-004 | task-1.4 |
