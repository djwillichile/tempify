# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `TemporalFrequencyResolver`: nueva sub-heurística Tier 3.b para inputs de **un solo archivo multibanda**. Cuando `N=1` y el `.tif` tiene 12 bandas, el resolver clasifica la frecuencia como `climatological` sin necesidad de que el usuario splittee el stack en 12 archivos separados. Probado con WorldClim v2.1 Alto Maipo (12 bandas, 126×147 px).
- `TempifyPipeline._read`: renombrado automático de la dimensión `band` → `month` para multiband stacks de 12 capas, manteniendo compatibilidad con los flujos existentes (single GeoTIFF de 1 banda, multi-file collection).
- 2 tests unitarios nuevos en `tests/unit/detection/test_frequency.py`: caso multibanda de 12 bandas (debe inferir climatological) y caso single-band (debe caer al callback/raise).
- Sample WorldClim real en `examples/data/worldclim_maipo_alto/wc1_6_maipo_alto_tavg_stack.tif` (220 KB, Alto Maipo, Chile, EPSG:4326, 30s res). Demuestra que tempify acepta multibanda nativamente.
- Segundo tutorial Colab en `docs/tutorials/02-real-worldclim-maipo.ipynb` (18 celdas, ~640 KB): caso real con WorldClim Alto Maipo, mapas mensuales del input, 4 fechas diarias representativas del output, ciclo anual cordillera vs valle. Demuestra el contraste altitudinal (−18 °C en alta cordillera invernal a +23 °C en valle estival).
- **Política de seguridad**: `SECURITY.md` con canal de reporte privado (GitHub PVR + email institucional), versiones soportadas, SLAs de respuesta. Cumple REQ-SEC-001.
- **Spec de seguridad**: `specs/security/requirements.md` con 10 REQs (REQ-SEC-001 a REQ-SEC-010) cubriendo divulgación responsable, prohibición de patrones unsafe, version consistency, notebook hygiene, governance files, CI gating, supply chain. Indexada en `CLAUDE.md`.
- **Auditoría de seguridad**: `specs/_audit/2026-05-17-security-audit.md` con el reporte completo (0 críticos/altos, 3 MED, 6 LOW). 5 hallazgos ya corregidos en este release; 4 quedan tracked para v0.1.3 (CI, governance docs, tests/security/).

### Fixed

- **Drift de versión (H-001 de la auditoría):** `pyproject.toml` declaraba `version = "0.1.0"` mientras `__version__` ya estaba en `0.1.2`. Sincronizado a `0.1.2`. Ahora `pip show tempify`, `tempify.__version__`, `CITATION.cff::version` y el tag de release coinciden bit-exactamente con la versión archivada en Zenodo (DOI 10.5281/zenodo.20251750).
- **Username del desarrollador filtrado en outputs cacheados** (H-004): sanitizadas 2 occurrences en `docs/tutorials/01-getting-started.ipynb` (paths `C:\Users\Guillermo\AppData\...` → `C:\Users\runner\AppData\...`).

### Pendiente para v0.2.0

- Capa 7 (GUI) basada en PySide6 (deferred del v0.1.0).
- Empaquetado Windows (PyInstaller `--onedir` + Inno Setup) (deferred del v0.1.0).
- Integración de redes neuronales pre-entrenadas (ClimaX, Pangu-Weather, FourCastNet) bajo patrón híbrido (clásico baseline + NN refinement). Ver [ADR-0017](docs/adr/0017-neural-interpolator-extensibility.md).

## [0.1.2] — 2026-05-17

Release de empaquetado, documentación y metadatos. Sin cambios funcionales en el código del paquete (`src/tempify/` queda byte-idéntico a v0.1.0/v0.1.1 más el bump de versión). El motivo principal de este release es:

1. **Disparar el webhook de Zenodo** (activado tras v0.1.1 y antes de v0.1.2) para que mintee un DOI sobre un release válido.
2. **Arreglar el `CITATION.cff`** que tenía un ORCID placeholder (`0000-0000-0000-0000`), causa de que Zenodo rechazara el ingest de v0.1.1.
3. **Publicar la landing page** del proyecto en GitHub Pages (`docs/index.html`).

### Added

- `docs/index.html`: landing page en español con la paleta corporativa de ICTA digital (verde→teal→cyan→azul, fondo claro). Incluye hero con imagen de stacks ráster, visualización SVG inline de la curva PCHIP sobre la climatología real de Santiago (12 nodos mensuales → 365 valores diarios), tabla numérica de los 4 métodos, quickstart con código copy-paste, tarjeta del tutorial Colab, sección de roadmap v0.2.0 destacando el ejecutable Windows, footer con BibTeX y datos de contacto institucional. Servida desde GitHub Pages en `https://djwillichile.github.io/tempify/`.
- `docs/assets/`: directorio para los assets visuales del landing.
- `docs/.nojekyll`: para que GH Pages sirva el HTML directamente sin pasar por Jekyll.
- Notebook tutorial: nueva celda 4.2.bis con la curva PCHIP del píxel central renderizada con la paleta ICTA (réplica matplotlib del SVG del landing).
- Notebook tutorial: la sección 4.5 (línea de tiempo 3D) ahora muestra 4 anclas mensuales (Ene/Abr/Jul/Oct) marcadas en rojo + 3 días interpolados translúcidos a cada lado, en lugar de 10 días consecutivos. La separación entre grupos hace evidente el rol de las anclas como "puntos de referencia" entre los que `tempify` interpola.

### Fixed

- `CITATION.cff`: ORCID placeholder `0000-0000-0000-0000` reemplazado por el real (`0000-0002-7864-4899`); afiliación institucional canónica tomada del repo `geoia-bloom-huasco` (ICTA Ltda. + Universidad San Sebastián); campos `version` y `date-released` actualizados a `0.1.2` / `2026-05-17`. Verificado contra schema CFF 1.2.0 con `cffconvert --validate`.
- `README.md`: nuevo bloque "Citar este software" con cita corta estilo APA + BibTeX expandido (nombre completo, ORCID, organization, version 0.1.2).

### Changed

- `src/tempify/__init__.py`: `__version__ = "0.1.1" -> "0.1.2"`.

## [0.1.1] — 2026-05-17

Release de documentación. Sin cambios en el código de producción del paquete (`src/tempify/` queda idéntico a v0.1.0 más el bump de versión); todos los cambios están en `docs/tutorials/`.

### Added

- `docs/tutorials/01-getting-started.ipynb`: Colab notebook que recorre la API pública de `tempify` end-to-end sobre el sample sintético WorldClim Chile Central. Demuestra los cuatro métodos de interpolación, la garantía de conservación de media de `pchip_mp` (≤ 1e-4 °C, observado ~1e-14 °C en float64), y el reporte de procedencia. Reproducible en Google Colab vía badge "Open in Colab". Incluye:
  - Quickstart con `pchip_mp`.
  - Inspección del NetCDF de salida y grid 3×4 con un raster por mes.
  - Línea de tiempo 3D con anclas mensuales destacadas para visualizar la interpolación entre nodos observados.
  - Comparación numérica de los 4 métodos (tabla `max|diff|` + RMSE).
  - Renderizado del `ProcessingReport` en Markdown y JSON.
  - Lectura crítica (cuándo usar cada método, convención midpoint, climatological wraparound, política de precipitación).

### Fixed

- Notebook tutorial: corrección del slicing por píxel (`daily[:, 15, 15]` → `daily.isel(y=15, x=15)`); el writer NetCDF produce dims `(y, x, time)`, no `(time, y, x)`, por lo que la indexación posicional devolvía silenciosamente una columna espacial en vez de la serie temporal. Plots de Demo 1 y Demo 2 ahora muestran las 4 series diarias recorriendo el año completo.
- Notebook tutorial: corrección del texto sobre `fourier` que afirmaba conservación de media "por construcción"; la métrica empírica (~0.83 °C con 3 armónicos) refuta esa afirmación. El markdown ahora dirige a `pchip_mp` cuando se requiere conservación estricta.
- Notebook tutorial: celda de instalación cambiada de `subprocess.check_call` con `--quiet` (que ocultaba errores de pip en Colab) a la magic `%pip install` de IPython con output visible.

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
