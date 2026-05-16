# Design — io-handlers

**Estado:** Draft
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-16

## 1. Visión técnica

La Capa 1 (I/O) aísla por completo el conocimiento de formatos del resto de tempify. La materia prima de intercambio entre capas es siempre `xr.DataArray` con CRS preservado vía el accesor `rio` (ADR-0001). El diseño define dos Protocols (`BaseReader`, `BaseWriter`), una familia de implementaciones concretas por formato (GeoTIFF, NetCDF, colección multi-archivo, Zarr opcional), una utilidad de procedencia centralizada y una jerarquía tipada de excepciones. No existe lógica de interpolación, ni transformaciones espaciales: leer, concatenar, escribir, y registrar trazabilidad.

El módulo `tempify.io` se descompone en cuatro submódulos: `readers`, `writers`, `provenance`, y `common` (Protocols, excepciones, helpers compartidos). Esta separación facilita el testing aislado y respeta la regla arquitectónica de no introducir dependencias hacia capas superiores.

## 2. Arquitectura propuesta

### Diagrama de componentes

```
tempify.io
├── common.py            Protocols, exceptions, dtype/encoding helpers
├── provenance.py        Provenance dataclass, MD5 streaming, attrs serialization
├── readers/
│   ├── __init__.py      re-export of public readers
│   ├── geotiff.py       GeoTIFFReader
│   ├── netcdf.py        NetCDFReader
│   └── multi.py         MultiFileCollectionReader
└── writers/
    ├── __init__.py      re-export of public writers
    ├── netcdf.py        NetCDFWriter (CF-compliant default)
    ├── geotiff.py       GeoTIFFCollectionWriter, MultiBandGeoTIFFWriter
    └── zarr.py          ZarrWriter (optional extra)
```

```
Pipeline ──▶ BaseReader (Protocol) ──▶ {GeoTIFFReader, NetCDFReader, MultiFileCollectionReader}
                                              │
                                              ▼
                                       xr.DataArray (CRS preservado)
                                              │
Pipeline ──▶ BaseWriter (Protocol) ──▶ {NetCDFWriter, GeoTIFFCollectionWriter,
                                         MultiBandGeoTIFFWriter, ZarrWriter}
                                              │
                                              ▼
                                       Path en disco + procedencia adjunta
```

### Componentes nuevos

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| `BaseReader` | `src/tempify/io/common.py` | Protocol estructural para todos los lectores |
| `BaseWriter` | `src/tempify/io/common.py` | Protocol estructural para todos los escritores |
| `GeoTIFFReader` | `src/tempify/io/readers/geotiff.py` | Lectura single y multi-banda con `rioxarray.open_rasterio` |
| `NetCDFReader` | `src/tempify/io/readers/netcdf.py` | Lectura NetCDF/HDF5 con `xarray.open_dataset` + extracción de variable |
| `MultiFileCollectionReader` | `src/tempify/io/readers/multi.py` | Concat ordenado de múltiples archivos preservando CRS |
| `NetCDFWriter` | `src/tempify/io/writers/netcdf.py` | Escritura CF-compliant con encoding zlib nivel 4 |
| `GeoTIFFCollectionWriter` | `src/tempify/io/writers/geotiff.py` | Una banda temporal por archivo, filename templating |
| `MultiBandGeoTIFFWriter` | `src/tempify/io/writers/geotiff.py` | Un GeoTIFF multi-banda con todas las bandas temporales |
| `ZarrWriter` | `src/tempify/io/writers/zarr.py` | Escritura Zarr chunked (extra opcional) |
| `Provenance` | `src/tempify/io/provenance.py` | Dataclass inmutable con campos de procedencia |
| `compute_provenance_md5` | `src/tempify/io/provenance.py` | Streaming MD5 sobre archivos en disco |
| `attach_provenance_attrs` | `src/tempify/io/provenance.py` | Inyecta atributos de procedencia en `xr.DataArray` |
| `write_provenance_sidecar` | `src/tempify/io/provenance.py` | Escribe `.json` sidecar junto a outputs GeoTIFF |
| Excepciones tipadas | `src/tempify/io/common.py` | `UnsupportedFormatError`, `MissingOptionalDependencyError`, `UnsupportedBandCountError`, `CRSPreservationError` |

### Componentes modificados

No aplica. Esta es la primera implementación de la Capa 1.

## 3. Contratos públicos (APIs)

### Protocols

```python
from pathlib import Path
from typing import Protocol, runtime_checkable
import xarray as xr


@runtime_checkable
class BaseReader(Protocol):
    """Lee una fuente de datos ráster y la materializa como xr.DataArray."""

    def read(self, source: Path | list[Path]) -> xr.DataArray:
        """Lee uno o varios archivos y retorna un DataArray con CRS preservado."""

    def metadata(self) -> dict:
        """Devuelve metadata estática del último read (dims, dtype, CRS, nodata)."""


@runtime_checkable
class BaseWriter(Protocol):
    """Persiste un xr.DataArray en disco con procedencia adjunta."""

    def write(
        self,
        data: xr.DataArray,
        target: Path,
        *,
        overwrite: bool = False,
        provenance: "Provenance | None" = None,
    ) -> Path:
        """Escribe `data` a `target`. Retorna el Path efectivamente escrito."""
```

**Pre-condiciones de `read`:** `source` existe y es legible por GDAL/h5netcdf.
**Post-condiciones de `read`:** retorno con dims `(time, y, x)` o `(month, y, x)`, `rio.crs is not None`.
**Excepciones:** `UnsupportedFormatError`, `UnsupportedBandCountError`, `CRSPreservationError`.

**Pre-condiciones de `write`:** `data` tiene CRS válido vía `rio.crs`; `target.parent` existe.
**Post-condiciones de `write`:** archivo creado; procedencia adjunta (attrs en NetCDF/Zarr, sidecar JSON en GeoTIFF).
**Excepciones:** `FileExistsError` (REQ-006), `MissingOptionalDependencyError` (Zarr sin extra), `CRSPreservationError`.

### Implementaciones de lectores

```python
class GeoTIFFReader:
    def __init__(self, *, masked: bool = True, chunks: dict | None = None) -> None: ...
    def read(self, source: Path | list[Path]) -> xr.DataArray: ...
    def metadata(self) -> dict: ...


class NetCDFReader:
    def __init__(
        self,
        *,
        variable: str | None = None,
        engine: str = "netcdf4",
        chunks: dict | None = None,
    ) -> None: ...
    def read(self, source: Path | list[Path]) -> xr.DataArray: ...
    def metadata(self) -> dict: ...


class MultiFileCollectionReader:
    def __init__(
        self,
        *,
        concat_dim: str = "time",
        sort_by: str = "name",
        underlying: BaseReader | None = None,
    ) -> None: ...
    def read(self, source: list[Path]) -> xr.DataArray: ...
    def metadata(self) -> dict: ...
```

### Implementaciones de escritores

```python
class NetCDFWriter:
    def __init__(
        self,
        *,
        zlib_level: int = 4,
        engine: str = "netcdf4",
        unlimited_dims: tuple[str, ...] = ("time",),
    ) -> None: ...
    def write(
        self,
        data: xr.DataArray,
        target: Path,
        *,
        overwrite: bool = False,
        provenance: Provenance | None = None,
    ) -> Path: ...


class GeoTIFFCollectionWriter:
    DEFAULT_TEMPLATE: str = "{name}_{date:%Y%m%d}.tif"

    def __init__(
        self,
        *,
        filename_template: str = DEFAULT_TEMPLATE,
        compress: str = "deflate",
        predictor: int = 2,
    ) -> None: ...
    def write(
        self,
        data: xr.DataArray,
        target: Path,  # directorio destino
        *,
        overwrite: bool = False,
        provenance: Provenance | None = None,
    ) -> Path: ...


class MultiBandGeoTIFFWriter:
    MAX_BANDS: int = 65535

    def __init__(self, *, compress: str = "deflate", predictor: int = 2) -> None: ...
    def write(
        self,
        data: xr.DataArray,
        target: Path,
        *,
        overwrite: bool = False,
        provenance: Provenance | None = None,
    ) -> Path: ...


class ZarrWriter:  # WHERE [zarr] extra installed
    def __init__(self, *, compressor: str | None = "blosc", consolidated: bool = True) -> None: ...
    def write(
        self,
        data: xr.DataArray,
        target: Path,
        *,
        overwrite: bool = False,
        provenance: Provenance | None = None,
    ) -> Path: ...
```

### Funciones de procedencia

```python
def compute_provenance_md5(path: Path, *, chunk_size: int = 65536) -> str:
    """MD5 hex digest de un archivo, leído en streaming por chunks."""


def attach_provenance_attrs(
    data: xr.DataArray, provenance: Provenance
) -> xr.DataArray:
    """Retorna copia con atributos `tempify_*` poblados en `attrs`."""


def write_provenance_sidecar(provenance: Provenance, target_geotiff: Path) -> Path:
    """Escribe `<target_geotiff>.provenance.json` con la procedencia."""
```

### Excepciones

```python
class IOTempifyError(Exception):
    """Base de todas las excepciones de la Capa 1."""


class UnsupportedFormatError(IOTempifyError): ...
class MissingOptionalDependencyError(IOTempifyError): ...
class UnsupportedBandCountError(IOTempifyError): ...
class CRSPreservationError(IOTempifyError): ...
```

Mensajes en español por NFR-004 (formato: `"[IO-NNN] <mensaje accionable>"`).

## 4. Modelos de datos

### `Provenance`

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class Provenance:
    tempify_version: str
    tempify_method: str
    tempify_params: dict[str, object]
    tempify_md5_inputs: tuple[tuple[str, str], ...]  # ((path, md5), ...)
    tempify_timestamp_utc: str  # ISO-8601, ej "2026-05-16T14:32:11Z"
    reproducibility_mode: str = "parallel"  # ADR-0007
    platform: str = ""
    python_version: str = ""

    def to_netcdf_attrs(self) -> dict[str, str]: ...
    def to_json(self) -> str: ...
```

El payload está alineado con el bloque YAML embebido del `processing-report.schema` (sección 9). El `Provenance` es la unidad mínima persistida por la Capa 1; la Capa 5 (Pipeline) lo enriquece con `detection_confidence`, `warnings`, etc. al construir el reporte completo.

## 5. Algoritmos clave

### 5.1 Streaming MD5 chunked (REQ-003)

Para no cargar archivos multi-GB en memoria, el cálculo de MD5 se hace en streaming con chunks de 64 KiB.

```python
def compute_provenance_md5(path: Path, *, chunk_size: int = 65536) -> str:
    h = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()
```

**Complejidad:** O(N) en bytes, memoria O(1).
**Trade-offs:** MD5 elegido por compatibilidad con ADR-0007 y el schema de procedencia. No es criptográficamente seguro, pero la finalidad es trazabilidad (integridad accidental), no firma. Decisión revisitable: una migración futura a BLAKE3 o SHA256 exigiría bump MAJOR del schema (ver §6).

### 5.2 Concat multi-archivo preservando CRS (REQ-008)

`xarray.concat` puede descartar atributos del accesor `rio` si los archivos llegan con CRS heterogéneamente expresado. El algoritmo:

1. Aplicar `underlying.read` por archivo (delegado al lector subyacente, p. ej. `GeoTIFFReader`).
2. Verificar que todos los CRS sean iguales (`all(da.rio.crs == ref_crs)`). Si no, lanzar `CRSPreservationError`.
3. Ordenar por `sort_by` (`"name"` lexicográfico o `"time_coord"`).
4. `concat = xr.concat(items, dim=concat_dim, combine_attrs="override")`.
5. Re-escribir CRS explícitamente: `concat = concat.rio.write_crs(ref_crs, inplace=False)`.
6. Verificar `concat.rio.crs is not None`; si no, `CRSPreservationError`.

**Complejidad:** O(N·M) donde N es número de archivos y M es tamaño por archivo.
**Trade-offs:** `combine_attrs="override"` descarta inconsistencias menores en atributos. El paso 5 es defensivo contra cambios de comportamiento upstream en rioxarray.

### 5.3 Encoding NetCDF CF-compliant (REQ-004, REQ-007)

Al escribir NetCDF se construye un dict `encoding` por variable:

```python
encoding = {
    name: {
        "zlib": True,
        "complevel": self.zlib_level,
        "_FillValue": data.attrs.get("_FillValue", np.nan),
        "dtype": data.dtype.str,
        "chunksizes": self._infer_chunksizes(data),
    }
}
```

Atributos CF inyectados antes de `to_netcdf`:
- `units`, `calendar` en la coord `time` (heredados o defaults: `"days since 1970-01-01"`, `"proleptic_gregorian"`).
- `standard_name`, `long_name`, `units` en la variable principal (vienen del variable profile vía el pipeline).
- `grid_mapping` apuntando a una variable auxiliar (`spatial_ref` creada por `rio.write_crs`).

**Trade-offs:** Nivel 4 de zlib es el sweet-spot rendimiento/tamaño documentado para datos climáticos (ratio típico 3-5x, sobrecoste de escritura <10%).

### 5.4 Serialización de procedencia (REQ-010)

Dos rutas según formato:

- **NetCDF / Zarr:** atributos en `data.attrs` antes de la escritura (`tempify_version`, `tempify_method`, `tempify_params` serializado como JSON string, `tempify_md5_inputs` serializado como JSON string, `tempify_timestamp_utc`).
- **GeoTIFF (collection o multi-band):** sidecar `.provenance.json` escrito junto a cada `.tif` (un sidecar por archivo en la colección).

**Razón:** los GeoTIFF tienen capacidad limitada para atributos arbitrarios (TIFF tags + GDAL_METADATA item); preservar un JSON externo es más robusto y consumible por terceros.

### 5.5 Ordenamiento de archivos en colecciones

`MultiFileCollectionReader` ordena con uno de dos modos:

1. `sort_by="name"`: orden lexicográfico ASCII de `path.name`. Útil cuando los nombres incluyen fecha en formato ISO.
2. `sort_by="time_coord"`: lee la coord `time` de cada archivo (lectura ligera de metadatos vía `xarray.open_dataset` con `decode_times=True`) y ordena por valor mínimo.

El orden de los archivos se fija para garantizar reproducibilidad bit-exact (ADR-0007). En el cómputo de `md5_inputs` los paths se serializan ya ordenados.

## 6. Decisiones de diseño

### Decisión 1: MD5 vs SHA256 para hashes de procedencia

**Opciones consideradas:**
1. MD5 (128 bits, ~600 MB/s en CPU moderno).
2. SHA256 (256 bits, ~400 MB/s).
3. BLAKE3 (256 bits, ~3 GB/s, requiere dep extra).

**Decisión:** MD5.
**Razón:** REQ-003 lo nombra explícitamente; ADR-0007 ya lo adoptó como hash canónico del proyecto; el caso de uso (trazabilidad de integridad accidental) no requiere resistencia criptográfica. Mantener consistencia con el schema de procedencia evita bumps MAJOR innecesarios.
**Trade-offs:** Vulnerable a colisiones adversariales (no es un riesgo en este contexto). Decisión revisitable si una norma externa (auditoría reproducibilidad, FAIR) lo requiere; en tal caso, ADR nuevo y bump del schema.

### Decisión 2: Sidecar JSON vs tags TIFF para procedencia en GeoTIFF

**Opciones consideradas:**
1. Embedded en `GDAL_METADATA` (XML serializado).
2. Sidecar `.provenance.json` externo.
3. Embedded en `description` (string libre).

**Decisión:** Sidecar JSON.
**Razón:** El payload de procedencia incluye estructuras (lista de tuplas `(path, md5)`, dict de params) que no se acomodan a TIFF tags planos. JSON externo es legible por humanos y por scripts. La pérdida del sidecar es detectable (ausencia del archivo) en lugar de silenciosa.
**Trade-offs:** Dos archivos a mover juntos. Mitigado documentándolo en CHANGELOG y en docstrings.

### Decisión 3: Filename template default para `GeoTIFFCollectionWriter`

**Decisión:** `"{name}_{date:%Y%m%d}.tif"`, donde `{name}` es el nombre de la variable del `xr.DataArray` y `{date}` es la coord temporal.
**Razón:** Coincide con la convención WorldClim/CHELSA invertida y produce nombres ordenables lexicográficamente. La sustitución usa `str.format` con un sub-formateo seguro para `datetime`.
**Pendiente:** Si el catálogo de templates crece (formatos derivados, prefijos de proyecto), se promueve a ADR dedicado y a un módulo `tempify.io.naming`.

### Decisión 4: Localización de recursos compatible con PyInstaller

`tempify.io` no usa `__file__` para resolver rutas de recursos. Cualquier dato de soporte (esquemas, defaults) se accede vía `importlib.resources`, garantizando que el empaquetado en `--onedir` siga funcionando sin reescritura.

### Decisión 5: Dependencia opcional Zarr

`ZarrWriter` se importa de forma lazy. Si el extra `[zarr]` no está instalado, el constructor lanza `MissingOptionalDependencyError` con mensaje en español indicando `pip install tempify[zarr]`. El módulo `tempify.io.writers.zarr` se carga sólo al instanciar la clase, no al importar el paquete (REQ-009).

### Decisión 6: Engine NetCDF

Default `engine="netcdf4"` (REQ-004). Aceptamos `"h5netcdf"` como alternativa transparente si el usuario lo instala. No fijamos `engine` a runtime: lo pasamos a `xarray` y dejamos que escoja según disponibilidad.

## 7. Estrategia de testing

### Tests unitarios

- `test_base_reader_protocol_signature` — verifica que `GeoTIFFReader`, `NetCDFReader`, `MultiFileCollectionReader` satisfacen el Protocol `BaseReader` (REQ-001).
- `test_base_writer_protocol_signature` — análogo para todos los writers (REQ-001).
- `test_geotiff_reader_returns_dataarray_with_crs` — abre fixture single-band y verifica `rio.crs == EPSG:4326` (REQ-002).
- `test_netcdf_reader_returns_dataarray_with_crs` — análogo NetCDF.
- `test_multifile_reader_concat_preserves_crs` — 12 archivos monthly, verifica CRS post-concat (REQ-008).
- `test_multifile_reader_raises_on_heterogeneous_crs` — mezcla 4326 y 3857, espera `CRSPreservationError`.
- `test_netcdf_writer_cf_compliant_zlib_default` — escribe, reabre, verifica `complevel=4` y atributos CF (REQ-004, REQ-007).
- `test_netcdf_writer_includes_cf_attributes` — `units`, `calendar`, `_FillValue`, `standard_name`, `long_name`, `grid_mapping` presentes (REQ-007).
- `test_geotiff_collection_filename_template` — template default y custom, verifica nombres generados (REQ-005).
- `test_geotiff_collection_filename_template_invalid_token` — template con token desconocido, mensaje accionable.
- `test_writer_raises_file_exists_when_overwrite_false` — target existe, sin `overwrite`, `FileExistsError` (REQ-006); archivo no modificado verificado por md5 pre/post.
- `test_writer_overwrites_when_overwrite_true` — caso simétrico.
- `test_provenance_metadata_present_in_output` — NetCDF y GeoTIFF, verifica todos los campos `tempify_*` (REQ-003, REQ-010).
- `test_provenance_serialization_netcdf_and_sidecar_json` — NetCDF en attrs, GeoTIFF en `.provenance.json` (REQ-010).
- `test_compute_provenance_md5_streaming` — archivo de 100 MB sintético, comparar contra `hashlib.md5` one-shot.
- `test_zarr_writer_available_when_extra_installed` — skip si extra ausente; verifica roundtrip si presente (REQ-009).
- `test_zarr_writer_raises_missing_dependency_when_extra_absent` — simular import error vía monkeypatch, verifica `MissingOptionalDependencyError`.
- `test_multibandgeotiff_writer_rejects_excessive_bands` — input con >65535 bandas (mockeado), espera `UnsupportedBandCountError`.
- `test_error_messages_spanish` — barre todas las excepciones tipadas, verifica regex `[IO-\d{3}]` y al menos un término en español (NFR-004).

### Tests property-based (hypothesis)

- `test_md5_idempotent` — hashes repetidos del mismo archivo son iguales.
- `test_concat_associative_on_filename_order` — concat(concat(A,B),C) == concat(A,concat(B,C)) en valores y CRS, para listas aleatorias de 2–12 archivos sintéticos.
- `test_filename_template_collisions` — para inputs con coords temporales únicas, los nombres generados son únicos.

### Tests de integración

- `test_roundtrip_netcdf_preserves_attrs_and_values` — escribe → reabre → compara `np.testing.assert_array_equal` y CRS, attrs, dtype (NFR-001).
- `test_roundtrip_geotiff_collection_preserves_attrs_and_values` — análogo colección.
- `test_roundtrip_multiband_geotiff_preserves_attrs_and_values` — análogo multi-banda.
- `test_roundtrip_zarr_preserves_attrs_and_values` — análogo Zarr (skip si no instalado).
- `test_integration_worldclim_read_write_reopen` — fixture pequeño WorldClim 10min, lee con `GeoTIFFReader`, escribe con `NetCDFWriter`, reabre con `NetCDFReader`, verifica equivalencia.
- `test_crs_preserved_across_concat_and_write` — pipeline mini: 12 GeoTIFFs → concat → NetCDF, verifica CRS en archivo final (REQ-008).

### Benchmarks

- `bench_read_geotiff_stack_12x3000x500` — fixture sintética 12×3000×500, mide tiempo < 5s en SSD (NFR-002). Se ejecuta fuera de CI por convención del proyecto.
- `bench_md5_overhead_on_1gb_file` — verifica que el coste de hashing es <10% del tiempo de I/O.

### Fixtures necesarios

- `tests/fixtures/io/synthetic_monthly_3x3.tif` — single-band fixture (3×3, 12 archivos).
- `tests/fixtures/io/synthetic_monthly_3x3.nc` — equivalente NetCDF.
- `tests/fixtures/io/worldclim_tiny.tif` — fixture WorldClim recortado (10 arc-min, BBOX pequeño).
- `tests/fixtures/io/heterogeneous_crs/` — 2 archivos con CRS distintos.
- Generación lazy de stacks grandes vía `numpy.random.default_rng(42)` (no comiteados al repo).

## 8. Plan de migración

No aplica. Esta es la primera implementación. Versiones futuras que cambien la firma de `Provenance` o el formato del sidecar JSON requerirán bump MAJOR del paquete (ver schema en §6 y `processing-report.schema`).

## 9. Métricas de calidad

| Métrica | Umbral |
|---|---|
| Coverage del módulo `tempify.io` | ≥ 85% (NFR-003) |
| Lectura GeoTIFF 12×3000×500 en SSD | < 5 s (NFR-002) |
| Memoria peak en lectura streaming | < 2× tamaño de archivo |
| `mypy --strict tempify.io` | 0 errores |
| `ruff check tempify.io` | 0 warnings |
| Docstrings NumPy en API pública | 100% |

## 10. Trazabilidad requirements → design

| Requirement | Componente que lo implementa | Test |
|---|---|---|
| REQ-001 | `BaseReader`, `BaseWriter` Protocols en `common.py` | `test_base_reader_protocol_signature`, `test_base_writer_protocol_signature` |
| REQ-002 | Todos los readers retornan `xr.DataArray` con `rio.crs` poblado | `test_*_reader_returns_dataarray_with_crs` |
| REQ-003 | `Provenance` + `compute_provenance_md5` + `attach_provenance_attrs` | `test_provenance_metadata_present_in_output` |
| REQ-004 | `NetCDFWriter` con `zlib_level=4` default | `test_netcdf_writer_cf_compliant_zlib_default` |
| REQ-005 | `GeoTIFFCollectionWriter.DEFAULT_TEMPLATE` y `filename_template` | `test_geotiff_collection_filename_template` |
| REQ-006 | Check `target.exists() and not overwrite` en cada writer | `test_writer_raises_file_exists_when_overwrite_false` |
| REQ-007 | Inyección de atributos CF en `NetCDFWriter._build_encoding` y prep de attrs | `test_netcdf_writer_includes_cf_attributes` |
| REQ-008 | `MultiFileCollectionReader._concat_with_crs` + `rio.write_crs` post-write | `test_crs_preserved_across_concat_and_write` |
| REQ-009 | `ZarrWriter` con import lazy y `MissingOptionalDependencyError` | `test_zarr_writer_available_when_extra_installed` |
| REQ-010 | `Provenance.to_netcdf_attrs` + `write_provenance_sidecar` | `test_provenance_serialization_netcdf_and_sidecar_json` |
| NFR-001 | Roundtrip tests por formato | `test_roundtrip_*_preserves_attrs_and_values` |
| NFR-002 | Lectura via rioxarray + chunks Dask defaults | `bench_read_geotiff_stack_12x3000x500` |
| NFR-003 | Diseño modular permite ≥85% coverage | `pytest --cov=tempify.io --cov-fail-under=85` |
| NFR-004 | Excepciones con mensajes en español y código `[IO-NNN]` | `test_error_messages_spanish` |
