# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `docs/tutorials/01-getting-started.ipynb`: Colab notebook que recorre la API pública de `tempify` v0.1.0 end-to-end sobre el sample sintético WorldClim Chile Central. Demuestra los cuatro métodos de interpolación, la garantía de conservación de media de `pchip_mp`, y el reporte de procedencia. Reproducible en Google Colab vía badge "Open in Colab".

### Pendiente para v0.2.0

- Capa 7 (GUI) basada en PySide6 (deferred del v0.1.0).
- Empaquetado Windows (PyInstaller `--onedir` + Inno Setup) (deferred del v0.1.0).
- Integración de redes neuronales pre-entrenadas (ClimaX, Pangu-Weather, FourCastNet) bajo patrón híbrido (clásico baseline + NN refinement). Ver [ADR-0017](docs/adr/0017-neural-interpolator-extensibility.md).

## [0.1.0] — 2026-05-16

Primera versión funcional del paquete `tempify` con todas las capas
fundacionales implementadas, testeadas y documentadas bajo régimen
Spec-Driven Development (SDD) estricto.

### Capacidades

- **4 métodos de interpolación temporal** mensual → diaria, con vectorización Dask y manejo configurable de NaN (`raise`, `propagate_all`, `skip_pixel`):
  - `LinearInterpolator`
  - `PchipInterpolator` (Fritsch-Carlson, C¹ en frontera Dic-Ene).
  - `PchipMeanPreservingInterpolator` (Rymes-Myers iterativo con conservación de media mensual <1e-4 °C).
  - `FourierInterpolator` (FFT multi-armónico configurable 1..5).
- **Climatological wraparound** como feature de primer orden (ADR-0016): extensión artificial del dominio anual de 12 a ≥14 puntos para mejor contexto en métodos suaves; off-switch explícito vía `wraparound=False`.
- **Convención midpoint** (ADR-0015 / CF Conventions §7.4): valores mensuales se colocan en el centroide del mes; configurable vía `monthly_anchor`.
- **Capa I/O** con readers para GeoTIFF y NetCDF (single + multi-file collection con orden NFC determinista) y writers CF-compliant (NetCDF zlib L4, GeoTIFF multi-banda + collection con sidecar JSON de procedencia, Zarr opcional).
- **Capa Detection** con `StructureDetector` (mode A/B/C + filtrado de sidecars) y `TemporalFrequencyResolver` (4 tiers: CF metadata → filename pattern → count heuristic → callback, con 4 parsers built-in: WorldClim, CHELSA, CHIRPS, ERA5).
- **Capa Validation** con `GeospatialCoherenceValidator` (tolerancias canónicas ADR-0009), `MethodVariableCompatibilityChecker` (rechazo de precipitación con métodos suaves per ADR-0004, override expreso `--force-method`), `PostInterpolationValidator` (mean preservation, cyclic continuity, physical range, NaN integrity), `StatisticalReporter`, `VariableProfileMatcher` con 4 perfiles built-in (temperature, precipitation, relative_humidity, solar_radiation).
- **Capa Pipeline** con `TempifyPipeline.run()` orquestando 7 fases canónicas (detect, validate_geospatial, validate_compatibility, interpolate, validate_post, write, generate_report) + `ProcessingReport` con procedencia completa (versión, timestamp UTC, MD5 inputs/outputs, configuración).
- **Capa CLI** con 5 subcomandos (`convert`, `inspect`, `validate`, `profiles list`, `version`) en español, exit codes canónicos (0/1/2/3/130), confirmación tipeada para `--force-method`.

### Decisiones documentadas (ADRs)

17 ADRs cubriendo: xarray como abstracción central, Dask scheduler, Typer CLI, política de precipitación, PySide6 (diferido), PyInstaller (diferido), política de reproducibilidad (strict vs parallel), confidence scoring, tolerancias geo, conservación de media, ADRs 0011-0013 diferidos, naming TempifyPipeline, posicionamiento midpoint, climatological wraparound, y extensibilidad para NN bajo patrón híbrido.

### Métricas verificables

- **241 tests** pasando (1 skipped por extra opcional `zarr`).
- **Cobertura ≥ 91%** (umbral mínimo configurado: 85%).
- `mypy --strict` limpio en 46 módulos.
- `ruff check` + `ruff format` limpios.
- Demo end-to-end reproducible en `examples/` (WorldClim sintético Chile Central).

### Compatibilidad

- Python 3.11, 3.12, 3.13.
- Linux, macOS, Windows.
- Wheel pip-instalable; conda-forge planificado para v0.1.x.

### Contacto

Mantenido por [ICTA Ltda.](https://icta.cl), Santiago, Chile.

## [Pre-historia]

### Initial project structure (pre-v0.1.0)

- Proyecto inicializado bajo el nombre **tempify** (temporal densification for raster stacks).
- Estructura siguiendo Spec-Driven Development + Harness Engineering.
- Steering docs: product, tech, architecture, conventions, harness rules.
- 9 specs SDD (requirements + design + tasks).
- Slash commands: `/spec-init`, `/spec-design`, `/spec-tasks`, `/impl`, `/review`.
- Git hooks: pre-commit, pre-task, post-task.
- Referencia de validación empírica: experimento Quinta Normal 2020 + stack 3×3 sintético.
