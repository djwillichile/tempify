# Architecture

## Visión general

Arquitectura en **5 capas con separación estricta**. Cada capa tiene un contrato definido y se testea aisladamente.

```
┌─────────────────────────────────────────────────────────────┐
│  CLI Layer (tempify.cli)                             │
│  ─ Typer commands, prompts interactivos, reporte final       │
├─────────────────────────────────────────────────────────────┤
│  Pipeline Layer (tempify.pipeline)                   │
│  ─ Orquestación, ReportGenerator, metadata de procedencia    │
├─────────────────────────────────────────────────────────────┤
│  Domain Layers (intercambiables vía interfaces)             │
│  ┌──────────────┐ ┌────────────┐ ┌───────────────────────┐  │
│  │ detection    │ │ validation │ │ interpolation         │  │
│  │ ─ Structure  │ │ ─ Geo      │ │ ─ Linear              │  │
│  │ ─ Frequency  │ │ ─ Post-int │ │ ─ PCHIP               │  │
│  │ ─ Variable   │ │ ─ Compat   │ │ ─ PCHIP+RM            │  │
│  └──────────────┘ └────────────┘ │ ─ Fourier             │  │
│                                  └───────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  I/O Layer (tempify.io)                              │
│  ─ Readers (GeoTIFF, NetCDF, MultiFile)                      │
│  ─ Writers (NetCDF CF, GeoTIFF coll, MultiBand, Zarr)        │
│  ─ Metadata handling                                         │
└─────────────────────────────────────────────────────────────┘
```

## Capa 1: I/O (`tempify.io`)

**Responsabilidad:** aislar todo conocimiento de formatos del resto del sistema.

```python
class BaseReader(Protocol):
    def read(self, source: Path | list[Path]) -> xr.DataArray: ...
    def metadata(self) -> dict: ...

class BaseWriter(Protocol):
    def write(self, data: xr.DataArray, target: Path, **opts) -> Path: ...
```

**Implementaciones:**
- `GeoTIFFReader`, `NetCDFReader`, `MultiFileCollectionReader`
- `NetCDFWriter` (CF-compliant, default), `GeoTIFFCollectionWriter`, `MultiBandGeoTIFFWriter`, `ZarrWriter`

**Contrato de salida** (`xr.DataArray`):
- Dimensiones: `(time, y, x)` u opcionalmente `(month, y, x)`
- Coordenada `time` con units y calendar CF
- Atributos: `_FillValue`, `units`, `long_name`, `standard_name`
- CRS preservado vía `rio` accessor

## Capa 2: Detection (`tempify.detection`)

**Responsabilidad:** identificar QUÉ son los datos antes de procesarlos.

**Componentes:**

- `StructureDetector` decide: stack único (A), colección de monocapas (B), lista explícita (C).
- `TemporalFrequencyResolver` aplica jerarquía:
  1. CF-conventions (`time.units`, `time.calendar`)
  2. Parsing de nomenclatura (regex catalog: WorldClim, CHELSA, CHIRPS, ERA5)
  3. Heurística por conteo
  4. Solicitud interactiva (callback al CLI o parámetro en API)
- `VariableProfileMatcher` identifica variable y carga perfil desde `profiles/*.yaml`.

**Output:**
```python
@dataclass
class DetectionResult:
    structure_mode: Literal["A", "B", "C"]
    temporal_frequency: TemporalFrequency
    variable_profile: VariableProfile
    files: list[Path]
    confidence: dict[str, float]
```

## Capa 3: Validation (`tempify.validation`)

**Responsabilidad:** verificar invariantes antes y después de procesar.

- `GeospatialCoherenceValidator`: CRS, extensión, resolución, nodata
- `MethodVariableCompatibilityChecker`: combinaciones permitidas según perfil
- `PostInterpolationValidator`: conservación, continuidad cíclica, rango físico
- `StatisticalReporter`: min/max/mean/std/nan% por banda temporal

**Política de fallos:**
- Validaciones pre-proceso: **fail-fast** con error claro.
- Validaciones post-proceso: registrar en reporte; advertir pero no abortar.

## Capa 4: Interpolation (`tempify.interpolation`)

**Responsabilidad:** conversión temporal pura, sin conocimiento de I/O.

```python
class BaseInterpolator(ABC):
    @abstractmethod
    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        **opts
    ) -> xr.DataArray: ...
```

**Implementaciones:**
- `LinearInterpolator`
- `PchipInterpolator` (nodos cíclicos por defecto)
- `PchipMeanPreservingInterpolator` (Rymes-Myers iterativo)
- `FourierInterpolator(n_harmonics: int)`

**Vectorización:** todas usan `xr.apply_ufunc` con `dask="parallelized"`.

## Capa 5: Pipeline (`tempify.pipeline`)

**Responsabilidad:** orquestar end-to-end y producir reporte.

```python
class TempifyPipeline:
    def __init__(self, config: PipelineConfig): ...

    def run(self, source: Path | list[Path]) -> PipelineResult:
        detection = self._detect(source)
        self._validate_geospatial(detection)
        self._validate_compatibility(detection)
        result = self._interpolate(detection)
        validation = self._validate_post(result, detection)
        outputs = self._write(result)
        report = self._generate_report(detection, validation, outputs)
        return PipelineResult(outputs=outputs, report=report)
```

## Capa 6: CLI (`tempify.cli`)

**Responsabilidad:** interfaz humana, sin lógica de negocio.

```bash
tempify convert <input> --output <output> [opts]
tempify inspect <input>      # Solo detección
tempify validate <input>     # Solo validación
tempify profiles list
tempify version
```

## Reglas arquitectónicas duras

1. **Capas inferiores no conocen capas superiores.** I/O no sabe de Detection; Detection no sabe de Pipeline.
2. **Dependencias por interfaces.** Protocols/ABCs, no clases concretas.
3. **`xr.DataArray` es el formato de intercambio interno.** Conversiones solo en I/O.
4. **No state global.** Configs explícitas; sin singletons.
5. **Errores tipados.** Cada capa define sus excepciones (`GeospatialIncoherenceError`, `UnknownFrequencyError`).

## ADRs pendientes para v1.0

- ADR-0001: Por qué xarray y no pandas/geopandas como abstracción central
- ADR-0002: Por qué Dask y no multiprocessing nativo
- ADR-0003: Por qué Typer y no Click o argparse
- ADR-0004: Tratamiento de precipitación (rechazo vs módulo separado)
