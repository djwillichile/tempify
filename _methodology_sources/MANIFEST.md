# Manifest — Fuentes para la redacción del capítulo de metodología

> **Snapshot:** `tempify` @ `0715cfde878d7927f4a05923d14ee64e5affecfb` (post-PR #67).
> **Propósito:** entregar al redactor (humano o LLM en sesión externa) todos los archivos del repositorio necesarios para escribir `docs/methodology/methodology.md` + `methodology_en.md` siguiendo el outline acordado, sin necesidad de clonar el repo completo.
> **Cómo usar:** abre el archivo en `<sección>` listada abajo; los paths relativos están preservados respecto a la raíz del repo (excepto que viven bajo `_methodology_sources/`).

---

## Outline del capítulo (recordatorio)

1. Planteamiento del problema
2. Fundamentos matemáticos
3. Catálogo de métodos
4. Algoritmo PCHIP+RM (mean-preserving)
5. Validación empírica
6. Casos de uso documentados
7. Limitaciones y no-objetivos
8. Comparación con software existente
9. Reproducibilidad y procedencia

---

## Matriz archivo → sección

| Archivo | §1 | §2 | §3 | §4 | §5 | §6 | §7 | §8 | §9 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `project_meta/README.md` | ★ |   |   |   |   | ★ |   |   |   |
| `project_meta/CHANGELOG.md` |   |   |   |   |   |   |   |   | ★ |
| `project_meta/CITATION.cff` |   |   |   |   |   |   |   |   | ★ |
| `project_meta/REFERENCES.bib` | ★ |   | ★ | ★ |   | ★ |   |   | ★ |
| `project_meta/precipitation.md` | ★ |   |   |   |   |   | ★ |   |   |
| `steering/architecture.md` |   |   |   |   |   |   |   |   | ★ |
| `steering/tech.md` |   |   |   |   |   |   |   | ★ | ★ |
| **CÓDIGO — Capa Interpolation** |   |   |   |   |   |   |   |   |   |
| `code/interpolation/base.py` |   | ★ |   |   |   |   |   |   |   |
| `code/interpolation/_kernels.py` |   |   | ★ | ★ |   |   |   |   |   |
| `code/interpolation/linear.py` |   |   | ★ |   |   |   |   |   |   |
| `code/interpolation/pchip.py` |   |   | ★ |   |   |   |   |   |   |
| `code/interpolation/pchip_mp.py` |   |   | ★ | ★ |   |   |   |   |   |
| `code/interpolation/akima.py` |   |   | ★ |   |   |   |   |   |   |
| `code/interpolation/cubic.py` |   |   | ★ |   |   |   |   |   |   |
| `code/interpolation/fourier.py` |   |   | ★ |   |   |   |   |   |   |
| `code/constants.py` |   |   |   | ★ |   |   |   |   |   |
| `code/api.py` |   |   |   |   |   |   |   |   | ★ |
| **CÓDIGO — Capa Pipeline** |   |   |   |   |   |   |   |   |   |
| `code/pipeline/config.py` |   |   |   |   |   |   |   |   | ★ |
| `code/pipeline/core.py` |   |   |   |   |   |   |   |   | ★ |
| `code/pipeline/report.py` |   |   |   |   |   |   |   |   | ★ |
| **CÓDIGO — Capa Validation** |   |   |   |   |   |   |   |   |   |
| `code/validation/post.py` |   |   |   |   | ★ |   |   |   |   |
| `code/validation/profiles.py` |   |   |   |   |   |   | ★ |   |   |
| `code/validation/compatibility.py` |   |   |   |   |   |   | ★ |   |   |
| `code/profiles/temperature.yaml` |   |   |   |   |   |   | ★ |   |   |
| `code/profiles/precipitation.yaml` |   |   |   |   |   |   | ★ |   |   |
| `code/profiles/solar_radiation.yaml` |   |   |   |   |   |   | ★ |   |   |
| `code/profiles/relative_humidity.yaml` |   |   |   |   |   |   | ★ |   |   |
| `code/datasets.py` |   |   |   |   | ★ |   |   |   |   |
| **ADRs** |   |   |   |   |   |   |   |   |   |
| `adr/0001-use-xarray-as-central-abstraction.md` |   |   |   |   |   |   |   | ★ | ★ |
| `adr/0002-dask-vs-multiprocessing.md` |   |   |   |   |   |   |   | ★ | ★ |
| `adr/0004-precipitation-policy.md` |   |   |   |   |   |   | ★ |   |   |
| `adr/0007-reproducibility-policy.md` |   |   |   |   |   |   |   |   | ★ |
| `adr/0010-mean-preservation-tolerance.md` |   |   |   | ★ | ★ |   |   |   |   |
| `adr/0014-tempifypipeline-naming-correction.md` |   |   |   |   |   |   |   |   | ★ |
| `adr/0015-monthly-value-temporal-placement.md` |   | ★ |   |   |   |   |   |   |   |
| `adr/0016-climatological-wraparound.md` |   | ★ | ★ |   |   |   |   |   |   |
| `adr/0018-classical-interpolator-catalog.md` |   |   | ★ |   |   |   |   |   |   |
| **Specs SDD** |   |   |   |   |   |   |   |   |   |
| `specs/core-interpolation/requirements.md` |   |   |   | ★ |   |   |   |   |   |
| `specs/core-interpolation/design.md` |   |   | ★ | ★ |   |   |   |   |   |
| `specs/validation/requirements.md` |   |   |   |   | ★ |   |   |   |   |
| `specs/validation/design.md` |   |   |   |   | ★ |   |   |   |   |
| `specs/pipeline/requirements.md` |   |   |   |   |   |   |   |   | ★ |
| `specs/pipeline/design.md` |   |   |   |   |   |   |   |   | ★ |
| **Examples (scripts ejecutables)** |   |   |   |   |   |   |   |   |   |
| `examples/run_demo.py` |   |   |   |   | ★ |   |   |   |   |
| `examples/bench_max_diff.py` |   |   |   |   | ★ |   |   |   |   |
| `examples/generate_worldclim_sample.py` |   |   |   |   | ★ |   |   |   |   |
| `examples/regenerate_maipo_timeseries.py` |   |   |   |   | ★ |   |   |   |   |
| `examples/regenerate_maipo_monthly_grid.py` |   |   |   |   | ★ |   |   |   |   |

---

## Guía por sección

### §1 — Planteamiento del problema

**Lee primero:**
- `project_meta/README.md` (secciones "¿Para qué sirve?" — ya contiene la prosa base con citas)
- `project_meta/precipitation.md` (ejemplo de redacción metodológica adyacente)
- `project_meta/REFERENCES.bib` (entradas: fick_hijmans_2017, karger_2017, abatzoglou_2018, harris_2020, allen_1998, mcmaster_wilhelm_1997, hijmans_graham_2006)

**Insight clave a incluir:** la brecha mensual→diaria es un problema de "interpolación de promedios" (mean-preserving), NO un problema de "interpolación puntual" (curve-fitting). Esta distinción justifica todo §4.

---

### §2 — Fundamentos matemáticos

**Lee primero:**
- `adr/0015-monthly-value-temporal-placement.md` (decisión midpoint; tabla canónica de DOY por mes en años comunes vs bisiestos)
- `adr/0016-climatological-wraparound.md` (padding cíclico 4-pt; por qué se necesita C¹ en frontera Dic-Ene)
- `code/interpolation/base.py` (clase `TemporalAxis`, método `monthly_anchor_doys()`)

**Fórmulas que ya están en los ADRs:** definición formal del centroide, equivalencia con CF Conventions §7.4 (variable `time_bnds`), aritmética de `period = n_days_target + 1.0` en el wraparound.

---

### §3 — Catálogo de métodos

**Lee primero:**
- `adr/0018-classical-interpolator-catalog.md` (tabla resumen oficial de los 6 métodos; roadmap a `cubic_mp_lai_kaplan` para v0.2.0)
- `code/interpolation/_kernels.py` (los 6 kernels NumPy puros: `linear_kernel`, `pchip_kernel`, `akima_kernel`, `cubic_kernel`, `fourier_kernel`, `pchip_mp_kernel`)
- `code/interpolation/{linear,pchip,akima,cubic,fourier}.py` (las clases wrapper con `BaseInterpolator`; los docstrings tienen las fórmulas en notación numpydoc)
- `specs/core-interpolation/design.md` (§5 tiene la derivación completa de cada método; §6 la tabla comparativa canónica)

**Para la tabla §3.7:** los valores `max|diff|` reales medidos están en el commit message de PR #61 y en el código de `examples/bench_max_diff.py`. Reproducir con `python examples/bench_max_diff.py` desde el repo da:
- linear: 5.58 × 10⁻¹ °C
- pchip: 3.23 × 10⁻¹ °C
- pchip_mp: ~10⁻¹⁴ °C (machine epsilon, NO el iterador trabajando)
- fourier: 8.32 × 10⁻¹ °C
- akima: 3.26 × 10⁻¹ °C
- cubic: 2.82 × 10⁻¹ °C

---

### §4 — Algoritmo PCHIP+RM (el corazón del documento)

**Lee primero (en este orden):**
1. `adr/0010-mean-preservation-tolerance.md` — política jerárquica de 3 niveles de tolerancia (1e-6 iterador / 1e-4 contractual / variable per profile)
2. `code/interpolation/pchip_mp.py` — la clase `PchipMeanPreservingInterpolator` (docstring + constructor + `interpolate()`)
3. `code/interpolation/_kernels.py` — bajar a la función `pchip_mp_kernel()` (el corrector iterativo, ~30 líneas)
4. `specs/core-interpolation/requirements.md` — REQ-006 (criterio de paro), REQ-007 (stamping de attrs), REQ-008 (NaN handling pre-iteración)
5. `specs/core-interpolation/design.md` — §5.3 con pseudocódigo del corrector + análisis de convergencia
6. `code/constants.py` — los `DEFAULT_RM_*` literales

**🔑 INSIGHT CRÍTICO a destacar en §4.2 (descubierto en auditoría externa):**

El valor empírico `max|diff| ≈ 10⁻¹⁴ °C` que se reporta como evidencia de mean preservation **NO se debe al iterador Rymes-Myers haciendo el trabajo**. Verificación empírica directa (`examples/bench_max_diff.py`):

```text
max_abs_diff = 1.0658141036e-14 degC
rymes_myers_iterations_max = 0      ← cero
rymes_myers_converged = 1
float64_eps = 2.220e-16
```

`iterations_max = 0` significa que el iterador **nunca aplicó una corrección**. El baseline PCHIP+wraparound cíclico-4pt ya satisface `max|error| < convergence_tol=1e-6` antes de la primera iteración, por lo que el iterador sale por el break del criterio de paro. Lo que queda es ruido `float64` puro (`eps × 15 ≈ 3 × 10⁻¹⁵`, coherente con el observado ~10⁻¹⁴).

**Implicación para la redacción:** el método se llama "PCHIP+Rymes-Myers" porque incluye el corrector como red de seguridad para datos con curvatura extrema. Para los climáticos estándar (T, RH, solar), PCHIP base ya converge. La garantía contractual de 10⁻⁴ es conservadora; el observado es 10¹⁰ veces más estricto.

**Para §4.3 (alternativas modernas):**
- Mencionar Lai & Kaplan 2022 (entrada `lai_kaplan_2022` en `REFERENCES.bib`)
- Roadmap a `cubic_mp_lai_kaplan` en v0.2.0 documentado en `adr/0018`

---

### §5 — Validación empírica

**Lee primero:**
- `examples/generate_worldclim_sample.py` — genera el sample sintético Chile Central (60×60 px). Lee también `code/datasets.py` que define `SANTIAGO_MONTHLY_TAVG` y la grilla.
- `examples/bench_max_diff.py` — script que genera la tabla §3.7. Reproducible.
- `examples/run_demo.py` — verificación E2E que asserta `max_diff < 1e-4` para `pchip_mp`.
- `examples/regenerate_maipo_*.py` — los 2 scripts del caso real Alto Maipo (figuras del landing).
- `code/validation/post.py` — `PostInterpolationValidator` (nivel 2 de ADR-0010).
- `specs/validation/requirements.md` — REQ-005, REQ-007 (chequeos post-interpolación contractuales).

**Datos reales del Alto Maipo:** `examples/data/worldclim_maipo_alto/wc1_6_maipo_alto_tavg_stack.tif` (12 bandas, 126×147 px, EPSG:4326, bbox aprox −71.0,−34.1 / −69.8,−33.0). **No** está copiado en este directorio (es binario y pesa); el redactor puede mencionarlo con su path.

---

### §6 — Casos de uso

**Lee primero:**
- `project_meta/README.md` — secciones "Grados-día", "Evapotranspiración", "Modelos de distribución de especies" ya tienen prosa base con citas. Conviene refundir y expandir.
- `project_meta/REFERENCES.bib` — para verificar las citas exactas y BibTeX keys.

**Sugerencia:** las prosas del README son de calidad pero compactas. En §6 expandir cada caso con: (1) ecuación del estimador, (2) por qué la curvatura del input importa formalmente, (3) magnitud del sesgo si se usa media mensual directa.

---

### §7 — Limitaciones y no-objetivos

**Lee primero:**
- `project_meta/precipitation.md` — documento ya existente; **NO duplicar**, solo referenciar.
- `adr/0004-precipitation-policy.md` — la decisión política y su implementación.
- `code/profiles/*.yaml` — los 4 perfiles definen `allowed_methods` por variable.
- `code/validation/compatibility.py` — implementación del checker; el set `SMOOTH_METHODS` lista los 6 métodos rechazados por defecto sobre precipitación (post-PR #66).
- `code/validation/profiles.py` — el set `ALLOWED_METHODS` global.

**No-objetivos a listar explícitamente:**
- Sin downscaling espacial.
- Sin generación de variabilidad sinóptica (no es weather generator).
- Sin relleno de gaps ni manejo de series con missing months.
- Sin homogeneización temporal ni QC del input.
- Sin extrapolación temporal fuera del año-objetivo.
- Precipitación rechazada con métodos suaves por defecto (override expreso requerido).

---

### §8 — Comparación con software existente

**Lee primero:**
- `steering/tech.md` — decisiones de stack (xarray, dask, scipy) con justificación.
- `adr/0001-use-xarray-as-central-abstraction.md`, `adr/0002-dask-vs-multiprocessing.md` — racional de las decisiones arquitectónicas.

**Software a comparar (sugerido en orden de relevancia):**
- R: `terra::approxNA`, `raster::approxNA` (solo lineal, sin mean-preservation)
- Python: `xarray.interp` (genérico, sin política de variables)
- CDO: `cdo inttime` (sin garantía de conservación de media)
- Python: `xclim` (Ouranos) — sí hace temporal interpolation con varias opciones
- R: `Climate4R` — suite climatológica con downscaling y bias correction
- `ESMValTool` — preprocesador de modelos climáticos

**No incluido en este snapshot:** documentación externa de esos paquetes (el redactor debe consultarla directamente).

---

### §9 — Reproducibilidad y procedencia

**Lee primero:**
- `code/pipeline/report.py` — dataclass `ProcessingReport` con todos los campos de procedencia + `ReportGenerator.to_markdown()` / `.to_json()`.
- `code/pipeline/config.py` — `PipelineConfig` frozen dataclass con todos los parámetros (incluido `seed`, `reproducibility_mode`).
- `code/pipeline/core.py` — `TempifyPipeline.run()` orquestador de las 7 fases.
- `adr/0007-reproducibility-policy.md` — política bit-exact strict vs parallel.
- `adr/0014-tempifypipeline-naming-correction.md` — naming PascalCase.
- `code/api.py` — capa ergonómica v0.1.6 (`rast`, `tempify`, `plot`); interopera con `xr.DataArray` nativo.
- `project_meta/CITATION.cff` — formato de cita; DOI versionado por release.
- `project_meta/CHANGELOG.md` — semver y historial de releases.

---

## Notas para el redactor

1. **Idioma:** español chileno/latam neutro. NO voseo rioplatense (NO "citá", "elegís", "podés"; SÍ "cita", "eliges", "puedes"). Ver PR #64.
2. **Convención §:** notación académica `§N` para "sección N". Si se prefiere prosa, usar "sección N".
3. **Sin em-dashes (—) opcional:** el repo los usa libremente. Si la redacción es para paper, considerar reemplazar por comas/paréntesis.
4. **Snapshot SHA:** `0715cfde878d7927f4a05923d14ee64e5affecfb` (main post-PR #67). Si el repo avanza, refrescar este directorio con un nuevo `git checkout <archivo>` desde main.
5. **Para refrescar este directorio:** `git restore --source=main _methodology_sources/code/...` (o reemplazar archivo por archivo).
6. **Permanencia:** este directorio es **temporal**. Una vez publicada la metodología, se sugiere eliminar `_methodology_sources/` en un commit aparte.

---

## Inventario rápido

- **9 ADRs** (los más relevantes para metodología, de los 16 totales del repo)
- **18 archivos de código** (interpoladores, kernels, pipeline, validation, profiles)
- **6 specs SDD** (requirements + design de las 3 capas más críticas)
- **5 scripts ejecutables** (bench + demo + regeneradores de figuras)
- **5 archivos de project meta** (README, CHANGELOG, CITATION, REFERENCES, precipitation.md)
- **2 archivos de steering** (tech, architecture)

**Total: 48 archivos, ~700 KB.**
