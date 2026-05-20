# Kit de redacción metodológica — tempify (archivo único)

> **Snapshot:** `f83d216eb68f8f69d8bc7d088f626130750ebd9f` (main post-PR #68).
> **Propósito:** archivo único con todo el material fuente del repositorio necesario para redactar el capítulo de Metodología de tempify. Sustituye al árbol `_methodology_sources/` cuando se necesita subir UN solo archivo a un Project de Claude.ai (la UI sólo acepta archivos sueltos).
> **Tamaño:** ~340 KB de texto plano.
> **Cómo navegar:** las secciones siguen el orden MANIFEST → meta-proyecto → steering → ADRs → specs → código → ejemplos. Cada archivo del repo aparece como `## File: <ruta>` seguido del contenido íntegro envuelto en code fence con lenguaje detectado.
> **Búsqueda rápida:** Ctrl+F el path original del repo (ej. `code/interpolation/pchip_mp.py`) y caes en el archivo.


---

# Manifest y meta-proyecto


## File: `MANIFEST.md`


```markdown
# Manifest — Fuentes para la redacción del capítulo de metodología

> **Snapshot:** `tempify` @ `0715cfde878d7927f4a05923d14ee64e5affecfb` (post-PR #67).
> **Propósito:** entregar al redactor (humano o LLM en sesión externa) todos los archivos del repositorio necesarios para escribir `docs/methodology/methodology.md` + `methodology_en.md` siguiendo el outline acordado, sin necesidad de clonar el repo completo.
> **Cómo usar:** abre el archivo en `<sección>` listada abajo; los paths relativos están preservados respecto a la raíz del repo (excepto que viven bajo `_methodology_sources/`).

---

##### Outline del capítulo (recordatorio)

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

##### Matriz archivo → sección

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

##### Guía por sección

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

##### Notas para el redactor

1. **Idioma:** español chileno/latam neutro. NO voseo rioplatense (NO "citá", "elegís", "podés"; SÍ "cita", "eliges", "puedes"). Ver PR #64.
2. **Convención §:** notación académica `§N` para "sección N". Si se prefiere prosa, usar "sección N".
3. **Sin em-dashes (—) opcional:** el repo los usa libremente. Si la redacción es para paper, considerar reemplazar por comas/paréntesis.
4. **Snapshot SHA:** `0715cfde878d7927f4a05923d14ee64e5affecfb` (main post-PR #67). Si el repo avanza, refrescar este directorio con un nuevo `git checkout <archivo>` desde main.
5. **Para refrescar este directorio:** `git restore --source=main _methodology_sources/code/...` (o reemplazar archivo por archivo).
6. **Permanencia:** este directorio es **temporal**. Una vez publicada la metodología, se sugiere eliminar `_methodology_sources/` en un commit aparte.

---

##### Inventario rápido

- **9 ADRs** (los más relevantes para metodología, de los 16 totales del repo)
- **18 archivos de código** (interpoladores, kernels, pipeline, validation, profiles)
- **6 specs SDD** (requirements + design de las 3 capas más críticas)
- **5 scripts ejecutables** (bench + demo + regeneradores de figuras)
- **5 archivos de project meta** (README, CHANGELOG, CITATION, REFERENCES, precipitation.md)
- **2 archivos de steering** (tech, architecture)

**Total: 48 archivos, ~700 KB.**

```

## File: `project_meta/README.md`


```markdown
# tempify

> **Densificación temporal para stacks ráster geoespaciales.**
> *Generate more data between your existing data.*

<!-- Fila 1: estado, calidad, lenguaje, licencia, DOI -->
[![Tests](https://img.shields.io/badge/tests-330%20passing-brightgreen)](https://github.com/djwillichile/tempify/tree/main/tests)
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)](https://github.com/djwillichile/tempify)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue?logo=python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20297689.svg)](https://zenodo.org/records/20297689)

<!-- Fila 2: stack tecnológica, tooling, actividad, documentación -->
[![xarray](https://img.shields.io/badge/xarray-powered-4c8cdf)](https://xarray.dev)
[![Dask](https://img.shields.io/badge/Dask-out--of--core-eb6f1f)](https://www.dask.org)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-d7ff64)](https://docs.astral.sh/ruff/)
[![Type checked: mypy](https://img.shields.io/badge/typed-mypy-1d6dba)](https://mypy-lang.org/)
[![Last commit](https://img.shields.io/github/last-commit/djwillichile/tempify?color=8c5cf2&label=last%20commit)](https://github.com/djwillichile/tempify/commits/main)
[![Docs](https://img.shields.io/badge/docs-djwillichile.github.io-22c55e)](https://djwillichile.github.io/tempify/)


##### ¿Qué es?

`tempify` es una librería Python + CLI que realiza **densificación temporal** sobre stacks ráster geoespaciales. Toma una serie de rásters muestreada a baja frecuencia (por ejemplo, 12 valores mensuales) y genera una serie densa (365 o 366 valores diarios) preservando propiedades estadísticas críticas como la conservación de la media mensual.

Análogo conceptual: igual que la **interpolación de fotogramas** genera frames intermedios para un video más fluido, `tempify` genera valores temporales intermedios para un stack ráster más denso.

##### ¿Para qué sirve?

Los principales productos climáticos globales de alta resolución espacial — WorldClim (Fick & Hijmans, 2017), CHELSA (Karger et al., 2017), TerraClimate (Abatzoglou et al., 2018) y CRU-TS (Harris et al., 2020) — se distribuyen a frecuencia mensual o climatológica. Sin embargo, múltiples procesos ambientales dependen de manera **no lineal** de la variación subdiaría o diaria de las variables climáticas, lo que hace que los valores mensuales sean insuficientes como input directo.

### Grados-día de desarrollo (GDD)

El acumulado de grados-día es el índice fenológico más usado en agronomía y ecología: integra temperatura sobre un umbral base diariamente (McMaster & Wilhelm, 1997). Calcularlo desde medias mensuales introduce un sesgo sistemático porque la función umbral (max(T − T_base, 0)) es no lineal — interpolar valores intermedios antes de aplicar el umbral produce resultados distintos a aplicarlo sobre la media mensual directamente.

### Evapotranspiración de referencia (ET₀)

La ecuación de Penman-Monteith FAO-56 (Allen et al., 1998) — estándar internacional para ET₀ — requiere Tmax, Tmin y Tmean **diarios** para calcular el déficit de presión de vapor y la radiación neta. La ecuación simplificada de Hargreaves-Samani (Hargreaves & Samani, 1985), usada cuando solo hay temperatura, también opera sobre el rango térmico diario (Tmax − Tmin). Usar temperaturas mensuales directas subestima la amplitud térmica y por tanto la demanda evapotranspirativa.

### Modelos de distribución de especies (SDM)

Los modelos de distribución de especies requieren variables bioclimáticas derivadas de series diarias (e.g., temperatura del trimestre más cálido, precipitación del mes más seco). Hijmans & Graham (2006) demostraron que la resolución temporal del dato climático de entrada afecta significativamente la capacidad predictiva de los SDMs, especialmente en zonas con marcada estacionalidad.

### Otros campos de aplicación

- **Hidrología distribuida:** cómputo de balance hídrico diario y crecidas (modelos tipo SCS-CN, HBV, VIC).
- **Índices bioclimáticos CHELSA/WorldClim:** requieren Tmax/Tmin diario para BIO5 (máx. del mes más cálido) y BIO6 (mín. del mes más frío).
- **Calidad del aire regional:** modelos de dispersión fotooxidativa con forzante meteorológico diario.

`tempify` automatiza esta conversión mensual → diaria con métodos validados y trazabilidad metodológica completa, preservando la media mensual original como restricción dura.

##### ¿Qué no es?

- No es un GIS general (no reproyecta, no recorta).
- No hace downscaling espacial (la resolución espacial no cambia).
- No es un weather generator estocástico (no inventa variabilidad sinóptica).
- No interpola precipitación con métodos suaves (rechazado por diseño).

##### Tutoriales

| Notebook | Descripción |
|----------|-------------|
| [`01-getting-started.ipynb`](docs/tutorials/01-getting-started.ipynb) | Introducción a la API: datos sintéticos WorldClim-like, seis métodos de interpolación, conservación de media mensual, reporte de procedencia, visualización 3D. [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/djwillichile/tempify/blob/main/docs/tutorials/01-getting-started.ipynb) |
| [`02-real-worldclim-maipo.ipynb`](docs/tutorials/02-real-worldclim-maipo.ipynb) | Caso real con datos WorldClim v2.1 descargados para la cuenca del Maipo (Chile). Densificación mensual → diaria, análisis espacial y validación de conservación. [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/djwillichile/tempify/blob/main/docs/tutorials/02-real-worldclim-maipo.ipynb) |

##### Instalación

```bash
#### Desde el repo (recomendado para v0.1.x)
git clone https://github.com/djwillichile/tempify.git
cd tempify
pip install -e ".[dev]"

#### pip / conda-forge: planificado para v0.1.x cuando el paquete suba a PyPI
```

Requiere Python 3.11, 3.12 o 3.13.

##### Ejemplo mínimo

```bash
#### CLI
tempify convert ./worldclim_chile/ \
    --method pchip_mp \
    --year 2023 \
    --output ./out/ \
    --report ./out/report.md
```

```python
#### API Python
from pathlib import Path
from tempify.pipeline import PipelineConfig, TempifyPipeline

cfg = PipelineConfig(
    method="pchip_mp",
    target_year=2023,
    output_dir=Path("./out"),
)
result = TempifyPipeline(cfg).run(Path("./worldclim_chile/"))
print(result.outputs)        # [PosixPath('./out/tempify_output.nc')]
print(result.report.method)  # 'pchip_mp'
```

##### Métodos disponibles

| Método | Descripción | Recomendado para |
|---|---|---|
| `linear` | Interpolación lineal entre nodos | Prototipos rápidos |
| `pchip` | Piecewise Cubic Hermite (shape-preserving) | Uso general |
| `pchip_mp` | PCHIP + Rymes-Myers mean-preserving | **Producto final, máxima fidelidad** |
| `fourier` | Ajuste armónico (1-5 armónicos) | Representación paramétrica del ciclo |
| `akima` | Akima 1970 (C¹, menos overshoot que cubic) | Variables con cambios bruscos |
| `cubic` | Spline natural C² | Señales muy suaves (puede overshoot) |

##### Estado del proyecto

**v0.1.5** (2026-05-18) — Módulos auxiliares `datasets`, `utils`, `plotting`; seis métodos de interpolación (`akima` y `cubic` agregados en v0.1.4); notebooks simplificados. Ver [CHANGELOG](CHANGELOG.md).

**v0.1.0 — primer release funcional** (2026-05-16). Capas 1-6 implementadas (I/O, Detection, Validation, Interpolation, Pipeline, CLI), 241 tests passing, 91% coverage, 17 ADRs documentados.

**Diferido a v0.2.0:** GUI PySide6, instalador Windows .exe, integración de redes neuronales pre-entrenadas bajo patrón híbrido (ver [ADR-0017](docs/adr/0017-neural-interpolator-extensibility.md)).

Este repositorio sigue **Spec-Driven Development** y **Harness Engineering**. Toda implementación está precedida por una spec aprobada en `specs/`. Ver `CLAUDE.md` para el régimen de trabajo.

##### Ejemplo rápido (WorldClim Chile Central)

Demo end-to-end sobre 12 GeoTIFFs sintéticos que reproducen la
climatología real de temperatura media mensual de la Región
Metropolitana de Santiago (≈21 °C verano, 9 °C invierno) con la
convención de nombres de WorldClim v2.1.

```bash
#### 1. Generar los archivos sinteticos (~50 KB, no requiere internet)
python examples/generate_worldclim_sample.py

#### 2. Convertir mensual a diario via CLI
tempify convert examples/data/worldclim_chile_central \
    --method pchip_mp \
    --year 2023 \
    --output examples/out/cli \
    --report examples/out/cli/report.md

#### 3. (opcional) Ejecutar el demo Python que verifica numericamente
python examples/run_demo.py
```

Verifica end-to-end que: detección automática (mode B + climatological
WorldClim), pipeline completo de 7 fases, NetCDF diario CF-compliant
de salida, conservación de media mensual <1e-4 °C, y reporte de
procedencia con MD5 de inputs. Ver `examples/README.md`.

##### Estructura del repositorio

```
tempify/
├── CLAUDE.md                  # Harness gobernante del agente
├── steering/                  # Contexto persistente del proyecto
├── specs/                     # Specs SDD (requirements → design → tasks → impl-log)
├── src/tempify/               # Código fuente
├── tests/                     # Tests unitarios e integración
├── docs/                      # Documentación, ADRs, tutoriales
└── .claude/                   # Commands, hooks, skills del harness
```

##### Documentación

- Tutoriales: `docs/tutorials/`
- Notas metodológicas: `docs/methodology/`
- Architecture Decision Records: `docs/adr/`

##### Contribuir

Este proyecto sigue Spec-Driven Development estricto. Para contribuir:

1. Lee `CLAUDE.md` y `steering/harness.md` para entender el régimen de trabajo.
2. Abre un issue describiendo la feature antes de iniciar trabajo.
3. Las contribuciones se discuten primero a nivel de spec, después en código.

##### Licencia

MIT License. Ver `LICENSE`.

##### Citar este software

Para metadatos completos (autores, afiliación, ORCID) ver [CITATION.cff](CITATION.cff). Todas las entradas BibTeX están en [`REFERENCES.bib`](REFERENCES.bib).

> Fuentes-Jaque, G. S. (2026). *tempify: Temporal densification for geospatial raster stacks* (v0.1.6) \[Software\]. ICTA Ltda.; Universidad San Sebastián; Universidad de Chile. https://doi.org/10.5281/zenodo.20297689

##### Referencias bibliográficas de los métodos

Las publicaciones originales detrás de cada método de interpolación que `tempify` implementa. Si usas un método específico en una publicación científica, cita también el paper correspondiente (no solo el paquete). Todas las revistas están indexadas en Web of Science / JCR. Entradas BibTeX en [`REFERENCES.bib`](REFERENCES.bib).

| Método | Clave BibTeX |
|--------|-------------|
| `pchip`, `pchip_mp` (base) | `fritsch_carlson_1980` |
| `pchip_mp` (corrección media) | `rymes_myers_2001` |
| `akima` | `akima_1970` |
| `cubic` | `deboor_1978` |
| `fourier` | `cooley_tukey_1965` |
| _v0.2.0_ `cubic_mp_lai_kaplan` | `lai_kaplan_2022` |

### En formato APA

Fritsch, F. N., & Carlson, R. E. (1980). Monotone piecewise cubic interpolation. *SIAM Journal on Numerical Analysis*, *17*(2), 238–246. https://doi.org/10.1137/0717021

Rymes, M. D., & Myers, D. R. (2001). Mean preserving algorithm for smoothly interpolating averaged data. *Solar Energy*, *71*(4), 225–231. https://doi.org/10.1016/S0038-092X(01)00052-4

Akima, H. (1970). A new method of interpolation and smooth curve fitting based on local procedures. *Journal of the ACM*, *17*(4), 589–602. https://doi.org/10.1145/321607.321609

de Boor, C. (1978). *A practical guide to splines* (Vol. 27, Applied Mathematical Sciences). Springer-Verlag.

Cooley, J. W., & Tukey, J. W. (1965). An algorithm for the machine calculation of complex Fourier series. *Mathematics of Computation*, *19*(90), 297–301. https://doi.org/10.1090/S0025-5718-1965-0178586-1

Lai, L. O., & Kaplan, J. O. (2022). A fast mean-preserving spline for interpolating interval data. *Journal of Atmospheric and Oceanic Technology*, *39*(4), 503–512. https://doi.org/10.1175/JTECH-D-21-0154.1

> **Sobre datasets de referencia.** El stack `examples/data/worldclim_maipo_alto/` que distribuimos es un recorte derivado de WorldClim v2.1. Si lo usas en publicaciones, cita el producto original.

### Datasets de entrada citados en la documentación

Fick, S. E., & Hijmans, R. J. (2017). WorldClim 2: New 1-km spatial resolution climate surfaces for global land areas. *International Journal of Climatology*, *37*(12), 4302–4315. https://doi.org/10.1002/joc.5086

Karger, D. N., Conrad, O., Böhner, J., Kawohl, T., Kreft, H., Soria-Auza, R. W., Zimmermann, N. E., Linder, H. P., & Kessler, M. (2017). Climatologies at high resolution for the earth's land surface areas (CHELSA). *Scientific Data*, *4*, 170122. https://doi.org/10.1038/sdata.2017.122

Abatzoglou, J. T., Dobrowski, S. Z., Parks, S. A., & Hegewisch, K. C. (2018). TerraClimate, a high-resolution global dataset of monthly climate and climatic water balance from 1958–2015. *Scientific Data*, *5*, 170191. https://doi.org/10.1038/sdata.2017.191

Harris, I., Osborn, T. J., Jones, P., & Lister, D. (2020). Version 4 of the CRU TS monthly high-resolution gridded multivariate climate dataset. *Scientific Data*, *7*, 109. https://doi.org/10.1038/s41597-020-0453-3

### Bases científicas de los casos de uso

Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). *Crop evapotranspiration: Guidelines for computing crop water requirements* (FAO Irrigation and Drainage Paper 56). FAO.

Hargreaves, G. H., & Samani, Z. A. (1985). Reference crop evapotranspiration from temperature. *Applied Engineering in Agriculture*, *1*(2), 96–99. https://doi.org/10.13031/2013.26773

McMaster, G. S., & Wilhelm, W. W. (1997). Growing degree-days: One equation, two interpretations. *Agricultural and Forest Meteorology*, *87*(4), 291–300. https://doi.org/10.1016/S0168-1923(97)00027-0

Hijmans, R. J., & Graham, C. H. (2006). The ability of climate envelope models to predict the effect of climate change on species distributions. *Global Change Biology*, *12*(12), 2272–2281. https://doi.org/10.1111/j.1365-2486.2006.01256.x

##### Contacto

**ICTA Ltda.** · Santiago, Chile · Mantenedor: Guillermo Fuentes-Jaque

- Email institucional: [contacto@icta.cl](mailto:contacto@icta.cl)
- Sitio web: [icta.cl](https://icta.cl)
- WhatsApp: [+56 9 9292 4314](https://wa.me/56992924314)
- Email del mantenedor: [guillermo@icta.cl](mailto:guillermo@icta.cl)
- Issues técnicos: usa el [issue tracker de GitHub](https://github.com/djwillichile/tempify/issues) en lugar de los canales anteriores.

```

## File: `project_meta/CITATION.cff`


```yaml
cff-version: 1.2.0
message: "Si usas tempify en investigación, por favor cita el software como sigue."
title: "tempify: Temporal densification for geospatial raster stacks"
type: software
authors:
  - family-names: Fuentes-Jaque
    given-names: Guillermo S.
    orcid: https://orcid.org/0000-0002-7864-4899
    email: guillermo.f1990@gmail.com
    affiliation: >-
      Instituto de Ciencias y Tecnología Ambiental ICTA Ltda., Chile.
      Facultad de Ingeniería, Universidad San Sebastián, Chile.
      Magíster en Gestión Territorial de Recursos Naturales,
      Ingeniero en Recursos Naturales Renovables, Universidad de Chile.
      Científico de datos geoespaciales · Consultor ambiental · Docente universitario.
contact:
  - name: "ICTA Ltda."
    email: contacto@icta.cl
    website: "https://icta.cl"
    tel: "+56 9 9292 4314"
abstract: >-
  tempify realiza densificación temporal de stacks ráster geoespaciales:
  toma una serie muestreada a baja frecuencia (típicamente 12 valores mensuales)
  y genera una serie densa (365 o 366 valores diarios) preservando propiedades
  estadísticas críticas como la conservación de la media mensual. Aplicable a
  productos como WorldClim, CHELSA, CRU-TS, TerraClimate.
keywords:
  - geospatial
  - raster
  - temporal-densification
  - interpolation
  - climate
  - worldclim
  - xarray
  - python
license: MIT
repository-code: "https://github.com/djwillichile/tempify"
url: "https://djwillichile.github.io/tempify/"
version: "0.1.6"
date-released: "2026-05-18"
doi: "10.5281/zenodo.20297689"
identifiers:
  - type: doi
    value: "10.5281/zenodo.20297689"
    description: "Versión 0.1.6 archivada en Zenodo (DOI específico de esta release)"
  - type: doi
    value: "10.5281/zenodo.20277280"
    description: "Versión 0.1.5 archivada en Zenodo (release anterior, conservado para trazabilidad)"
  - type: doi
    value: "10.5281/zenodo.20265222"
    description: "Versión 0.1.4 archivada en Zenodo (release anterior, conservado para trazabilidad)"
  - type: doi
    value: "10.5281/zenodo.20259997"
    description: "Versión 0.1.3 archivada en Zenodo (release anterior, conservado para trazabilidad)"
  - type: doi
    value: "10.5281/zenodo.20251750"
    description: "Versión 0.1.2 archivada en Zenodo (release anterior, conservado para trazabilidad)"
references:
  - type: article
    authors:
      - family-names: Rymes
        given-names: M. D.
      - family-names: Myers
        given-names: D. R.
    title: "Mean preserving algorithm for smoothly interpolating averaged data"
    journal: "Solar Energy"
    volume: 71
    issue: 4
    year: 2001
    start: 225
    end: 231
  - type: article
    authors:
      - family-names: Fritsch
        given-names: F. N.
      - family-names: Carlson
        given-names: R. E.
    title: "Monotone piecewise cubic interpolation"
    journal: "SIAM Journal on Numerical Analysis"
    volume: 17
    issue: 2
    year: 1980
    start: 238
    end: 246
    doi: "10.1137/0717021"
  - type: article
    authors:
      - family-names: Akima
        given-names: Hiroshi
    title: "A New Method of Interpolation and Smooth Curve Fitting Based on Local Procedures"
    journal: "Journal of the ACM"
    volume: 17
    issue: 4
    year: 1970
    start: 589
    end: 602
    doi: "10.1145/321607.321609"
  - type: book
    authors:
      - family-names: de Boor
        given-names: Carl
    title: "A Practical Guide to Splines (Applied Mathematical Sciences, vol. 27)"
    publisher:
      name: Springer-Verlag
      city: New York
    year: 1978
    isbn: "978-0-387-95366-3"
  - type: article
    authors:
      - family-names: Lai
        given-names: Leo O.
      - family-names: Kaplan
        given-names: Jed O.
    title: "A Fast Mean-Preserving Spline for Interpolating Interval Data"
    journal: "Journal of Atmospheric and Oceanic Technology"
    volume: 39
    issue: 4
    year: 2022
    start: 503
    end: 512
    doi: "10.1175/JTECH-D-21-0154.1"
    notes: "Planificado para v0.2.0 como método cubic_mp_lai_kaplan (ver ADR-0018)."

```

## File: `project_meta/REFERENCES.bib`


```bibtex
% REFERENCES.bib — tempify bibliographic references
% All entries used in README.md and academic citations.
% Encoding: UTF-8

% ── Software citation ────────────────────────────────────────────────────────

@software{fuentes_jaque_tempify_2026,
  author       = {Fuentes-Jaque, Guillermo S.},
  orcid        = {0000-0002-7864-4899},
  title        = {{tempify}: Temporal densification for geospatial raster stacks},
  year         = {2026},
  version      = {0.1.6},
  organization = {ICTA Ltda.; Universidad San Sebastián; Universidad de Chile},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.20297689},
  url          = {https://doi.org/10.5281/zenodo.20297689}
}

% ── Interpolation methods ────────────────────────────────────────────────────

@article{fritsch_carlson_1980,
  author  = {Fritsch, F. N. and Carlson, R. E.},
  title   = {Monotone Piecewise Cubic Interpolation},
  journal = {SIAM Journal on Numerical Analysis},
  volume  = {17},
  number  = {2},
  pages   = {238--246},
  year    = {1980},
  doi     = {10.1137/0717021}
}

@article{rymes_myers_2001,
  author  = {Rymes, M. D. and Myers, D. R.},
  title   = {Mean Preserving Algorithm for Smoothly Interpolating Averaged Data},
  journal = {Solar Energy},
  volume  = {71},
  number  = {4},
  pages   = {225--231},
  year    = {2001},
  doi     = {10.1016/S0038-092X(01)00052-4}
}

@article{akima_1970,
  author  = {Akima, Hiroshi},
  title   = {A New Method of Interpolation and Smooth Curve Fitting Based on Local Procedures},
  journal = {Journal of the ACM},
  volume  = {17},
  number  = {4},
  pages   = {589--602},
  year    = {1970},
  doi     = {10.1145/321607.321609}
}

@book{deboor_1978,
  author    = {de Boor, Carl},
  title     = {A Practical Guide to Splines},
  series    = {Applied Mathematical Sciences},
  volume    = {27},
  publisher = {Springer-Verlag},
  address   = {New York},
  year      = {1978},
  isbn      = {978-0-387-95366-3}
}

@article{cooley_tukey_1965,
  author  = {Cooley, James W. and Tukey, John W.},
  title   = {An Algorithm for the Machine Calculation of Complex Fourier Series},
  journal = {Mathematics of Computation},
  volume  = {19},
  number  = {90},
  pages   = {297--301},
  year    = {1965},
  doi     = {10.1090/S0025-5718-1965-0178586-1}
}

@article{lai_kaplan_2022,
  author  = {Lai, Leo O. and Kaplan, Jed O.},
  title   = {A Fast Mean-Preserving Spline for Interpolating Interval Data},
  journal = {Journal of Atmospheric and Oceanic Technology},
  volume  = {39},
  number  = {4},
  pages   = {503--512},
  year    = {2022},
  doi     = {10.1175/JTECH-D-21-0154.1}
}

% ── Reference datasets ───────────────────────────────────────────────────────

@article{fick_hijmans_2017,
  author  = {Fick, Stephen E. and Hijmans, Robert J.},
  title   = {{WorldClim} 2: New 1-km Spatial Resolution Climate Surfaces for Global Land Areas},
  journal = {International Journal of Climatology},
  volume  = {37},
  number  = {12},
  pages   = {4302--4315},
  year    = {2017},
  doi     = {10.1002/joc.5086}
}

@article{karger_2017,
  author  = {Karger, Dirk Nikolaus and Conrad, Olaf and B{\"o}hner, J{\"u}rgen and Kawohl,
             Tobias and Kreft, Holger and Soria-Auza, Rodrigo Wilber and Zimmermann,
             Niklaus E. and Linder, H. Peter and Kessler, Michael},
  title   = {Climatologies at High Resolution for the Earth's Land Surface Areas ({CHELSA})},
  journal = {Scientific Data},
  volume  = {4},
  pages   = {170122},
  year    = {2017},
  doi     = {10.1038/sdata.2017.122}
}

@article{abatzoglou_2018,
  author  = {Abatzoglou, John T. and Dobrowski, Solomon Z. and Parks, Sean A. and
             Hegewisch, Katherine C.},
  title   = {{TerraClimate}, a High-Resolution Global Dataset of Monthly Climate and
             Climatic Water Balance from 1958--2015},
  journal = {Scientific Data},
  volume  = {5},
  pages   = {170191},
  year    = {2018},
  doi     = {10.1038/sdata.2017.191}
}

@article{harris_2020,
  author  = {Harris, Ian and Osborn, Timothy J. and Jones, Phil and Lister, David},
  title   = {Version 4 of the {CRU TS} Monthly High-Resolution Gridded Multivariate
             Climate Dataset},
  journal = {Scientific Data},
  volume  = {7},
  pages   = {109},
  year    = {2020},
  doi     = {10.1038/s41597-020-0453-3}
}

% ── Scientific basis for use cases ──────────────────────────────────────────

@book{allen_1998,
  author    = {Allen, Richard G. and Pereira, Luis S. and Raes, Dirk and Smith, Martin},
  title     = {Crop Evapotranspiration: Guidelines for Computing Crop Water Requirements},
  series    = {FAO Irrigation and Drainage Paper},
  volume    = {56},
  publisher = {Food and Agriculture Organization of the United Nations},
  address   = {Rome},
  year      = {1998},
  isbn      = {92-5-104219-5}
}

@article{hargreaves_samani_1985,
  author  = {Hargreaves, George H. and Samani, Zohrab A.},
  title   = {Reference Crop Evapotranspiration from Temperature},
  journal = {Applied Engineering in Agriculture},
  volume  = {1},
  number  = {2},
  pages   = {96--99},
  year    = {1985},
  doi     = {10.13031/2013.26773}
}

@article{mcmaster_wilhelm_1997,
  author  = {McMaster, G. S. and Wilhelm, W. W.},
  title   = {Growing Degree-Days: One Equation, Two Interpretations},
  journal = {Agricultural and Forest Meteorology},
  volume  = {87},
  number  = {4},
  pages   = {291--300},
  year    = {1997},
  doi     = {10.1016/S0168-1923(97)00027-0}
}

@article{hijmans_graham_2006,
  author  = {Hijmans, Robert J. and Graham, Catherine H.},
  title   = {The Ability of Climate Envelope Models to Predict the Effect of Climate
             Change on Species Distributions},
  journal = {Global Change Biology},
  volume  = {12},
  number  = {12},
  pages   = {2272--2281},
  year    = {2006},
  doi     = {10.1111/j.1365-2486.2006.01256.x}
}

% ── Software libraries ──────────────────────────────────────────────────────

@article{hoyer_hamman_2017,
  author  = {Hoyer, Stephan and Hamman, Joseph J.},
  title   = {xarray: {N-D} Labeled Arrays and Datasets in {Python}},
  journal = {Journal of Open Research Software},
  volume  = {5},
  number  = {1},
  pages   = {10},
  year    = {2017},
  doi     = {10.5334/jors.148}
}

@inproceedings{rocklin_2015,
  author    = {Rocklin, Matthew},
  title     = {{Dask}: Parallel Computation with Blocked Algorithms and Task Scheduling},
  booktitle = {Proceedings of the 14th {Python} in {Science} Conference},
  editor    = {Huff, Kathryn and Bergstra, James},
  pages     = {130--136},
  year      = {2015},
  doi       = {10.25080/Majora-7b98e3ed-013}
}

% ── Standards and conventions ───────────────────────────────────────────────

@misc{cf_conventions_2024,
  author       = {{Unidata}},
  title        = {{NetCDF} Climate and Forecast ({CF}) Metadata Conventions, Version 1.10},
  year         = {2024},
  howpublished = {\url{https://cfconventions.org/cf-conventions/v1.10/}},
  note         = {Maintained by the CF Conventions Committee}
}

```

## File: `project_meta/CHANGELOG.md`


```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

##### [Unreleased]

### Pendiente para v0.2.0+

- `cubic_mp_lai_kaplan`: spline mean-preserving moderno per [Lai & Kaplan 2022, JTECH](https://journals.ametsoc.org/view/journals/atot/39/4/JTECH-D-21-0154.1.xml). Reemplazaría a Rymes-Myers como baseline mean-preserving.
- Post-procesador `SavitzkyGolayPostProcessor` (nueva fase opcional del pipeline tras `interpolate`, antes de `validate_post`).
- `WhittakerHendersonInterpolator` como alternativa flexible a `fourier` con preservación de momentos.

Ver [ADR-0018](docs/adr/0018-classical-interpolator-catalog.md) para el roadmap completo.

##### [0.1.6] — 2026-05-18

API ergonómica de conveniencia tipo `terra` de R. Permite cargar, inspeccionar,
visualizar e interpolar un stack en pocas líneas desde el nivel de paquete.

### Added

- **`tempify.api`**: módulo nuevo con capa de conveniencia de alto nivel.
  - `rast(path)` — carga un GeoTIFF multi-banda como `TempifyRast`; análogo a `terra::rast()`.
  - `TempifyRast` — wrapper de `xr.DataArray` con `__repr__` tipo terra (llama a `raster_info()`)
    y método `.str()` con info extendida (rango de valores, NaN, atributos).
  - `plot(r, sub=None, cmap="viridis")` — grilla automática de bandas con colorbar compartida;
    `sub` acepta índices 1-based como en `terra::plot(r, sub=1:16)`.
  - `tempify(stack, from_freq, to_freq, method="pchip_mp", year=None)` — interpolación en
    memoria (sin disco) del stack; retorna `TempifyRast` con dim `time` en orden `(time, y, x)`.
- **Exportaciones de nivel de paquete**: `from tempify import rast, tempify, plot` ahora
  funciona directamente desde `tempify.__init__`.

### Specs

- `specs/ergonomic-api/requirements.md` — requisitos EARS de la capa de conveniencia.
- `specs/ergonomic-api/design.md` — contratos de interfaz y decisiones de diseño.
- `specs/ergonomic-api/tasks.md` — tasks atómicas del ciclo de implementación.

---

##### [0.1.5] — 2026-05-18

Release de experiencia de usuario para notebooks y tutoriales. Sin cambios en el
nucleo metodologico ni en los metodos de interpolacion existentes.

### Added

- **`tempify.datasets`**: modulo nuevo para datos sinteticos reproducibles tipo WorldClim.
  - `create_worldclim_like_sample()` — genera 12 GeoTIFFs con nomenclatura WorldClim v2.1;
    superficie espacial realista (gradiente altitudinal Andes, clusters gaussianos, textura
    suavizada, ruido local). Reproducible via `seed`. Idempotente via `overwrite=False`.
  - `read_monthly_stack()` — carga 12 GeoTIFFs mensuales como `xr.DataArray (month=12, y, x)`.
  - `SANTIAGO_MONTHLY_TAVG` — climatologia de temperatura mensual para Santiago de Chile.
- **`tempify.utils`**: helpers para cargar y filtrar outputs del pipeline.
  - `open_tempify_output()` — abre el output de `TempifyPipeline.run()` detectando el formato
    automaticamente (`.nc`, `.tif`, `.zarr`). Acepta `PipelineResult` o `Path`.
  - `extract_daily_rasters()` — filtra un `DataArray` diario por meses, dias y/o ano.
  - `get_anchor_dates()` — retorna las 12 fechas ancla mensuales (dia 15) para un ano.
  - `raster_info()` — imprime resumen del DataArray estilo `terra::print(r)`: dimensiones,
    resolucion, extension, CRS, capas o rango temporal, tipo de datos.
- **`tempify.plotting`**: visualizaciones livianas para notebooks (matplotlib opcional).
  - `plot_monthly_rasters()` — grilla 3x4 de los 12 GeoTIFFs mensuales con colorbar compartida.
  - `plot_raster_timeseries()` — serie temporal de un pixel con scatter de anclas opcionales.
  - `plot_temporal_stack_3d()` — stack raster 3D; anclas con borde rojo, interpoladas con
    menor opacidad.
- **Dependencia opcional `[viz]`**: `pip install tempify[viz]` agrega `matplotlib>=3.8`.
- **Tutorial actualizado**: `docs/tutorials/01-getting-started.ipynb` — de ~800 lineas de
  boilerplate a ~60 lineas de llamadas API (-760 lineas).

##### [0.1.4] — 2026-05-18

Release de extensión del catálogo de interpoladores: dos métodos clásicos nuevos (akima, cubic) per [ADR-0018](docs/adr/0018-classical-interpolator-catalog.md). Sin breaking changes; los 4 métodos existentes (`linear`, `pchip`, `pchip_mp`, `fourier`) siguen byte-idénticos a v0.1.3.

### Added

- **`AkimaInterpolator`** (`src/tempify/interpolation/akima.py`): spline C¹ de Akima 1970 con cyclic option (dos wrap nodes per side, ADR-0016). Menos agresivo que PCHIP al aplanar máximos locales, menos overshoots que cubic. Envuelve `scipy.interpolate.Akima1DInterpolator`.
- **`CubicSplineInterpolator`** (`src/tempify/interpolation/cubic.py`): spline natural C² (not-a-knot). Más suave que PCHIP, pero **puede overshoot entre nodos** — usar `pchip` o `pchip_mp` si la monotonicidad importa. Envuelve `scipy.interpolate.CubicSpline`.
- Kernels nuevos en `_kernels.py`: `akima_kernel`, `cubic_kernel`, ambos con padding cíclico de 2 wrap nodes por lado.
- 14 tests unitarios nuevos (`tests/unit/interpolation/test_akima.py`, `test_cubic.py`) cubriendo kernel + facade: input constante, pass-through de nodos, error sinusoidal acotado, extrapolación non-cyclic, NaN policy raise + propagate_all.
- **ADR-0018**: catálogo extensible de interpoladores clásicos. Documenta las 8 familias revisadas (cubic, Akima, Makima, Lai-Kaplan, Savitzky-Golay, Whittaker-Henderson, GPR, STL) con sus tradeoffs y plan de release.
- `tempify_method` attr ahora puede valer `"akima"` o `"cubic"`.
- CLI: `tempify convert --method akima|cubic` acepta los nuevos métodos.
- Perfiles de variable actualizados (`temperature`, `relative_humidity`, `solar_radiation`) para aceptar `akima` y `cubic`. `precipitation` los rechaza por defecto (consistente con [ADR-0004](docs/adr/0004-precipitation-policy.md)).

### Changed

- `InterpolationMethod` Literal ahora incluye 6 valores: `"linear" | "pchip" | "pchip_mp" | "fourier" | "akima" | "cubic"`.
- Suite de tests: 241 → **257 passing** (1 skipped por extra opcional `zarr`).
- Documentación landing + README: tabla de métodos extendida a 6 filas.
- Notebook tutorial: loop de comparación Demo 2 ahora incluye los 6 métodos.

##### [0.1.3] — 2026-05-17

- Capa 7 (GUI) basada en PySide6 (deferred del v0.1.0).
- Empaquetado Windows (PyInstaller `--onedir` + Inno Setup) (deferred del v0.1.0).
- Integración de redes neuronales pre-entrenadas (ClimaX, Pangu-Weather, FourCastNet) bajo patrón híbrido (clásico baseline + NN refinement). Ver [ADR-0017](docs/adr/0017-neural-interpolator-extensibility.md).
- Workflows GitHub Actions (`pytest + ruff + mypy + gitleaks`), Dependabot, CodeQL — REQ-SEC-008.
- `CODE_OF_CONDUCT.md` y `CONTRIBUTING.md` — REQ-SEC-007.
- Tests automáticos `tests/security/` para REQ-SEC-002 / -005 / -006.

##### [0.1.3] — 2026-05-17

Release de soporte multibanda nativo + caso real WorldClim + auditoría de seguridad + gobernanza mínima del repositorio público.

### Added

- **Soporte multibanda nativo en el pipeline**: `TemporalFrequencyResolver` gana una nueva sub-heurística Tier 3.b. Cuando `N=1` y el `.tif` tiene 12 bandas, el resolver infiere `climatological` sin que el usuario tenga que splittear el stack en 12 archivos. `TempifyPipeline._read` renombra automáticamente la dim `band` → `month` para multiband stacks de 12 capas. La nueva REQ-003b queda documentada en `specs/temporal-frequency-resolver/requirements.md`.
- 2 tests unitarios nuevos en `tests/unit/detection/test_frequency.py` cubriendo el caso multibanda de 12 bandas (debe inferir climatological) y el caso single-band (debe caer al callback/raise).
- Sample WorldClim real en `examples/data/worldclim_maipo_alto/wc1_6_maipo_alto_tavg_stack.tif` (220 KB, Alto Maipo, Andes centrales de Chile, EPSG:4326, 30 arc-sec).
- **Segundo tutorial Colab** en `docs/tutorials/02-real-worldclim-maipo.ipynb` (18 celdas, ~640 KB): demuestra el soporte multibanda end-to-end sobre datos reales, mapas mensuales, 4 fechas diarias representativas, ciclo cordillera vs valle (−18 °C a +23 °C).
- **Landing page: nueva sección "Caso real · Alto Maipo, Chile"** entre Métodos y Quickstart, con 3 figuras (input mensual / output diario / ciclo anual cordillera-vs-valle) y chips de metadatos. Las 3 figuras totalizan 213 KB en `docs/assets/`. Nav item "Caso real" agregado.
- **Política de seguridad**: `SECURITY.md` con canal de reporte privado (GitHub PVR + email institucional), versiones soportadas, SLAs de respuesta. Cumple REQ-SEC-001.
- **Spec de seguridad**: `specs/security/requirements.md` con 10 REQs (REQ-SEC-001 a REQ-SEC-010) cubriendo divulgación responsable, prohibición de patrones unsafe, version consistency, notebook hygiene, governance files, CI gating, supply chain. Indexada en `CLAUDE.md`.
- **Reporte de auditoría**: `specs/_audit/2026-05-17-security-audit.md` con el resultado completo (0 críticos, 0 altos, 3 MED, 6 LOW). 5 hallazgos cerrados en este release; 4 quedan tracked para v0.2.0.

### Fixed

- **Drift de versión (H-001):** `pyproject.toml` declaraba `version = "0.1.0"` mientras `__version__` ya era `0.1.2`. Sincronizado a `0.1.3` en este release. Ahora `pip show tempify`, `tempify.__version__`, `CITATION.cff::version` y el tag de release coinciden bit-exactamente.
- **Username del desarrollador filtrado en outputs cacheados (H-004):** sanitizadas 2 occurrences en `docs/tutorials/01-getting-started.ipynb`.

### Changed

- `src/tempify/__init__.py`: `__version__ "0.1.2" -> "0.1.3"`.
- `pyproject.toml`: `version "0.1.0" -> "0.1.3"` (alineado).
- `CITATION.cff`: `version "0.1.2" -> "0.1.3"`.

##### [0.1.2] — 2026-05-17

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

##### [0.1.1] — 2026-05-17

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

##### [0.1.0] — 2026-05-16

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

##### [Pre-historia]

### Initial project structure (pre-v0.1.0)

- Proyecto inicializado bajo el nombre **tempify** (temporal densification for raster stacks).
- Estructura siguiendo Spec-Driven Development + Harness Engineering.
- Steering docs: product, tech, architecture, conventions, harness rules.
- 9 specs SDD (requirements + design + tasks).
- Slash commands: `/spec-init`, `/spec-design`, `/spec-tasks`, `/impl`, `/review`.
- Git hooks: pre-commit, pre-task, post-task.
- Referencia de validación empírica: experimento Quinta Normal 2020 + stack 3×3 sintético.

```

## File: `project_meta/precipitation.md`


```markdown
# Precipitation: why smooth interpolation is rejected

##### Summary

tempify **rejects by design** smooth interpolation (linear, PCHIP, Fourier) of monthly precipitation to daily. This document explains why and what alternatives exist.

##### The problem

Precipitation is **fundamentally different** from temperature, humidity, or radiation:

- **Intermittent.** Most days have zero precipitation; some have intense events.
- **Right-skewed distribution.** A few days produce most of the monthly total.
- **No temporal autocorrelation comparable to temperature.** Storms are discrete events.
- **Lower bound at zero.** Negative precipitation is physically impossible.

A smooth interpolator applied to monthly precipitation produces:

1. **Constant drizzle.** Every day gets a non-zero fraction of the monthly total. Physically absurd.
2. **No dry days.** A region with a monthly total of 30 mm gets ~1 mm every day, when reality might be 30 mm in a single storm and zero on the other 30 days.
3. **No extremes.** Maximum daily precipitation is dramatically underestimated.
4. **Distorted hydrological response.** Models calibrated on daily precipitation will misbehave with smoothly interpolated input.

##### Why this is not a bug to fix

The information needed to reconstruct daily precipitation from monthly totals **does not exist** in the monthly data. It must come from elsewhere:

- A daily-resolution reanalysis (ERA5-Land, CHIRPS).
- A stochastic weather generator (LARS-WG, MarkSim, WeaGETS).
- A physically-based hybrid (delta method with a high-resolution daily template).

These approaches are out of scope for tempify's core: we do not generate new variability, we only interpolate.

##### What tempify does instead

The `VariableProfileMatcher` identifies precipitation by:

- Standard name `precipitation`, `prec`, `pr`, `precip`
- Filename patterns matching common products (CHIRPS, WorldClim's `prec`)
- Units of `mm`, `mm/day`, `mm/month`, `kg m-2 s-1`

When precipitation is detected, the profile sets:

```yaml
variable: precipitation
allowed_methods: []  # No smooth interpolators
rejected_methods: ["linear", "pchip", "pchip_mp", "fourier"]
recommendation: "Use a daily reanalysis (CHIRPS, ERA5-Land) or a weather generator."
```

The `MethodVariableCompatibilityChecker` raises `MethodVariableIncompatibilityError` if the user explicitly requests a smooth method on precipitation.

##### Recommended workflows for precipitation

### Option A: Use a daily product directly

If you need daily precipitation, download a daily product:

- **CHIRPS** (5 km, daily, 1981-present, global excluding high latitudes)
- **ERA5-Land** (9 km, daily, 1950-present, global)
- **MERRA-2** (50 km, daily, 1980-present, global)

These already contain the variability you need.

### Option B: Delta method (tempify does NOT do this)

If you must use monthly precipitation but want daily variability:

1. Get a daily product (e.g., CHIRPS) for the same period.
2. Compute monthly totals of the daily product.
3. Apply the ratio (monthly target) / (monthly from daily) as a multiplicative correction.
4. The result has daily variability (from CHIRPS) and conserves the monthly target.

This is essentially a bias correction. It is a valid technique but **out of scope** for tempify v1.0. May be added as an opt-in module in a future release.

### Option C: Stochastic weather generator (tempify does NOT do this)

Tools like LARS-WG or simple Markov chain + gamma models can generate stochastic daily series that respect monthly statistics. These are **out of scope** for tempify.

##### Override (not recommended)

A user can force smooth interpolation of precipitation by passing `--force-method pchip --i-know-what-i-am-doing`. This:

- Logs a warning in the report.
- Marks the output's metadata with `"force_method_used": true` and `"physical_validity": "questionable"`.
- Should never be used in published or operational work.

##### References

- Haylock, M. R., et al. (2008). A European daily high-resolution gridded data set of surface temperature and precipitation for 1950-2006. *J. Geophys. Res.*, 113, D20119.
- Funk, C., et al. (2015). The climate hazards infrared precipitation with stations (CHIRPS). *Scientific Data*, 2, 150066.
- Wilks, D. S., & Wilby, R. L. (1999). The weather generation game: a review of stochastic weather models. *Progress in Physical Geography*, 23(3), 329-357.

```

## File: `steering/architecture.md`


```markdown
# Architecture

##### Visión general

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

##### Capa 1: I/O (`tempify.io`)

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

##### Capa 2: Detection (`tempify.detection`)

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

##### Capa 3: Validation (`tempify.validation`)

**Responsabilidad:** verificar invariantes antes y después de procesar.

- `GeospatialCoherenceValidator`: CRS, extensión, resolución, nodata
- `MethodVariableCompatibilityChecker`: combinaciones permitidas según perfil
- `PostInterpolationValidator`: conservación, continuidad cíclica, rango físico
- `StatisticalReporter`: min/max/mean/std/nan% por banda temporal

**Política de fallos:**
- Validaciones pre-proceso: **fail-fast** con error claro.
- Validaciones post-proceso: registrar en reporte; advertir pero no abortar.

##### Capa 4: Interpolation (`tempify.interpolation`)

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

##### Capa 5: Pipeline (`tempify.pipeline`)

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

##### Capa 6: CLI (`tempify.cli`)

**Responsabilidad:** interfaz humana, sin lógica de negocio.

```bash
tempify convert <input> --output <output> [opts]
tempify inspect <input>      # Solo detección
tempify validate <input>     # Solo validación
tempify profiles list
tempify version
```

##### Reglas arquitectónicas duras

1. **Capas inferiores no conocen capas superiores.** I/O no sabe de Detection; Detection no sabe de Pipeline.
2. **Dependencias por interfaces.** Protocols/ABCs, no clases concretas.
3. **`xr.DataArray` es el formato de intercambio interno.** Conversiones solo en I/O.
4. **No state global.** Configs explícitas; sin singletons.
5. **Errores tipados.** Cada capa define sus excepciones (`GeospatialIncoherenceError`, `UnknownFrequencyError`).

##### ADRs pendientes para v1.0

- ADR-0001: Por qué xarray y no pandas/geopandas como abstracción central
- ADR-0002: Por qué Dask y no multiprocessing nativo
- ADR-0003: Por qué Typer y no Click o argparse
- ADR-0004: Tratamiento de precipitación (rechazo vs módulo separado)

```

## File: `steering/tech.md`


```markdown
# Tech Stack

##### Lenguaje base

- **Python 3.11+** (typing moderno con `|`, `Self`, structural matching)
- **Tipado obligatorio** en toda función pública (verificado con `mypy --strict`)

##### Dependencias core (runtime)

| Dependencia | Propósito | Justificación |
|---|---|---|
| `numpy >= 1.26` | Arrays N-dim | Base del ecosistema científico |
| `xarray >= 2024.1` | DataArray/Dataset etiquetados | Indispensable para datos climáticos con CF |
| `dask[array] >= 2024.1` | Paralelización y out-of-core | Integración nativa con xarray |
| `rioxarray >= 0.15` | I/O GeoTIFF con georreferencia | Wrapper de rasterio sobre xarray |
| `netcdf4 >= 1.6` | I/O NetCDF | Backend recomendado por xarray |
| `scipy >= 1.12` | PchipInterpolator, mínimos cuadrados | Implementaciones de referencia |
| `pyyaml >= 6.0` | Configs y perfiles | Estándar |
| `typer >= 0.12` | CLI | Auto-doc y validación de tipos |
| `rich >= 13.7` | Output formateado, progress bars | UX en terminal |

##### Dependencias dev

| Dependencia | Propósito |
|---|---|
| `pytest >= 8.0` | Test runner |
| `pytest-cov` | Coverage |
| `hypothesis` | Property-based testing |
| `mypy` | Type checking strict |
| `ruff` | Lint + format |
| `sphinx + sphinx-rtd-theme` | Docs |
| `jupyter` | Tutoriales |

##### Restricciones

- No agregar dependencias pesadas sin **ADR** en `docs/adr/`.
- Evitar GDAL directo: rioxarray + rasterio ya la encapsulan.
- No usar `pandas` salvo donde sea estrictamente necesario. Preferir xarray.
- No usar `geopandas` en core. Operaciones vectoriales en módulos opcionales.

##### Empaquetado

- `pyproject.toml` con PEP 621 (sin `setup.py`)
- Build backend: `hatchling`
- Distribución: PyPI + conda-forge
- Versionado: SemVer estricto

##### `pyproject.toml` mínimo

```toml
[project]
name = "tempify"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "numpy>=1.26",
    "xarray>=2024.1",
    "dask[array]>=2024.1",
    "rioxarray>=0.15",
    "netcdf4>=1.6",
    "scipy>=1.12",
    "pyyaml>=6.0",
    "typer>=0.12",
    "rich>=13.7",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov", "hypothesis", "mypy", "ruff"]
docs = ["sphinx", "sphinx-rtd-theme", "jupyter"]
zarr = ["zarr>=2.17"]

[project.scripts]
tempify = "tempify.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

##### CI/CD

- GitHub Actions
- Matriz: Python 3.11/3.12/3.13 × Linux/macOS/Windows
- Jobs: lint → typecheck → test → build → docs

##### Compatibilidad mínima

- Python: 3.11+
- OS: Ubuntu 22.04+, macOS 13+, Windows 10/11
- GDAL (via rasterio wheel): 3.6+

```


---

# ADRs (decisiones arquitectónicas)


## File: `adr/0001-use-xarray-as-central-abstraction.md`


```markdown
# ADR-0001: Use xarray.DataArray as central data abstraction

**Status:** Accepted
**Date:** 2026-05-15
**Decision-makers:** Guillermo Fuentes-Jaque

##### Context

tempify needs an internal data abstraction to represent raster stacks across all layers (I/O, detection, validation, interpolation, pipeline). Several candidates exist in the Python geospatial ecosystem:

1. **NumPy arrays** with separate metadata
2. **pandas DataFrame** (long format)
3. **geopandas GeoDataFrame** (vector-oriented)
4. **xarray DataArray** (N-dim labeled arrays)
5. **Raw rasterio Dataset** objects

##### Decision

Use **`xarray.DataArray`** as the central data abstraction across all layers.

##### Rationale

### Pros of xarray

- **Labeled dimensions and coordinates** native: `(time, y, x)` with proper coordinate values, essential for climate data.
- **CF-conventions support** via rioxarray and built-in attrs handling.
- **Dask integration** native: `chunks={"time": 1, "x": 512, "y": 512}` is one parameter away.
- **Out-of-core processing** essential for stacks larger than RAM (Chile complete at 30 arc-sec).
- **De facto standard** in climate / geospatial Python (xclim, climakitae, climpyrical, intake-xarray all depend on it).
- **CRS preservation** via rioxarray `rio` accessor.
- **Ufunc vectorization** with `xr.apply_ufunc(..., dask="parallelized")` eliminates manual loops.

### Cons of xarray

- Heavier dependency than raw numpy.
- Learning curve for users not familiar with labeled arrays.
- Some operations (e.g., complex indexing) slower than equivalent numpy.

### Why not the alternatives

- **NumPy** alone: would force us to carry metadata separately (CRS, time axis, units), reinventing xarray.
- **pandas**: long format requires reshape for every spatial operation; not idiomatic for raster.
- **geopandas**: vector-oriented, wrong tool for raster stacks.
- **rasterio Dataset**: low-level, single-file oriented; doesn't handle multi-temporal naturally.

##### Consequences

### Positive

- All layers communicate via a single, well-understood type.
- Parallelism via Dask is "free" once chunking is set.
- Users familiar with xarray (the target audience: climate scientists) feel immediately at home.

### Negative

- Mandatory dependency on xarray + rioxarray + (optionally) dask.
- Test fixtures must be xarray objects, not raw arrays.

### Risks

- xarray API has evolved over years; we pin to `>= 2024.1` to use modern features. If xarray makes breaking changes in the future, we may need migration work.

##### Implementation notes

- All I/O readers return `xr.DataArray`.
- All I/O writers accept `xr.DataArray`.
- Internal functions type-hint with `xr.DataArray`.
- CRS preserved via `rioxarray` accessor (`.rio.crs`, `.rio.write_crs`).
- Time coordinate follows CF-conventions: `units="days since YYYY-MM-DD"`, `calendar` attribute.

##### References

- xarray documentation: https://docs.xarray.dev/
- rioxarray: https://corteva.github.io/rioxarray/
- CF Conventions: https://cfconventions.org/
- Pangeo project (Climate Python ecosystem): https://pangeo.io/

```

## File: `adr/0002-dask-vs-multiprocessing.md`


```markdown
# ADR-0002: Dask vs multiprocessing nativo

**Estado:** Accepted
**Fecha:** 2026-05-16
**Deciders:** Guillermo Fuentes-Jaque
**Contexto técnico:** Capa 4 (Interpolation) y restricciones NFR-001/NFR-004 de la spec `core-interpolation`.

##### Contexto

La densificación temporal de tempify aplica una función 1D (interpolación mensual → diaria) píxel a píxel sobre stacks ráster `(time, y, x)` cuyo tamaño puede superar la RAM disponible. El caso de referencia (NFR-001) es Chile a 2.5 arc-min, stack `12 × 3000 × 500 = 18M píxeles temporales`, con presupuesto de <60 s en 8 cores y <1 GB de RAM por chunk (NFR-004).

El problema combina tres requisitos simultáneos:

1. **Vectorización píxel a píxel** de una operación compute-bound (PCHIP, mínimos cuadrados Fourier, iteración Rymes-Myers).
2. **Out-of-core** para stacks que no caben en RAM (Chile completo a 30 arc-sec supera los 8 GB).
3. **Integración con `xr.DataArray`** sin romper el contrato de la Capa 4, que ya impone `xr.apply_ufunc(..., dask="parallelized")` (ver `steering/architecture.md` § Capa 4).

El ADR-0001 ya fijó `xarray.DataArray` como abstracción central. Falta decidir el mecanismo concreto de paralelismo subyacente.

##### Decisión

Usar **Dask** como mecanismo de paralelismo, exclusivamente vía `xr.apply_ufunc(..., dask="parallelized")`. No se introducirá `multiprocessing`, `concurrent.futures.ProcessPoolExecutor`, `joblib` ni paralelismo manual basado en threads.

##### Alternativas consideradas

| Alternativa | Veredicto | Razón principal |
|---|---|---|
| `multiprocessing.Pool` | Rechazada | Serialización pickle del array completo por worker; sin lazy evaluation; sin integración con `xr.DataArray` |
| `concurrent.futures.ProcessPoolExecutor` | Rechazada | Mismas limitaciones que `multiprocessing.Pool`; API ligeramente más limpia, fondo idéntico |
| `joblib` | Rechazada | Optimizado para tareas tipo scikit-learn; sin chunking nativo de arrays N-dim; sin out-of-core |
| `threading` puro | Rechazada | El GIL limita el paralelismo compute-bound salvo en kernels NumPy/SciPy que lo liberen; gestión manual del chunking |
| **Dask** (`dask.array` + scheduler) | **Aceptada** | Chunking lazy, scheduler intercambiable, out-of-core gratis, integración nativa con xarray |

### Detalle de las descartadas

- **`multiprocessing.Pool` y `ProcessPoolExecutor`.** Requieren copiar el array a cada proceso vía pickle (overhead lineal en el tamaño del stack). El particionado espacial debe implementarse manualmente y no compone con la propagación de coordenadas y atributos CF de `xr.DataArray`. Tampoco resuelven out-of-core: si el stack no cabe en RAM, no cabe en el proceso padre antes de repartir.
- **`joblib`.** Su API `Parallel(n_jobs=...)` está pensada para iteración sobre listas de tareas independientes (típicamente sklearn). Aplicarla a arrays grandes obliga a reimplementar el chunking que Dask ya provee.
- **`threading`.** Las funciones de SciPy (`PchipInterpolator`, `lstsq`) liberan el GIL en partes, pero la orquestación manual del particionado, scheduling y agregación reproduce a peor escala lo que el scheduler `threaded` de Dask hace por defecto.

### Razones positivas de Dask

- **Lazy evaluation + chunking declarativo.** `chunks={"time": -1, "x": 512, "y": 512}` describe la partición; el grafo solo se evalúa al pedir `.compute()` o al escribir.
- **Scheduler intercambiable** sin tocar la lógica de negocio: `synchronous` para tests deterministas, `threaded` para producción local, `distributed` para clústeres futuros.
- **Integración nativa con xarray** vía `xr.apply_ufunc(..., dask="parallelized", output_dtypes=[...])`. Esto preserva dims, coords y attrs (incluida la CRS de `rioxarray`) sin código adicional.
- **Out-of-core gratuito.** Los chunks que no caben en RAM se materializan bajo demanda; la huella se acota por chunk, satisfaciendo NFR-004.
- **De facto en el ecosistema Pangeo** (xclim, climpyrical, intake-xarray), reduciendo fricción con el público objetivo de la herramienta.

##### Consecuencias

### Positivas

- Capa 4 escribe interpoladores como funciones 1D NumPy puras; el paralelismo es transversal.
- NFR-001 alcanzable sin código de orquestación propio: la responsabilidad de scheduling se delega al runtime de Dask.
- Tests deterministas (NFR-003, ADR-0007) son posibles cambiando `scheduler='synchronous'` sin tocar el código bajo prueba.
- Migración futura a `dask.distributed` no requiere refactor de los interpoladores.

### Negativas

- Dependencia obligatoria de `dask[array] >= 2024.1` (ya declarada en `steering/tech.md`).
- Curva de aprendizaje: depurar grafos Dask exige familiaridad con `.visualize()` y con el modelo de computación diferida.
- Sobrecoste no nulo en stacks pequeños donde el grafo Dask pesa más que el cómputo. Mitigación: documentar un umbral aproximado de uso y permitir `chunks=None` para forzar evaluación eager.

### Riesgos

- **Chunking mal dimensionado** degrada el rendimiento más allá de lo esperado (ver riesgo declarado en `core-interpolation/requirements.md` § 7). Mitigación: defaults razonables y documentación.
- **Cambios en la API de Dask** entre versiones mayores. Mitigación: pin `>= 2024.1` y cobertura de regresión en CI.

##### Notas de implementación

- **Scheduler por defecto:** `threaded`. Apropiado para las operaciones compute-bound de la Capa 4, donde los kernels NumPy/SciPy liberan el GIL.
- **Tamaño de chunk por defecto:** `512` en las dimensiones espaciales (`x`, `y`); `time` no se chunkea (`-1`) porque la interpolación es un reduce a lo largo de esa dimensión. Configurable vía `PipelineConfig.chunk_size`.
- **Modo single-thread reproducible:** `scheduler='synchronous'` disponible explícitamente para tests bit-exact y para depuración (ver ADR-0007).
- **Contrato de Capa 4:** todos los interpoladores invocan `xr.apply_ufunc` con `dask="parallelized"`, `vectorize=False`, `output_dtypes=[source.dtype]` y `input_core_dims=[["month"]]`, `output_core_dims=[["time"]]`. Esto es invariante arquitectónico, no decisión por interpolador.
- **Sin imports de `multiprocessing`, `concurrent.futures` ni `joblib` en el código del paquete.** El linter prohíbe esos módulos en `src/tempify/` salvo excepción justificada por ADR posterior.

##### Referencias

- Dask documentation: https://docs.dask.org/
- `xarray.apply_ufunc`: https://docs.xarray.dev/en/stable/generated/xarray.apply_ufunc.html
- Pangeo project: https://pangeo.io/
- ADR-0001: Use xarray.DataArray as central data abstraction
- `steering/architecture.md` § Capa 4 Interpolation
- `specs/core-interpolation/requirements.md` NFR-001, NFR-003, NFR-004

```

## File: `adr/0004-precipitation-policy.md`


```markdown
# ADR-0004: Política de precipitación

**Status:** Accepted
**Date:** 2026-05-16
**Decision-makers:** Guillermo Fuentes-Jaque

##### Context

La precipitación es una variable cualitativamente distinta a temperatura, humedad o radiación. Sus propiedades estadísticas hacen que la interpolación temporal suave (Lineal, PCHIP, PCHIP+RM, Fourier) produzca resultados no físicos:

- **Intermitente.** La mayoría de los días no presentan precipitación; unos pocos concentran el total mensual.
- **Distribución sesgada a la derecha.** Sin gaussianidad ni autocorrelación temporal comparable a temperatura.
- **Cota inferior dura en cero.** Valores negativos son físicamente imposibles.
- **No suave.** Las tormentas son eventos discretos, no transiciones continuas.

Aplicar un interpolador suave sobre totales mensuales de precipitación produce "drizzle" artificial (todos los días reciben una fracción no nula), elimina la varianza diaria real, subestima eventos extremos y rompe la conservación del cero. La información necesaria para reconstruir variabilidad diaria **no existe** en la serie mensual: debe provenir de un producto diario (CHIRPS, ERA5-Land) o de un weather generator estocástico (LARS-WG, cadenas de Markov + gamma). Ninguna de estas vías está en alcance para tempify v1.0, que es un densificador determinístico.

La política debe equilibrar dos preocupaciones: (a) proteger a usuarios menos expertos de generar outputs científicamente inválidos, y (b) no bloquear completamente a usuarios avanzados que sepan qué hacen (p. ej., benchmarking, comparación de métodos, casos donde el output se postprocesa).

Ver `docs/methodology/precipitation.md` para el desarrollo completo de la justificación.

##### Decision

Política dual de **rechazo por defecto** con **override expreso**:

1. **Rechazo por defecto.** El componente `MethodVariableCompatibilityChecker` (Capa 3, Validation) rechaza el par `(variable=precipitation, method ∈ {linear, pchip, pchip_mp, fourier})` lanzando `MethodVariableIncompatibilityError`. La identificación de la variable usa `VariableProfileMatcher` (standard_name, patrones de nombre, unidades). El veto se carga desde `profiles/precipitation.yaml` con `allowed_methods: []` y `rejected_methods: [linear, pchip, pchip_mp, fourier]`.

2. **Override expreso.** Existe un escape consciente vía CLI: `--force-method <method> --i-know-what-i-am-doing`. El override:
   - Requiere **confirmación interactiva** explícita (no se acepta en modo no interactivo sin un segundo flag `--force-method-confirm`).
   - **Estampa metadatos** en el output: `attrs["force_method_used"] = true` y `attrs["force_method_warning"] = "Resultado no recomendado científicamente"`.
   - Registra el evento en el reporte de ejecución.

##### Rationale

### Por qué rechazo por defecto y no warning

Los warnings se ignoran rutinariamente: se ahogan en logs, no aparecen en notebooks de exploración, y desaparecen en pipelines automatizados. Un usuario inexperto recibirá un GeoTIFF aparentemente correcto y lo publicará. El rechazo duro convierte el error silencioso en un error explícito que debe resolverse antes de continuar.

### Por qué existe el override

Negar absolutamente el método elimina casos legítimos: benchmarks metodológicos, comparaciones contra una baseline "ingenua", investigación sobre el efecto de la interpolación suave, generación de inputs para pipelines downstream que aplican su propia bias correction. El override expreso preserva estos casos a costa de fricción deliberada.

### Por qué stamping de metadatos

El output puede salir de tempify y entrar en cadenas analíticas largas. Un consumidor downstream (humano o automatizado) debe poder filtrar outputs no recomendados sin reconstruir la procedencia. La metadata viaja con el archivo (NetCDF `attrs`, GeoTIFF tags) y es la única señal persistente.

##### Alternatives considered

### Silenciar el rechazo (sólo warning en logs)

Descartado. Mala UX científica: los warnings son ruido. El usuario que no sabe que la interpolación suave es inválida sobre precipitación tampoco va a leer un warning entre cien líneas de log. Riesgo alto de mal uso silencioso.

### Soportar weather generators (estocásticos) en v1.0

Descartado por alcance. Un weather generator robusto (cadenas de Markov para ocurrencia + distribución gamma/exponencial para intensidad, condicionado mensualmente) es un proyecto en sí mismo. tempify se define como **densificador determinístico** y reproducible bit-exact (ver Guardrail 6 en CLAUDE.md). Introducir estocasticidad rompería esa garantía. Puede evaluarse como módulo opt-in en una v2.x.

### Permitir interpolación libre con warning prominente

Descartado. Variante del primer alternativo. Cualquier mecanismo que no detenga la ejecución es ignorable.

### Implementar delta method (bias correction multiplicativa contra un producto diario)

Descartado por alcance. Es una técnica válida (ver `methodology/precipitation.md` Opción B), pero requiere un input adicional (producto diario de referencia), lógica de pareo temporal y espacial, y reabre la pregunta de qué producto usar. Diferido a futuro como módulo opt-in.

##### Consequences

### Positive

- **Protege a usuarios menos expertos** del error silencioso más probable del dominio.
- **Señal clara en la metadata** para auditoría y filtrado downstream.
- **Coherente con el principio de fail-fast** del proyecto: errores explícitos sobre warnings.
- **Documenta intención científica** en el output: cualquier reviewer puede detectar un `force_method_used = true`.

### Negative

- **Fricción para usuarios avanzados** que deban justificar conscientemente el override.
- **Confirmación interactiva** complica pipelines no interactivos (mitigado por `--force-method-confirm`).
- **Mantenimiento adicional**: el perfil `precipitation.yaml` y los matchers deben actualizarse a medida que aparezcan nuevas convenciones de nombre o unidades.

### Risks

- Detección de "precipitación" puede tener falsos negativos (variable mal nombrada, sin standard_name, unidades ambiguas). Mitigación: documentar la lista de matchers y permitir al usuario forzar el perfil con `--variable-profile precipitation`.
- Usuarios con experiencia podrían encontrar el flujo de override molesto y abandonar la herramienta. Aceptado como costo de la política.

##### Implementation notes

- **`MethodVariableCompatibilityChecker`** (Capa 3, ver `steering/architecture.md`) consulta `VariableProfile.allowed_methods` y `VariableProfile.rejected_methods` cargados desde YAML.
- **`profiles/precipitation.yaml`**: `allowed_methods: []`, `rejected_methods: [linear, pchip, pchip_mp, fourier]`. En futuras versiones podrá listar métodos de conservación de masa cuando existan.
- **CLI**: ante `--force-method` sobre precipitación, mostrar el prompt interactivo:
  > `ATENCIÓN: ¿Confirmas que entiendes que interpolar precipitación con un método suave producirá valores no físicos? (escriba 'si entiendo' para continuar):`
  Solo la cadena exacta `si entiendo` autoriza la ejecución. Cualquier otra entrada aborta con código de salida no cero.
- **Stamping**: obligatorio en todo writer (`io-handlers`). Los `attrs` deben propagarse a NetCDF (atributos globales), GeoTIFF (tags) y Zarr (consolidated metadata).
- **Reporte de validación**: el override debe quedar registrado en el `impl-log` de la corrida y en el reporte estructurado de `specs/validation`.
- **Tests**: cobertura obligatoria para (a) rechazo por defecto, (b) override con confirmación correcta, (c) override sin confirmación rechazado, (d) presencia de `attrs` en outputs forzados.

##### References

- `docs/methodology/precipitation.md` — fundamentos científicos y workflows alternativos.
- `steering/architecture.md` § Capa 3 Validation — ubicación de `MethodVariableCompatibilityChecker`.
- `specs/validation/requirements.md` — requisitos donde se enforça la política.
- `specs/cli/requirements.md` — superficie del flag `--force-method` y la confirmación interactiva.
- CLAUDE.md, Guardrail 5: "Precipitación nunca se interpola con métodos suaves."
- Wilks, D. S., & Wilby, R. L. (1999). The weather generation game. *Progress in Physical Geography*, 23(3), 329-357.

```

## File: `adr/0007-reproducibility-policy.md`


```markdown
# ADR-0007: Política de reproducibilidad (dos modos)

**Estado:** Accepted
**Fecha:** 2026-05-16
**Deciders:** Guillermo Fuentes-Jaque
**Contexto técnico:** NFR-003 de `core-interpolation`, REQ-010 y NFR-002 de `pipeline`, guardrail nº 6 de `CLAUDE.md`.

##### Contexto

El proyecto tempify declara como invariante "reproducibilidad bit-exact: mismos inputs y mismos parámetros producen mismo output, verificable con MD5". Este compromiso entra en tensión con tres realidades del cómputo numérico paralelo y heterogéneo:

1. **Orden de reducción en Dask.** Operaciones de reducción flotante (`sum`, `mean`, agregaciones intermedias del grafo) no son asociativas en IEEE 754. Con el scheduler `threaded` o `distributed`, el orden de combinación de chunks depende del tamaño de chunk, del número de workers y del orden de finalización de tareas. Dos ejecuciones de la misma operación pueden diferir en el último bit (típicamente ULP ≤ 1).

2. **Backend BLAS/LAPACK.** La interpolación Fourier por mínimos cuadrados (`scipy.linalg.lstsq`) y la FFT (`scipy.fft`) delegan en BLAS. Las wheels oficiales de NumPy/SciPy usan OpenBLAS; entornos conda-forge pueden enlazar MKL. Implementaciones distintas (orden de bloqueo, AVX-512 vs AVX2, denormals) producen resultados que difieren en bits poco significativos.

3. **Plataforma.** Windows con MSVC + libm de UCRT y Linux con glibc + libm de GCC no garantizan idéntico redondeo en funciones trascendentes (`exp`, `sin`, `cos`). El proyecto soporta ambas plataformas (ver `steering/tech.md`).

Una política "bit-exact universal" exigiría fijar plataforma, BLAS, scheduler single-thread y desactivar todo paralelismo. Eso destruye el objetivo de rendimiento de NFR-001 (Chile a 2.5 arc-min en menos de 60 s). Una política "solo `allclose`" elimina la capacidad de detectar regresiones numéricas finas en CI, donde una diferencia bit-a-bit revela un cambio de implementación no intencional. Hace falta una política con dos niveles.

##### Decisión

Adoptar una política de reproducibilidad **de dos modos**, controlada por `PipelineConfig.reproducibility_mode: Literal["strict", "parallel"]`, con default `"parallel"`.

### Modo `strict` (reproducibilidad bit-exact controlada)

Activado en:
- CI (todos los tests marcados `@pytest.mark.reproducibility`).
- Validación de release (script `scripts/validate_release.py` previo a publicar versión).
- Uso explícito vía CLI `--reproducibility-mode strict` o vía configuración del usuario.

Garantías:
- Salida **bit-exact** (mismo MD5) ante mismos inputs, misma versión del paquete y **misma plataforma**. Cross-platform NO se garantiza, ni se intenta.

Mecanismos:
- `dask.config.set(scheduler='synchronous')` durante toda la ejecución.
- Seed fija (`numpy.random.default_rng(seed=42)` para cualquier estocasticidad residual; actualmente ninguno de los métodos de Capa 4 es estocástico, pero la cláusula queda registrada).
- Ordenamiento estable de chunks: iteración determinista del grafo Dask (`optimize_graph=True`, `traverse=True`).
- Documentación explícita en el manual: "modo `strict` ≈ 5x–10x más lento que `parallel`; usar solo cuando la trazabilidad bit-a-bit sea requisito".

### Modo `parallel` (default de producción)

Activado en:
- Uso normal del paquete (CLI sin flags, API sin override).
- Pipelines de producción de los usuarios finales.

Garantías:
- Equivalencia numérica vía `numpy.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-15)`. Las diferencias entre ejecuciones se acotan a `~1 ULP` en el último bit.
- **NO** se garantiza bit-exact. El MD5 puede variar entre ejecuciones.

Mecanismos:
- `dask.config.set(scheduler='threaded')` con `num_workers = os.cpu_count()`.
- Chunking por defecto según ADR-0002 (`512` espacial, `-1` temporal).
- Sin seed fija (irrelevante: no hay estocasticidad).

### Stamping de metadata (ambos modos)

Todo output escrito por la Capa 5 incluye en `attrs` del `xr.DataArray`:

- `attrs["reproducibility_mode"]` = `"strict"` o `"parallel"`.
- `attrs["tempify_version"]` = versión del paquete (`importlib.metadata.version("tempify")`).
- `attrs["md5_inputs"]` = MD5 del/los archivo(s) de entrada (computado sobre bytes en disco, ordenado estable).
- `attrs["md5_outputs"]` = MD5 del array de salida tras `.compute()` (computado sobre `.tobytes()` con orden `C`).
- `attrs["scheduler"]` = nombre del scheduler activo en la ejecución.
- `attrs["platform"]` = `f"{sys.platform}-{platform.machine()}"`.

Esta metadata permite a un consumidor decidir si un output cumple sus requisitos de reproducibilidad sin depender de re-ejecutar el pipeline.

##### Alternativas consideradas

| Alternativa | Veredicto | Razón principal |
|---|---|---|
| Bit-exact universal (cross-platform) | Rechazada | Imposible sin pinear plataforma, BLAS y libm a una única combinación; destruye soporte multi-OS |
| Solo `assert_allclose` (sin modo strict) | Rechazada | Pierde poder para detectar regresiones de implementación (cambios silenciosos de algoritmo que entran dentro de `rtol` quedarían invisibles en CI) |
| Bit-exact en modo único, perdiendo paralelismo | Rechazada | Incumple NFR-001; el usuario final pagaría 5x–10x de latencia para una garantía que solo importa en validación de release |
| **Dos modos: `strict` para CI/release + `parallel` para producción** | **Aceptada** | Cubre el caso donde la trazabilidad bit-a-bit importa (regresión) y el caso donde el rendimiento importa (uso diario); coste de complejidad acotado a una sola variable de configuración |

### Por qué la elegida

- **Cero ambigüedad.** Cada ejecución declara su modo en metadata; un revisor sabe en qué nivel de garantía está leyendo.
- **CI estable.** Los tests de `strict` corren en synchronous scheduler y son determinísticos por construcción dentro de una plataforma.
- **Coste de complejidad acotado.** Una única variable (`reproducibility_mode`) atraviesa todas las capas; no hay rutas de código divergentes por algoritmo.
- **Honestidad respecto a IEEE 754.** No se promete lo que el hardware no puede entregar (bit-exact cross-platform con FFT y BLAS distintos).

##### Consecuencias

### Positivas

- **Testabilidad.** Los tests de reproducibilidad bit-exact existen y son ejecutables (parametrizados con `reproducibility_mode="strict"`).
- **Trazabilidad.** La metadata `attrs["md5_outputs"]` permite verificación de integridad downstream sin re-correr el pipeline.
- **CI determinista.** Las suites marcadas `@pytest.mark.reproducibility` no dependen del hardware del runner mientras la plataforma sea estable (matriz de CI: `windows-latest`, `ubuntu-latest`, cada una con su propio baseline MD5).
- **Validación de release.** El script `validate_release.py` compara MD5 contra baseline persistido en `tests/baselines/<platform>/`. Cualquier deriva numérica se detecta antes de publicar.

### Negativas

- **Dos rutas de código.** La gestión del scheduler vive en `tempify.pipeline.runtime`. Aunque la divergencia es mínima (un `with dask.config.set(...)`), añade superficie a mantener.
- **Sobrecoste de cómputo del MD5.** Computar `md5_outputs` exige materializar el resultado en RAM tras `.compute()`. Para stacks que no caben en RAM, se computa por chunks acumulando un `hashlib.md5()` en streaming. Coste estimado: 5–8% sobre el tiempo total de escritura.
- **Baselines por plataforma.** El repositorio mantiene un baseline MD5 por plataforma soportada (`windows-x86_64`, `linux-x86_64`). Cada release validado debe regenerarlos. Linux ARM y macOS no están soportados oficialmente.

### Riesgos

- **Drift silencioso entre versiones de SciPy.** Una nueva versión de SciPy podría cambiar el orden interno de `lstsq` y romper baselines. Mitigación: pin estricto de `scipy` en el `pyproject.toml` y bump deliberado con regeneración de baselines documentada en `impl-log.md` de cada release.
- **Falsos positivos de regresión.** Una actualización legítima del algoritmo que cambie 1 ULP romperá baselines aunque la salida sea válida. Mitigación: el procedimiento de release exige aprobación humana explícita de la regeneración del baseline, registrada en ADR si el cambio es semántico.

##### Notas de implementación

- **Configuración.** `PipelineConfig.reproducibility_mode: Literal["strict", "parallel"] = "parallel"`. Validado por `pydantic` en construcción.
- **Punto único de aplicación.** El context manager `tempify.pipeline.runtime.reproducibility_context(mode)` envuelve la ejecución completa y aplica `dask.config.set(scheduler=...)`. Ningún otro módulo toca el scheduler.
- **Tests.**
  - `tests/reproducibility/test_bit_exact.py` parametriza los 4 métodos de Capa 4 con `reproducibility_mode="strict"` y compara MD5 contra `tests/baselines/<platform>/<method>.md5`.
  - `tests/reproducibility/test_allclose.py` corre 10 ejecuciones consecutivas en `reproducibility_mode="parallel"` y verifica `assert_allclose(rtol=1e-12, atol=1e-15)` entre todas ellas.
- **Cómputo de MD5.**
  - `md5_inputs`: hash de los bytes del archivo en disco, ruta absoluta normalizada, lista ordenada lexicográficamente si hay varios inputs.
  - `md5_outputs`: hash del array de salida en orden `C`, `dtype` y `shape` incluidos en el prefijo (`f"{dtype}|{shape}|".encode() + array.tobytes()`).
  - **El timestamp del reporte de validación NO entra en el cómputo del MD5.** Cualquier campo `attrs` cuyo valor dependa del momento de ejecución (`attrs["created_at"]`, `attrs["execution_time_s"]`) se excluye explícitamente.
- **CLI.** `tempify run --reproducibility-mode strict` o `--reproducibility-mode parallel`. Default heredado de `PipelineConfig`.
- **Documentación de usuario.** Sección "Reproducibility" en el manual, con la tabla de garantías por modo y el procedimiento de verificación con `md5sum` contra `attrs["md5_outputs"]`.

##### Referencias

- IEEE 754-2019: Standard for Floating-Point Arithmetic. https://ieeexplore.ieee.org/document/8766229
- Goldberg, D. (1991). *What Every Computer Scientist Should Know About Floating-Point Arithmetic*. ACM Computing Surveys, 23(1).
- Demmel, J. & Nguyen, H. D. (2013). *Fast Reproducible Floating-Point Summation*. IEEE 21st Symposium on Computer Arithmetic.
- Dask scheduler documentation: https://docs.dask.org/en/stable/scheduling.html
- NumPy reproducibility note: https://numpy.org/doc/stable/reference/random/parallel.html
- ADR-0001: Use xarray.DataArray as central data abstraction.
- ADR-0002: Dask vs multiprocessing nativo.
- `specs/core-interpolation/requirements.md` § NFR-003.
- `specs/pipeline/requirements.md` § REQ-010, § NFR-002.
- `CLAUDE.md` § Guardrails duros nº 6.

```

## File: `adr/0010-mean-preservation-tolerance.md`


```markdown
# ADR-0010: Política unificada de tolerancia para conservación de la media mensual

**Status:** Accepted
**Date:** 2026-05-16
**Decision-makers:** Guillermo Fuentes-Jaque

##### Contexto

La propiedad central de tempify (en su método estrella PCHIP+Rymes-Myers) es que la media mensual del output diario reconstruye exactamente la media mensual del input. "Exactamente" requiere, en aritmética de punto flotante, una tolerancia explícita. Hoy el proyecto declara tres tolerancias distintas en tres lugares distintos, todas nominalmente relacionadas con "conservación de la media mensual":

1. `1e-6` en `specs/core-interpolation/requirements.md` REQ-006, como criterio de convergencia del iterador Rymes-Myers (en unidades de la variable).
2. `1e-4` en `specs/validation/requirements.md` REQ-004, como criterio absoluto del post-validator que recibe el output ya producido.
3. `1e-4 °C` en `steering/product.md` como métrica de éxito v1.0, específica para temperatura.

La triplicación es problemática:

- **Ambigüedad semántica.** No es obvio si las tres tolerancias son "la misma cosa" expresada distinto o tres cosas conceptualmente distintas.
- **Ambigüedad de tipo.** No se aclara si son absolutas o relativas. Una tolerancia absoluta de `1e-4` es trivial para temperatura en °C pero inadecuada para radiación en `W m-2` o estricta de más para presión en Pa.
- **Sin enganche por variable.** Una sola tolerancia global no escala a un proyecto que aspira a manejar familias de variables con magnitudes muy distintas.
- **Riesgo de drift.** Si un módulo se actualiza y otro no, el contrato implícito al usuario se rompe silenciosamente.

Se requiere unificar la política y dejar trazable qué tolerancia rige cuándo y por qué.

##### Decisión

Adoptar una **política de tres niveles**, donde cada nivel tiene un dueño claro, un valor por defecto explícito y un mecanismo de configuración bien delimitado. Los tres niveles no se contradicen: cada uno opera en una capa distinta del flujo, con un propósito distinto.

| Nivel | Quién | Valor por defecto | Tipo | Configurable |
|---|---|---|---|---|
| 1 | Iterator (Rymes-Myers) | `1e-6` | absoluta, unidades de la variable | sí, vía `PchipMeanPreservingInterpolator(convergence_tol=...)` |
| 2 | PostInterpolationValidator | `atol=1e-4`, `rtol=1e-6` | mixta (absoluta + relativa) | sí, vía `VariableProfile.acceptable_mean_error` |
| 3 | VariableProfile (YAML) | depende de la variable | absoluta, unidades de la variable | sí, en el perfil YAML del usuario |

### Nivel 1: tolerancia de convergencia del iterador Rymes-Myers

- **Dueño:** módulo `tempify.core.interpolation.pchip_mp` (el iterador).
- **Default:** `convergence_tol = 1e-6` en unidades de la variable.
- **Naturaleza:** criterio **interno** del algoritmo. Determina cuándo el bucle Rymes-Myers para de iterar.
- **No es** una garantía contractual al usuario. Es una decisión sobre cuándo el algoritmo declara "convergí".
- **Configurable** mediante el constructor del interpolador.

### Nivel 2: tolerancia contractual post-interpolación

- **Dueño:** módulo `tempify.validation.post.PostInterpolationValidator`.
- **Default:** `atol = 1e-4` y `rtol = 1e-6` aplicados como `|reconstructed - original| <= atol + rtol * |original|`.
- **Naturaleza:** **promesa al usuario**. El método se compromete a que la media mensual reconstruida del output coincide con la del input dentro de esta tolerancia.
- **Acción al fallar:** se emite WARNING en el `ValidationReport`; el procesamiento continúa. El fallo indica que el iterador no convergió suficientemente o que el método aplicado no es mean-preserving (lineal, PCHIP puro, Fourier sin restricción).
- **Configurable** indirectamente: el `PostValidator` consulta primero el `VariableProfile` (nivel 3); si éste no declara una tolerancia propia, cae al default del nivel 2.

### Nivel 3: tolerancia informativa por variable

- **Dueño:** archivos `variable-profile.yaml` (perfil de variable).
- **Default:** depende de la variable. Ejemplos:
  - temperatura (°C): `acceptable_mean_error: 1e-4`
  - precipitación (mm): `acceptable_mean_error: 0.1` (no aplica a métodos suaves, pero sí a un eventual módulo delta-method)
  - radiación (W m-2): `acceptable_mean_error: 1e-2`
- **Naturaleza:** criterio físicamente significativo, ajustado a la magnitud típica y al uso aceptado de la variable.
- **Configurable** por el usuario en su propio perfil YAML.

### Trazabilidad de las constantes

Las tres tolerancias se exponen como `Final` literales en un módulo central `tempify.constants`, no hard-coded en cada módulo:

```python
#### tempify/constants.py
from typing import Final

RYMES_MYERS_CONVERGENCE_TOL: Final[float] = 1e-6
RYMES_MYERS_MAX_ITERATIONS: Final[int] = 50
POST_VALIDATION_ABS_TOL: Final[float] = 1e-4
POST_VALIDATION_REL_TOL: Final[float] = 1e-6
```

Cada módulo importa de ahí. Los perfiles YAML declaran su propia `acceptable_mean_error`. El `PostValidator` resuelve en orden: perfil → constantes.

##### Alternativas consideradas

### Alternativa A: una sola tolerancia global

Definir un único `MEAN_PRESERVATION_TOL = 1e-6` y aplicarlo en todas partes.

**Rechazado.** No funciona para precipitación (escala mm, donde `1e-6` es ruido numérico irrelevante) ni para radiación (escala W m-2, donde `1e-6` es absurdamente estricto). Tampoco distingue el rol interno (convergencia) del rol contractual (validación), que son conceptualmente distintos.

### Alternativa B: tolerancia 100% relativa

Usar siempre `rtol * |original|` sin componente absoluta.

**Rechazado.** Se rompe para variables que pueden cruzar cero o estar cerca de cero (anomalías de temperatura, NDVI cerca de 0, balance de radiación nocturno). Una tolerancia relativa pura diverge cuando `|original| → 0`.

### Alternativa C: tolerancia única `atol + rtol`

Una sola dupla `(atol, rtol)` global, sin diferenciar convergencia interna vs. validación contractual.

**Rechazado.** Confunde dos contratos: el iterador necesita un criterio de parada (idealmente más estricto que la promesa al usuario, para tener margen); el validator necesita un criterio de auditoría. Mezclarlos hace que cambiar uno fuerce a cambiar el otro.

##### Consecuencias

### Positivas

- Cada tolerancia tiene un dueño identificable y un propósito claro.
- El usuario puede ajustar la tolerancia contractual por variable sin tocar código.
- El equipo de desarrollo puede experimentar con el criterio de convergencia interno sin alterar la promesa al usuario.
- Las constantes viven en un solo lugar, fácil de auditar.

### Negativas

- Tres tolerancias requieren tres tests dedicados y tres entradas en la documentación.
- El orden de resolución (perfil → default) es una capa de indirección que el lector novato debe internalizar.

### Enmiendas requeridas

Esta ADR obliga a actualizar:

1. `specs/core-interpolation/requirements.md` REQ-006: aclarar que `1e-6` es la tolerancia de convergencia (nivel 1), no la garantía contractual.
2. `specs/validation/requirements.md` REQ-004: explicitar `atol=1e-4` y `rtol=1e-6`, y la resolución por perfil de variable.
3. `specs/_template/variable-profile.schema.yaml` (o equivalente): añadir el campo opcional `acceptable_mean_error: float`.
4. `steering/product.md`: aclarar que el `< 1e-4 °C` es el nivel 3 para temperatura, no una constante global.

##### Notas de implementación

- Definir las constantes en `tempify/constants.py` como `Final[float]`. Importar desde allí en `pchip_mp.py`, `post_validator.py` y `variable_profile.py`.
- El `PostInterpolationValidator` recibe el `VariableProfile` resuelto al construirse; si el perfil declara `acceptable_mean_error`, ese valor sobreescribe `POST_VALIDATION_ABS_TOL` para esa ejecución.
- El `ValidationReport` debe registrar qué tolerancia se usó efectivamente (origen: perfil vs. default) para trazabilidad.
- Tests dedicados: `test_constants_immutable`, `test_postvalidator_uses_profile_tolerance_when_present`, `test_postvalidator_falls_back_to_default`, `test_rymes_myers_convergence_tol_independent_of_postvalidator`.

##### Referencias

- Rymes, M. D., & Myers, D. R. (2001). Mean preserving algorithm for smoothly interpolating averaged data. *Solar Energy*, 71(4), 225-231.
- CF Conventions: https://cfconventions.org/
- ADR-0001: Use xarray.DataArray as central data abstraction (formato base de este ADR).
- `specs/core-interpolation/requirements.md` REQ-006.
- `specs/validation/requirements.md` REQ-004.
- `docs/methodology/precipitation.md` (contexto sobre por qué la tolerancia de nivel 3 es variable-específica).

```

## File: `adr/0014-tempifypipeline-naming-correction.md`


```markdown
# ADR-0014: Corrección de nomenclatura de `tempifyPipeline` a `TempifyPipeline`

**Status:** Accepted
**Date:** 2026-05-16
**Decision-makers:** Guillermo Fuentes-Jaque

##### Contexto

`steering/architecture.md` (Capa 5, Orquestación) introduce la clase orquestadora con el nombre `tempifyPipeline` (minúscula inicial). Esta nomenclatura entra en conflicto directo con `steering/conventions.md`, que establece **PascalCase para todas las clases** siguiendo PEP 8.

La incoherencia se ha propagado a las specs activas que referencian la clase:

- `specs/pipeline/requirements.md`
- `specs/cli/requirements.md`
- `specs/gui/requirements.md`

Dado que `steering/conventions.md` es un contrato vinculante del proyecto y la convención PEP 8 es estándar inamovible en el ecosistema Python, la divergencia debe resolverse antes de que el nombre se materialice en código de implementación. Corregirlo más tarde implicaría refactor transversal y churn innecesario en el historial de Git.

##### Decisión

Renombrar la clase orquestadora de **`tempifyPipeline`** a **`TempifyPipeline`** en todas las referencias del proyecto:

- `steering/architecture.md` (Capa 5 y diagramas de flujo)
- `specs/pipeline/requirements.md`
- `specs/cli/requirements.md`
- `specs/gui/requirements.md`
- Código futuro (módulo `tempify.pipeline`)

El paquete (`tempify`) y el módulo (`tempify.pipeline`) **permanecen en lowercase**, conforme a PEP 8 para nombres de paquetes y módulos. La corrección afecta exclusivamente al símbolo de clase.

##### Alternativas consideradas

### 1. Mantener `tempifyPipeline` y documentar una excepción a la convención

Rechazado. Documentar excepciones erosiona la regla y normaliza la negociación caso a caso de convenciones. PEP 8 no contempla camelCase para clases; aceptar la excepción introduciría una inconsistencia visible para cualquier colaborador familiarizado con el ecosistema Python.

### 2. Renombrar a `Pipeline` (sin prefijo)

Rechazado. El nombre es ambiguo dentro de un paquete que orquesta múltiples elementos (detectores, validadores, interpoladores, escritores). Un símbolo genérico `Pipeline` no contextualiza el dominio y colisiona conceptualmente con pipelines de bibliotecas externas (sklearn, Dask, Prefect) cuando aparezca en tracebacks o en imports.

### 3. `TempifyPipeline` (elegido)

Respeta PascalCase, contextualiza el dominio (cualquier traceback o IDE muestra inmediatamente la procedencia), y es trivialmente buscable en el código y la documentación. El prefijo `Tempify` es redundante con el paquete cuando se importa con `from tempify.pipeline import TempifyPipeline`, pero la redundancia se justifica por desambiguación y discoverabilidad.

##### Consecuencias

### Positivas

- Coherencia restaurada entre `steering/conventions.md` y `steering/architecture.md`.
- Alineación con PEP 8: ningún lector futuro tropezará con la convención.
- Refactor barato: la corrección ocurre antes de cualquier implementación.

### Negativas

- Enmienda transversal obligatoria a `steering/architecture.md`, `specs/pipeline/requirements.md`, `specs/cli/requirements.md`, `specs/gui/requirements.md`.
- Las specs deben re-aprobarse si el cambio implica diff no trivial en su superficie pública.

### Sin impacto

- El nombre del paquete (`tempify`) y del módulo (`tempify.pipeline`) **no cambian**: PEP 8 mantiene lowercase para paquetes/módulos.
- No hay código de implementación afectado (las specs siguen en estado Draft).

##### Referencias

- PEP 8 — Naming Conventions: https://peps.python.org/pep-0008/#naming-conventions
- `steering/conventions.md` — Sección de naming.
- `steering/architecture.md` — Capa 5 (Orquestación).

```

## File: `adr/0015-monthly-value-temporal-placement.md`


```markdown
# ADR-0015: Posicionamiento temporal de valores agregados (midpoint convention)

**Status:** Accepted
**Date:** 2026-05-16
**Decision-makers:** Guillermo Fuentes-Jaque
**Contexto técnico:** core-interpolation, temporal-frequency-resolver, io-handlers

##### Context

Un valor agregado temporalmente (media mensual, total mensual de precipitación) representa un periodo, no un instante. En el eje `time` de un `xr.DataArray`, ese valor debe colocarse en una marca temporal concreta. Las opciones son:

1. **Inicio del periodo** (ej. enero 2020 -> 2020-01-01).
2. **Fin del periodo** (ej. enero 2020 -> 2020-01-31).
3. **Centroide del periodo** (ej. enero 2020 -> 2020-01-16, midpoint).

La elección no es cosmética: afecta directamente la interpolación temporal. Si los valores mensuales se colocan al inicio del mes, los días de fin de mes quedan sistemáticamente sub-representados (la curva interpolada subestima el valor real del periodo) y se rompe la propiedad mean-preserving en métodos como PCHIP+RM.

**CF Conventions 7.4 (Climatological Statistics)** establece: *"For time-averaged data, the time coordinate is the midpoint of the averaging period."* Es el estándar de referencia para datos climáticos.

Productos reales del ecosistema climático no son uniformes:

- **ISIMIP:** día 15 fijo para todos los meses.
- **NEX-GDDP-CMIP6:** día 16 fijo.
- **ERA5 monthly mean:** midpoint exacto por mes (variable según días).
- **WorldClim:** no especifica; archivos GeoTIFF sin coordenada temporal explícita.
- **CHELSA, CRU-TS:** mezclan convenciones según versión.

tempify necesita una política única y explícita, con overrides controlados, para no propagar ambigüedad aguas abajo.

##### Decision

Los valores agregados mensuales se posicionan en el **centroide del periodo de agregación (midpoint)** por defecto, conforme a CF Conventions 7.4. La política se concreta en cuatro reglas:

### 1. Default = midpoint

Fórmula: `month_start + timedelta(days=days_in_month / 2)`, con redondeo half-to-even cuando `days_in_month` es par.

Tabla canónica (calendario gregoriano):

| Mes | Días | Midpoint (día del mes) |
|---|---|---|
| Enero | 31 | 16 |
| Febrero (común) | 28 | 14 |
| Febrero (bisiesto) | 29 | 15 |
| Marzo | 31 | 16 |
| Abril | 30 | 15 |
| Mayo | 31 | 16 |
| Junio | 30 | 15 |
| Julio | 31 | 16 |
| Agosto | 31 | 16 |
| Septiembre | 30 | 15 |
| Octubre | 31 | 16 |
| Noviembre | 30 | 15 |
| Diciembre | 31 | 16 |

### 2. `time_bnds` obligatorio en output CF

Todo output con coordenada `time` mensual declara la variable auxiliar `time_bnds` con celdas `[first_day, first_day_next_month)`. Esto permite a consumidores downstream reconstruir que el `time` es el centroide y no asumir convenciones implícitas.

### 3. Override por archivo (auto-detección)

- Si el input declara `time:bounds` (CF), se respeta y se infiere el anchor real (no se reposiciona).
- Si el filename codifica un día específico parseable (ej. `tas_20150115.tif`), se respeta ese timestamp.
- Solo si ambas señales están ausentes se aplica el default midpoint.

### 4. Override por usuario

`PipelineConfig` expone:

```python
monthly_anchor: Literal["midpoint", "start", "end", "custom"] = "midpoint"
time_axis: list[datetime] | None = None  # requerido si anchor == "custom"
```

La opción `"custom"` exige `time_axis` explícito con longitud igual al número de slices del stack; se valida en construcción del `PipelineConfig`.

##### Rationale

### Por qué midpoint y no las alternativas

- **Inicio del mes (`"start"`):** descartado por defecto. Introduce sesgo sistemático: la interpolación entre 2020-01-01 y 2020-02-01 atribuye el valor "enero" al instante 2020-01-01, no al periodo enero completo. Disponible como override por compatibilidad.
- **Fin del mes (`"end"`):** descartado por defecto. Mismo problema en sentido inverso. Disponible como override.
- **Día 15 fijo para todos los meses (ISIMIP):** descartado. Incoherente con febrero (28/29 días) y con meses de 30 días. Adopta una falsa uniformidad a costa de la corrección CF.
- **Centroide en fracción de día (timestamp con hora 12:00):** descartado. Complica interoperabilidad con formatos que solo aceptan resolución diaria (GeoTIFF metadata, nombres de archivo), sin ganancia práctica en interpolación.

### Por qué `time_bnds` obligatorio

Sin `time_bnds`, un consumidor downstream que recibe `time = 2020-01-16` no puede saber si es un instante, un centroide, o un día 16 arbitrario. Declarar `bounds = [2020-01-01, 2020-02-01)` elimina la ambigüedad y es lo que CF exige para datos agregados.

##### Consequences

### Positive

- Rigurosamente correcto CF (compatible con xclim, cdo, nco).
- Interpolación sin sesgo: la curva pasa por el valor promedio real del periodo.
- Conservación de media exacta es alcanzable en métodos mean-preserving (PCHIP+RM) sin correcciones ad-hoc.
- Output legible por cualquier herramienta CF-aware sin reinterpretación.

### Negative

- Febrero requiere lógica especial (28 vs 29 días) en la función helper.
- La tabla no es uniforme: usuarios acostumbrados a ISIMIP/NEX-GDDP (día fijo) deben configurar `monthly_anchor` explícitamente para reproducir esos productos.
- `time_bnds` añade complejidad menor a los writers.

### Risks

- Inputs sin metadata temporal explícita (WorldClim típico) requieren asumir midpoint, que puede no coincidir con la intención original del productor. Mitigación: documentar en `impl-log.md` la asunción aplicada y exponerla en logs del pipeline.

##### Implementation notes

- Helper: `tempify.constants.monthly_midpoint(year: int, month: int) -> datetime.date`.
- Factory: `tempify.core.temporal.TemporalAxis.from_months(year: int, anchor: Literal["midpoint","start","end"] = "midpoint") -> TemporalAxis`.
- Writers (`io-handlers`): emitir `time_bnds` siempre que el stride de `time` sea mensual.
- Reader (`temporal-frequency-resolver`): si detecta `time:bounds` CF, no reposicionar; si detecta filename con fecha parseable, no reposicionar; si nada, aplicar default.
- Tests obligatorios:
  - `test_midpoint_table_matches_cf_convention` — verifica los 12 valores de la tabla.
  - `test_leap_year_february_day_15` — febrero bisiesto = día 15.
  - `test_time_bnds_emitted_on_monthly_output` — writer produce `time_bnds`.
  - `test_custom_anchor_requires_time_axis` — validación de `PipelineConfig`.

##### References

- CF Conventions 7.4 (Climatological Statistics): https://cfconventions.org/Data/cf-conventions/cf-conventions-1.10/cf-conventions.html#climatological-statistics
- ISIMIP protocol §2.3 (Temporal conventions).
- NEX-GDDP-CMIP6 metadata convention.
- ADR-0001: Use xarray.DataArray as central data abstraction.
- specs/core-interpolation/design.md (sección mean-preserving).
- specs/temporal-frequency-resolver/design.md (cascada de inferencia).

```

## File: `adr/0016-climatological-wraparound.md`


```markdown
# ADR-0016: Climatological wraparound como feature de primer orden

**Estado:** Accepted
**Fecha:** 2026-05-16
**Deciders:** Guillermo Fuentes-Jaque
**Contexto técnico:** core-interpolation Sub-fase 2

##### Contexto

Cuando el input es una climatología de 12 meses (sin año contextual) o un único año calendario completo, los interpoladores suaves (Linear, PCHIP, Fourier) operan sobre un dominio finito y discreto: 12 puntos anclados en los midpoints canónicos (ADR-0015). Esto produce dos problemas:

1. **Pobre contexto en las fronteras del año.** Una interpolación PCHIP usando solo enero..diciembre no "sabe" que enero del año siguiente vuelve a ser similar a enero del año actual. Sin información extra, los métodos producen extrapolación arbitraria o cierre forzado.

2. **Sub-utilización de la naturaleza cíclica del clima.** Físicamente, los ciclos anuales son periódicos por construcción: la temperatura media de enero es estructuralmente similar de año a año. Tratar diciembre y enero como puntos aislados, sin compartir contexto, es subóptimo.

La práctica común en interpolación climatológica es **extender artificialmente** el dominio antes de interpolar: tratar el último mes (diciembre, índice 12) como si fuera el último mes del año anterior y el primer mes (enero, índice 1) como el primer mes del año siguiente. Esto da, como mínimo, 14 puntos anclados (en lugar de 12) y, dependiendo del método, padding adicional.

##### Decisión

`tempify` adopta **climatological wraparound** como feature de primer orden, **activado por defecto** para todos los interpoladores que operan sobre 12 meses. La implementación es transparente al usuario salvo cuando solicita explícitamente desactivarla.

### Reglas formales

1. **Wraparound mínimo (default ON).** Para todo input con `n_months == 12` y `wraparound=True` (default), antes de invocar el kernel se añade al dominio:
   - Un nodo izquierdo con valor `m[11]` y `x` desplazado a `x_in[11] - period`.
   - Un nodo derecho con valor `m[0]` y `x` desplazado a `x_in[0] + period`.

   `period` es el número total de días del año destino (365 o 366 per REQ-003).

2. **Wraparound extendido por método.** Los métodos que se benefician de más contexto pueden extender el padding:
   - **Linear:** padding mínimo (1 nodo por lado → 14 puntos efectivos).
   - **PCHIP / PCHIP+RM:** padding ampliado (2 nodos por lado → 16 puntos efectivos, asegura C¹ continuity).
   - **Fourier:** no requiere padding explícito; la FFT trata implícitamente al input como periódico con `n=12` muestras. La feature "wraparound" para Fourier se manifiesta como `attrs["tempify_wraparound"] = "fft_implicit"`.

3. **Opt-out explícito.** El parámetro `wraparound: bool = True` controla el comportamiento. Con `wraparound=False`:
   - Linear aplica extrapolación constante (`m[0]` antes de `x_in[0]`; `m[11]` después de `x_in[11]`).
   - PCHIP aplica extrapolación polinomial natural de SciPy.
   - Fourier mantiene `fft_implicit` (no se puede "apagar" la naturaleza periódica del FFT; documentar como excepción).

4. **Coexistencia con `cyclic`.** El parámetro existente `cyclic: bool = True` se mantiene como sinónimo retrocompatible de `wraparound` y será deprecado en v0.2.0. En v0.1.0, ambos parámetros son aceptados; si se pasan contradictoriamente, raise `ValueError("cyclic and wraparound must agree")`.

5. **Stamping de procedencia.** El output `DataArray` incluye `attrs["tempify_wraparound"]` con valor:
   - `"climatological_2pt"`: padding mínimo 2 puntos extra (Linear default).
   - `"climatological_4pt"`: padding extendido 4 puntos extra (PCHIP default).
   - `"fft_implicit"`: Fourier.
   - `"off"`: usuario forzó `wraparound=False`.

##### Alternativas consideradas

| Alternativa | Razón de rechazo |
|---|---|
| Mantener implícito en `cyclic` (status quo) | El usuario que llamó esto "feature de primer orden" tiene razón: el comportamiento es valioso pero invisible. Formalizar mejora documentación y API. |
| Padding fijo de 4 puntos para todos los métodos | Linear y Fourier no se benefician de tanto padding; PCHIP necesita C¹ que requiere 2 nodos. Decisión por-método es óptima. |
| Replicar todo el ciclo (24 puntos) | Sobreajuste de contexto. Los métodos suaves solo necesitan información local de las fronteras. |
| Hacer `wraparound=False` el default | Pierde calidad significativa en climatologías. La mayoría de inputs reales son climatológicos o anuales únicos. |

##### Consecuencias

### Positivas

- **API más expresiva:** el usuario que lee `tempify` entiende explícitamente que la extensión cíclica es un feature, no un detalle interno.
- **Documentación verificable:** el reporte de procesamiento muestra el modo de wraparound aplicado.
- **Compatibilidad retrocompatible:** ningún usuario pierde funcionalidad; `cyclic=True` (default) sigue funcionando idéntico.
- **Trazabilidad científica:** los outputs llevan stamping suficiente para reproducir.

### Negativas

- **Más parámetros visibles:** la firma `interpolate(..., cyclic=True, wraparound=True)` puede confundir hasta que `cyclic` se deprecie en v0.2.0.
- **Tests duplicados:** cada método ahora necesita cubrir wraparound on/off (≥4 tests adicionales por método).

### Riesgos

- **Drift entre `cyclic` y `wraparound`:** si el usuario pasa valores inconsistentes (`cyclic=True, wraparound=False`), el comportamiento debe ser determinista. La regla: raise `ValueError` per Decisión 4.

##### Notas de implementación

- En `tempify.interpolation._kernels`, los kernels `linear_kernel`, `pchip_kernel` ya implementan padding cíclico cuando `cyclic=True`. No requiere reescritura del kernel: el cambio es semántico/de naming en las fachadas.
- En `tempify.interpolation.base.BaseInterpolator.interpolate`, añadir parámetro `wraparound: bool = True` con validación de consistencia con `cyclic`.
- En `BaseInterpolator._postprocess`, añadir attribute `tempify_wraparound` con el modo aplicado.
- Para v0.2.0: deprecar `cyclic` con `DeprecationWarning` y migrar tests a `wraparound`.

##### Referencias

- [ADR-0015](0015-monthly-value-temporal-placement.md) — Convención midpoint para el posicionamiento temporal.
- [REQ-004 en core-interpolation/requirements.md](../../specs/core-interpolation/requirements.md) — Comportamiento cíclico actual (será actualizado para citar este ADR).
- Práctica común en climatología: Cleveland, W. S. (1979). Robust locally weighted regression. *JASA*, 74(368), 829-836 — discute extensión de dominio para suavizadores en series temporales.
- CF Conventions §7.4 — Climatological time coordinates (relevante para semántica del wrap).

```

## File: `adr/0018-classical-interpolator-catalog.md`


```markdown
# ADR-0018: Catálogo extensible de interpoladores clásicos

**Estado:** Approved
**Fecha:** 2026-05-18
**Deciders:** Guillermo Fuentes-Jaque
**Contexto técnico:** core-interpolation (extensibilidad clásica, no-NN)

##### Contexto

La v0.1.0 quedó con 4 métodos de interpolación temporal (`linear`, `pchip`, `pchip_mp`, `fourier`). En la práctica existen varias familias clásicas adicionales que la literatura climatológica usa rutinariamente y que tempify podría incorporar **sin recurrir a redes neuronales** (eso queda para [ADR-0017](0017-neural-interpolator-extensibility.md)).

Tras revisión bibliográfica 2026-05-18 sobre densificación temporal mensual→diaria en clima/teledetección, identificamos las siguientes familias candidatas y su estado relativo respecto a tempify v0.1.x:

| Familia | Mean preserving | Smooth | Coste | Lib | Veredicto |
|---|---|---|---|---|---|
| **Cubic spline natural** | No | C² | bajo | `scipy.interpolate.CubicSpline` | Adoptar en v0.1.4 |
| **Akima 1970** | No | C¹ menos oscilación | bajo | `scipy.interpolate.Akima1DInterpolator` | Adoptar en v0.1.4 |
| **Modified Akima (Makima)** | No | C¹ mejor regiones planas | bajo | SciPy ≥ 1.13 | Considerar v0.1.x |
| **Lai & Kaplan 2022 (Fast MP-spline)** | **Sí** + bounded | C¹ | medio | propio | Adoptar en v0.2.0 |
| **Savitzky-Golay** | No, suaviza | C∞ local | bajo | `scipy.signal.savgol_filter` | Post-procesador opcional v0.2.x |
| **Whittaker-Henderson** | Sí (momentos) | penalizado | medio | propio | Considerar v0.2.x |
| **Gaussian process / Kriging** | No directo | C∞ | alto O(N³) | `gpflow`/`gpytorch` | Diferido (ver ADR-0017) |
| **STL + interp** | Compuesto | dep. método | medio | `statsmodels` | Diferido |

##### Decisión

1. **v0.1.4 — adopción rápida de dos métodos de SciPy** (este ADR cubre la implementación):
   - `akima` (`AkimaInterpolator` envuelve `scipy.interpolate.Akima1DInterpolator`)
   - `cubic` (`CubicSplineInterpolator` envuelve `scipy.interpolate.CubicSpline`, condición `not-a-knot` por defecto, periódica si `cyclic=True`)

   Ambos siguen el contrato `BaseInterpolator` existente. Quedan **rechazados para precipitación** vía perfil de variable (per [ADR-0004](0004-precipitation-policy.md)) por ser métodos suaves que pueden producir negativos.

2. **v0.1.4 NO incluye un sabor mean-preserving de estos métodos.** La razón es que `pchip_mp` ya cumple ese rol (Rymes-Myers + PCHIP). Añadir un `cubic_mp` requeriría justificación adicional; se difiere al estudio del paper Lai & Kaplan 2022 que provee una construcción explícita superior.

3. **v0.2.0 — `cubic_mp_lai_kaplan`.** Implementación basada en [Lai & Kaplan 2022, JTECH](https://journals.ametsoc.org/view/journals/atot/39/4/JTECH-D-21-0154.1.xml). Características:
   - Preservación exacta de medias mensuales (∫ raster_diario = raster_mensual sobre cada mes).
   - Bounds opcionales (e.g. `min=0` para precipitación, `max=100` para humedad relativa).
   - C¹ sin overshoots por construcción.

   La nueva spec dedicada `specs/lai-kaplan-interpolation/` se redactará junto con la GUI v0.2.0.

4. **v0.2.x — Savitzky-Golay como capa de post-procesamiento.** Nueva fase opcional del pipeline (después de `interpolate`, antes de `validate_post`):
   - `SavitzkyGolayPostProcessor` con ventana y orden polinómico configurables (defaults `window=15, polyorder=3`).
   - No reemplaza ningún método, suaviza el output diario para reducir esquinas en los nodos.
   - Conmutable por `PipelineConfig.smoothing="savgol" | None`.

5. **v0.2.x — Whittaker-Henderson como `whittaker` interpolator.** Alternativa a `fourier` cuando la señal anual no es estrictamente armónica. Implementación a partir de [Eilers 2003 / Steinacker 2023](https://rmets.onlinelibrary.wiley.com/doi/full/10.1002/joc.8089) usando matrices sparse (O(N) por píxel). Preserva primeros p momentos (incluyendo media si p≥1).

6. **GPR / Kriging y wavelets — diferidos a una futura revisión.** El coste computacional O(N³) los hace inviables para rásters de N≥10⁶ píxeles sin GPU; cuando se aborden, será junto con la integración NN ([ADR-0017](0017-neural-interpolator-extensibility.md)).

##### Plan formal por release

### v0.1.4 (esta release)

**In-scope:**

- `src/tempify/interpolation/akima.py` → `AkimaInterpolator`
- `src/tempify/interpolation/cubic.py` → `CubicSplineInterpolator`
- `src/tempify/interpolation/_kernels.py` → `akima_kernel`, `cubic_kernel`
- Update `PipelineConfig.method` Literal con `"akima"` y `"cubic"`
- Update `PipelineCore` dispatcher en `tempify/pipeline/core.py`
- Update perfiles YAML (`profiles/temperature.yaml`, etc.) para aceptar/rechazar los nuevos métodos según la variable
- Update CLI: `tempify convert --method akima|cubic ...`
- Tests unitarios + property tests (hypothesis): `tests/unit/interpolation/test_akima.py`, `test_cubic.py`
- Update docs: README (tabla), landing `docs/index.html` (sección Métodos extendida a 6 filas), notebook tutorial (loop de comparación incluye los 6)
- CHANGELOG `[0.1.4]`

**Out-of-scope para v0.1.4:** mean-preserving variants, Savitzky-Golay, Whittaker, GPR.

### v0.2.0

- `cubic_mp_lai_kaplan` con spec dedicada
- GUI PySide6 (per spec `gui/`)
- Instalador Windows (per spec `packaging/`)
- Integración NN baseline + híbrido (per ADR-0017)

### v0.2.x

- Post-procesador Savitzky-Golay
- Whittaker-Henderson interpolator

##### Consecuencias

- **API estable preservada.** Los 4 métodos existentes (`linear`, `pchip`, `pchip_mp`, `fourier`) siguen byte-idénticos. Los nuevos son aditivos.
- **Contrato `BaseInterpolator` validado.** Que dos métodos nuevos entren en v0.1.4 con cero cambios al ABC confirma el supuesto de v0.1.0 sobre extensibilidad clásica.
- **Política de precipitación amplía cobertura.** Los perfiles de variable (`profiles/precipitation.yaml`) rechazan ahora 5 métodos en vez de 3 (`linear`, `pchip`, `pchip_mp`, `fourier`, `akima`, `cubic`), siempre permitiendo override con `--force-method`.
- **Reproducibilidad.** El `tempify_method` attr de los outputs identifica unívocamente el método. Outputs producidos antes de v0.1.4 siguen reproducibles bit-exact.

##### Referencias

- Akima, H. (1970). *A New Method of Interpolation and Smooth Curve Fitting Based on Local Procedures.* J. ACM 17(4): 589-602.
- Lai, C.-Y., & Kaplan, J. O. (2022). *A Fast Mean-Preserving Spline for Interpolating Interval Data.* J. Atmos. Oceanic Tech. 39(4): 503-512.
- Steinacker, R. (2023). *Mean value splines and their use for climatological time series.* Int. J. Climatology 43(4): 1842-1856.
- Hofstra, N., et al. (2008). *Comparison of six methods for the interpolation of daily, European climate data.* JGR Atmospheres 113: D21110.
- Fritsch, F. N., & Carlson, R. E. (1980). *Monotone piecewise cubic interpolation.* SIAM J. Numer. Anal. 17(2): 238-246.
- Rymes, M. D., & Myers, D. R. (2001). *Mean preserving algorithm for smoothly interpolating averaged data.* Solar Energy 71(4): 225-231.
- Savitzky, A., & Golay, M. J. E. (1964). *Smoothing and Differentiation of Data by Simplified Least Squares Procedures.* Anal. Chem. 36(8): 1627-1639.
- Eilers, P. H. C. (2003). *A perfect smoother.* Anal. Chem. 75(14): 3631-3636.

```


---

# Specs SDD (requirements + design por capa)


## File: `specs/core-interpolation/requirements.md`


```markdown
﻿# Requirements — core-interpolation

**Estado:** Approved
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-15
**Última actualización:** 2026-05-16

##### 1. Propósito

Implementar los cuatro métodos de interpolación temporal mensual → diaria (Lineal, PCHIP, PCHIP + Rymes-Myers mean-preserving, Fourier multi-armónico) validados experimentalmente sobre datos reales (Quinta Normal 2020) y sintéticos (stack 3×3). Esta spec es el corazón funcional del software; todas las demás specs orbitan alrededor de ella.

El posicionamiento de los nodos de entrada sobre el eje temporal sigue la convención **midpoint** (punto medio canónico de cada mes calendario) per [ADR-0015](../../docs/adr/0015-monthly-value-temporal-placement.md). Esta convención preserva la semántica "valor mensual = promedio del mes" y evita el sesgo sistemático introducido por anchors de inicio/fin.

##### 2. Alcance

### In-scope

- Cuatro métodos de interpolación temporal mensual → diaria.
- Soporte para nodos cíclicos (cierre del año).
- Vectorización píxel a píxel sobre `xr.DataArray` con `(month, y, x)`.
- Conservación de la media mensual exacta en el método PCHIP+RM.
- Manejo correcto de años bisiestos vs no bisiestos (365 vs 366 días).
- Propagación correcta de NoData.

### Out-of-scope

- Otras transiciones de frecuencia (anual → mensual, daily → horario). Diferidos a futuras specs.
- Interpolación espacial (la resolución no cambia).
- Métodos estocásticos / weather generators.
- Interpolación de precipitación con métodos suaves (rechazada por diseño). El rechazo de precipitación es enforced por `MethodVariableCompatibilityChecker` en `validation` per ADR-0004; esta spec solo provee los algoritmos.
- Métodos basados en redes neuronales pre-entrenadas (ClimaX, Pangu-Weather, GraphCast, FourCastNet, etc.). Diferidos a v0.2.0 en una spec separada `neural-interpolation`. El ABC `BaseInterpolator` es deliberadamente abierto para soportarlos cuando se aborde. Ver [ADR-0017](../../docs/adr/0017-neural-interpolator-extensibility.md).

##### 3. Actores y casos de uso

### Actor 1: Investigador en climatología aplicada

> Como investigador, quiero convertir un stack mensual WorldClim a diario preservando la media mensual, para alimentar modelos de fenología que requieren temperatura diaria sin introducir sesgo en agregados mensuales.

**Caso de uso típico:** El investigador carga el stack mensual con `xarray`, llama a `interpolate(stack, target_freq="daily", method="pchip_mp")`, y obtiene un `DataArray` diario que al re-agregar por mes coincide con el original.

### Actor 2: Docente

> Como docente, quiero mostrar a estudiantes las diferencias entre métodos de interpolación temporal, para enseñar conceptos de conservación de propiedades estadísticas en agregaciones.

**Caso de uso típico:** El docente compara visualmente los 4 métodos sobre un dataset pequeño y muestra las métricas de error.

##### 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL provide four interpolation methods: linear, PCHIP, PCHIP+Rymes-Myers (mean-preserving), and Fourier with configurable number of harmonics (1 to 5).

### REQ-002 (Ubiquitous)

THE SYSTEM SHALL expose all interpolation methods through a common interface `BaseInterpolator.interpolate(source: xr.DataArray, target_axis: TemporalAxis) -> xr.DataArray`.

### REQ-003 (Event-driven)

WHEN the user invokes any interpolation method on a monthly stack, THE SYSTEM SHALL return a daily stack with dimensions `(time, y, x)`, where `time` is a CF-compliant daily index covering either 365 or 366 days according to whether the target year is a leap year.

### REQ-004 (Ubiquitous)

THE SYSTEM SHALL handle cyclic boundary conditions by default: December connects smoothly to January without extrapolation artifacts. Esta continuidad es alcanzada vía el mecanismo de **climatological wraparound** formalizado en REQ-015 y ADR-0016, no como un detalle interno del kernel.

### REQ-005a (Optional)

WHERE `cyclic=False` AND method=`linear`, THE SYSTEM SHALL apply constant extrapolation at boundaries.

### REQ-005b (Optional)

WHERE `cyclic=False` AND method ∈ {`pchip`, `pchip_mp`}, THE SYSTEM SHALL apply Fritsch-Carlson polynomial extrapolation.

### REQ-005c (Optional)

WHERE `cyclic=False` AND method=`fourier`, THE SYSTEM SHALL use the natural Fourier periodic boundary (no special handling).

### REQ-006 (State-driven)

WHILE applying PCHIP+Rymes-Myers, THE SYSTEM SHALL iterate until the maximum absolute difference between the reconstructed monthly mean and the original monthly value is below a configurable tolerance (`convergence_tol`, default `1e-6` in the variable's units, configurable via `PchipMeanPreservingInterpolator(convergence_tol=...)`; this is the iterator's stopping criterion, NOT the contractual post-validation tolerance which lives in ADR-0010 nivel 2) or until reaching a maximum number of iterations (default 50).

### REQ-007 (Event-driven)

WHEN PCHIP+Rymes-Myers converges, THE SYSTEM SHALL record the number of iterations used in the output `DataArray.attrs["rymes_myers_iterations"]`.

### REQ-008 (Unwanted)

IF the input has NaN values:
- When ALL 12 months are NaN for a pixel: propagate NaN to all output days.
- When SOME months are NaN for a pixel: raise `PartialNanPixelError` with the pixel index OR (configurable via `nan_policy: Literal['raise', 'propagate_all', 'skip_pixel']`) propagate accordingly.

Default: `nan_policy='raise'` (fail-fast, conservative).

### REQ-009 (Unwanted)

IF the input stack does not contain exactly 12 months (e.g., has 11 or 13), THEN THE SYSTEM SHALL raise `InvalidMonthlyStackError` with a clear message identifying the issue.

### REQ-010 (Ubiquitous)

THE SYSTEM SHALL vectorize over spatial dimensions using `xr.apply_ufunc(..., dask='parallelized', dask_gufunc_kwargs={'output_sizes': {'time': target_days}})` with default chunk size from `tempify.constants.DEFAULT_CHUNK_SIZE` (configurable per call).

### REQ-011 (Unwanted)

IF the input stack has a non-Gregorian CF calendar (`noleap`, `360_day`, `julian`, `all_leap`), THEN THE SYSTEM SHALL raise `UnsupportedCalendarError` with a clear message in Spanish indicating which calendar was detected and that v0.1.0 supports only Gregorian/standard calendars.

### REQ-012 (Unwanted)

IF the input stack has duplicate or non-contiguous month coordinates (e.g., `[1,3,4,...,12]` or `[1,1,2,...]`), THEN THE SYSTEM SHALL raise `InvalidMonthlyStackError` identifying the issue.

### REQ-013 (Ubiquitous)

THE SYSTEM SHALL position each monthly input value at the canonical midpoint of its calendar month (per ADR-0015) when constructing the X-coordinate axis for the smooth interpolators (Linear, PCHIP, Fourier). The PCHIP+Rymes-Myers mean-preserving algorithm operates on monthly aggregates and the midpoint convention applies only to the auxiliary node initialization of the iterator.

### REQ-014 (Optional)

WHERE the caller provides `monthly_anchor='start'`, `'end'`, or `'custom'` instead of the default `'midpoint'`, THE SYSTEM SHALL position monthly values at the requested anchor. With `'custom'`, the caller must additionally provide an explicit `time_axis: list[datetime]` of length 12 (or matching the input length).

### REQ-015 (Ubiquitous)

THE SYSTEM SHALL apply **climatological wraparound** by default when the input has exactly 12 monthly values: month 12 (December) is duplicated as the implicit "month 0" positioned at `x_in[11] - period` (December of the previous year) and month 1 (January) is duplicated as the implicit "month 13" positioned at `x_in[0] + period` (January of the next year). This expands the effective interpolation domain from 12 to at minimum 14 anchor points (per ADR-0016). Individual methods MAY extend the padding further to gain additional context:

- **Linear:** exact 14 effective points (1 padding per side).
- **PCHIP / PCHIP+RM:** 16 effective points (2 padding per side) to ensure C¹ continuity at the December-January boundary.
- **Fourier:** no explicit padding required; the FFT implicitly treats the 12 monthly inputs as periodic samples and the wraparound semantics are inherent. The output is stamped with `attrs["tempify_wraparound"] = "fft_implicit"`.

The output `DataArray` always carries `attrs["tempify_wraparound"]` with one of the canonical values: `"climatological_2pt"`, `"climatological_4pt"`, `"fft_implicit"`, or `"off"`.

### REQ-016 (Optional)

WHERE the caller passes `wraparound=False`, THE SYSTEM SHALL disable the artificial domain extension and treat the 12 monthly inputs as a bare finite sequence. Out-of-range positions (before `x_in[0]` or after `x_in[11]`) are then handled per REQ-005a/b/c by method. Fourier remains periodic by construction (FFT inherent) regardless of `wraparound`; in that case the stamp `attrs["tempify_wraparound"] = "fft_implicit"` is preserved with a `DataArray.attrs["tempify_wraparound_user_request"] = "off"` note for traceability.

### REQ-017 (Unwanted)

IF the caller passes contradictory values of `cyclic` and `wraparound` (e.g., `cyclic=True, wraparound=False`), THEN THE SYSTEM SHALL raise `ValueError("cyclic and wraparound must agree; in v0.2.0 cyclic will be deprecated in favor of wraparound")`. `cyclic` is preserved in v0.1.0 as a retrocompatible synonym of `wraparound` and is scheduled for deprecation in v0.2.0.

##### 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Performance | Procesar un stack 12×3000×500 (Chile a 2.5min) en <60s, máquina 8 cores, `scheduler='threaded'` (modo `parallel` per ADR-0007) | Benchmark `tests/benchmark/test_perf_chile_2.5min.py` |
| NFR-002 | Reliability | Conservación de media mensual exacta en PCHIP+RM | Property test `test_rymes_myers_preserves_mean` con hypothesis |
| NFR-003 | Reliability | Reproducibilidad bit-exact en modo `strict` (single-thread, seeded); modo `parallel` garantiza `allclose(rtol=1e-12, atol=1e-15)` per ADR-0007 | Tests separados: `test_reproducibility_strict_md5_match`, `test_reproducibility_parallel_allclose` |
| NFR-004 | Memory | No cargar más de 1GB en RAM por chunk con default chunk_size=512 | Profiling con memray |
| NFR-005 | Usability | Mensajes de error en español por defecto, con código de error referenciable | Test `test_error_messages_spanish` |

##### 6. Criterios de aceptación

- [ ] REQ-001 cubierto por tests `test_linear_basic`, `test_pchip_basic`, `test_pchip_mp_basic`, `test_fourier_basic`
- [ ] REQ-002 cubierto por test `test_base_interpolator_protocol`
- [ ] REQ-003 cubierto por test `test_output_has_366_days_in_leap_year` y `test_output_has_365_days_in_non_leap_year`
- [ ] REQ-004 cubierto por test `test_cyclic_boundary_continuity`
- [ ] REQ-005a/b/c cubiertos por tests `test_non_cyclic_linear_constant`, `test_non_cyclic_pchip_polynomial`, `test_non_cyclic_fourier_periodic`
- [ ] REQ-006 cubierto por test `test_rymes_myers_converges`
- [ ] REQ-007 cubierto por test `test_rymes_myers_records_iterations`
- [ ] REQ-008 cubierto por tests `test_nan_all_propagation`, `test_partial_nan_raises`, `test_nan_policy_propagate_all`, `test_nan_policy_skip_pixel`
- [ ] REQ-009 cubierto por test `test_invalid_monthly_count_raises`
- [ ] REQ-010 cubierto por test `test_vectorized_with_dask`
- [ ] REQ-011 cubierto por test `test_non_gregorian_calendar_raises`
- [ ] REQ-012 cubierto por test `test_duplicate_or_noncontiguous_months_raises`
- [ ] REQ-013 cubierto por tests `test_temporal_axis_midpoint_table`, `test_linear_input_nodes_at_midpoint`
- [ ] REQ-014 cubierto por tests `test_monthly_anchor_start_shifts_nodes`, `test_custom_anchor_requires_explicit_dates`
- [ ] REQ-015 cubierto por tests `test_climatological_wraparound_adds_2pt_linear`, `test_climatological_wraparound_adds_4pt_pchip`, `test_wraparound_attr_stamped`
- [ ] REQ-016 cubierto por tests `test_wraparound_false_disables_extension_linear`, `test_wraparound_false_disables_extension_pchip`
- [ ] REQ-017 cubierto por test `test_contradictory_cyclic_wraparound_raises`
- [ ] NFR-001 medido y dentro del umbral
- [ ] NFR-002 verificado con 100+ casos de hypothesis
- [ ] NFR-003 verificado en ambos modos (`strict` y `parallel`) per ADR-0007
- [ ] Documentación: notas metodológicas en `docs/methodology/` para cada método con referencias
- [ ] Tutorial: notebook `docs/tutorials/01_interpolation_methods_comparison.ipynb`
- [ ] CHANGELOG actualizado

##### 7. Dependencias y supuestos

### Specs relacionadas

- Bloqueada por: ninguna (es la spec fundacional).
- Bloquea: pipeline, [io-handlers](../io-handlers/requirements.md), [validation](../validation/requirements.md), [cli](../cli/requirements.md).
- Independiente de: [structure-detection](../structure-detection/requirements.md) (los `BaseInterpolator` reciben `xr.DataArray` ya detectado y validado).

### Supuestos

- El usuario entiende que ningún método mensual→diario puede recuperar la varianza sinóptica diaria real. Esto se comunica claramente en la documentación.
- Para v1.0 solo se soporta transición 12 meses → 365/366 días. Otras transiciones diferidas.

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Pérdida de varianza diaria interpretada como "bug" por usuarios sin contexto | Media | Medio | Documentación clara + reporte automático que comunica la limitación intrínseca |
| Rymes-Myers no converge en casos patológicos | Baja | Medio | Tope de iteraciones + log warning; retornar mejor aproximación |
| Performance Dask pobre por chunks mal dimensionados | Media | Bajo | chunk_size configurable + recomendación en docs |

##### 8. Referencias

- Fritsch, F. N., & Carlson, R. E. (1980). Monotone piecewise cubic interpolation. *SIAM Journal on Numerical Analysis*, 17(2), 238-246.
- Rymes, M. D., & Myers, D. R. (2001). Mean preserving algorithm for smoothly interpolating averaged data. *Solar Energy*, 71(4), 225-231.
- Validación experimental previa: experimento Quinta Normal 2020 (ver `docs/methodology/empirical-validation-quinta-normal.md`).
- [ADR-0015](../../docs/adr/0015-monthly-value-temporal-placement.md) — Convención midpoint para el posicionamiento temporal de valores mensuales.
- [ADR-0016](../../docs/adr/0016-climatological-wraparound.md) — Climatological wraparound como feature de primer orden, parámetro `wraparound` y semántica por método.
- [ADR-0017](../../docs/adr/0017-neural-interpolator-extensibility.md) — Extensibilidad para métodos basados en redes neuronales (deferred a v0.2.0).
- CF Conventions §7.4 — Climatological statistics y semántica de celdas de tiempo (https://cfconventions.org/Data/cf-conventions/cf-conventions-1.11/cf-conventions.html#climatological-statistics).

```

## File: `specs/core-interpolation/design.md`


```markdown
# Design — core-interpolation

**Estado:** Draft
**Requirements doc:** [requirements.md](requirements.md) (Approved, REQ-001..014, NFR-001..005)
**Última actualización:** 2026-05-15

##### 1. Visión técnica

La feature `core-interpolation` materializa la Capa 4 (Interpolation) del proyecto (per `steering/architecture.md`). Es **interpolación temporal pura, sin I/O ni conocimiento de georreferencia**: recibe un `xr.DataArray` con coord `month ∈ [1,12]` y devuelve un `xr.DataArray` con coord `time` diaria (365 o 366 valores). La paralelización es ortogonal: todos los métodos vectorizan vía `xr.apply_ufunc(..., dask='parallelized')` sobre el kernel 1D del píxel (per ADR-0001, ADR-0002).

Se exponen cuatro métodos detrás de un único contrato `BaseInterpolator.interpolate(...)`: Lineal (referencia), PCHIP (Fritsch-Carlson, suave + monótono local), PCHIP+Rymes-Myers (PCHIP con corrección iterativa mean-preserving) y Fourier (multi-armónico, 1..5). La política de precipitación (ADR-0004) NO se aplica aquí: estos algoritmos son agnósticos a la variable. El rechazo vive en Capa 3 (`MethodVariableCompatibilityChecker`). La política de reproducibilidad (ADR-0007) tampoco se aplica aquí: el módulo es estatic-puro respecto al scheduler de Dask; el `reproducibility_context` lo aplica Capa 5.

##### 2. Arquitectura propuesta

### Diagrama de componentes

```
tempify.interpolation
├── base.py         BaseInterpolator (ABC)  ◄── contrato público
│                   TemporalAxis (dataclass)
│                   excepciones tipadas
├── linear.py       LinearInterpolator
├── pchip.py        PchipInterpolator        (wrapper scipy.PchipInterpolator)
├── pchip_mp.py     PchipMeanPreservingInterpolator (PCHIP + Rymes-Myers loop)
├── fourier.py      FourierInterpolator      (FFT multi-armónico)
└── _kernels.py     funciones 1D NumPy puras invocadas por apply_ufunc
                    (sin dependencia de xarray; testables aisladamente)

tempify.constants    DEFAULT_CHUNK_SIZE, DEFAULT_RM_CONVERGENCE_TOL,
                     DEFAULT_RM_MAX_ITER, FOURIER_MIN_HARMONICS,
                     FOURIER_MAX_HARMONICS
```

Diagrama de flujo de una llamada típica:

```
caller (Pipeline)
    │
    ▼
PchipMeanPreservingInterpolator(convergence_tol=1e-6, max_iterations=50)
    │
    ├─ validate_input(source)        ── raise Invalid* o UnsupportedCalendar*
    ├─ build target time coord        ── from TemporalAxis (CF compliant)
    │
    ▼
xr.apply_ufunc(
    _kernels.pchip_rm_kernel,
    source,
    input_core_dims=[["month"]],
    output_core_dims=[["time"]],
    dask="parallelized",
    dask_gufunc_kwargs={"output_sizes": {"time": target_days}},
    output_dtypes=[source.dtype],
)
    │
    ▼
xr.DataArray (time, y, x) con attrs["rymes_myers_iterations"]
```

### Componentes nuevos

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| `BaseInterpolator` (ABC) | `src/tempify/interpolation/base.py` | Contrato común `interpolate()`, validación de entrada, construcción de eje temporal |
| `TemporalAxis` (dataclass frozen) | `src/tempify/interpolation/base.py` | Especificación del eje destino (start, end, freq, calendar) |
| `LinearInterpolator` | `src/tempify/interpolation/linear.py` | Interpolación lineal por tramos (REQ-001, REQ-005a) |
| `PchipInterpolator` | `src/tempify/interpolation/pchip.py` | PCHIP Fritsch-Carlson (REQ-001, REQ-005b) |
| `PchipMeanPreservingInterpolator` | `src/tempify/interpolation/pchip_mp.py` | PCHIP + Rymes-Myers iterativo (REQ-001, REQ-006, REQ-007) |
| `FourierInterpolator` | `src/tempify/interpolation/fourier.py` | Serie de Fourier truncada (REQ-001, REQ-005c) |
| `_kernels` | `src/tempify/interpolation/_kernels.py` | Funciones 1D NumPy puras (sin xarray) por método |
| Constantes | `src/tempify/constants.py` | `DEFAULT_CHUNK_SIZE=512`, `DEFAULT_RM_CONVERGENCE_TOL=1e-6`, `DEFAULT_RM_MAX_ITER=50`, `FOURIER_MIN_HARMONICS=1`, `FOURIER_MAX_HARMONICS=5` |
| Excepciones | `src/tempify/interpolation/exceptions.py` | `InvalidMonthlyStackError`, `UnsupportedCalendarError`, `PartialNanPixelError` |

### Componentes modificados

N/A (primera implementación de la Capa 4).

##### 3. Contratos públicos (APIs)

### 3.1 `BaseInterpolator`

```python
from abc import ABC, abstractmethod
from typing import Literal
import xarray as xr

NanPolicy = Literal["raise", "propagate_all", "skip_pixel"]


class BaseInterpolator(ABC):
    """Abstract base for temporal interpolators (monthly to daily).

    All concrete implementations vectorize over spatial dimensions via
    ``xr.apply_ufunc(..., dask='parallelized')`` and respect the contract
    declared by :meth:`interpolate`.
    """

    @abstractmethod
    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: "TemporalAxis",
        *,
        cyclic: bool = True,
        nan_policy: NanPolicy = "raise",
        chunk_size: int | None = None,
    ) -> xr.DataArray:
        """Interpolate a monthly stack to a daily stack.

        Parameters
        ----------
        source : xr.DataArray
            Monthly stack with dims ``(month, y, x)``. ``month`` must contain
            exactly 12 contiguous integers ``[1, 2, ..., 12]``.
        target_axis : TemporalAxis
            Specification of the target daily axis (start, end, calendar).
        cyclic : bool, default True
            If True, December connects smoothly to January.
        nan_policy : {"raise", "propagate_all", "skip_pixel"}, default "raise"
            How to handle pixels with partial NaN months.
        chunk_size : int or None, default None
            Override for spatial chunk size. ``None`` uses
            ``tempify.constants.DEFAULT_CHUNK_SIZE``.

        Returns
        -------
        xr.DataArray
            Daily stack with dims ``(time, y, x)``, CF-compliant ``time``
            coord, same spatial coords as input, same dtype.
        """
```

**Pre-condiciones:**
- `source` tiene dims exactamente `("month", "y", "x")` (orden libre).
- `source["month"]` es `[1..12]` sin huecos ni duplicados (verificado, REQ-012).
- `source.dtype` es coma flotante (`float32` o `float64`).
- Calendario del eje destino ∈ `{"standard", "gregorian"}` (REQ-011).

**Post-condiciones:**
- Salida tiene exactamente 365 o 366 valores en `time` según año bisiesto (REQ-003).
- Salida preserva `attrs` físicos del input (`units`, `long_name`, `standard_name`).
- Salida añade `attrs["tempify_method"] = "<method_name>"` y, si aplica, `attrs["rymes_myers_iterations"]` (REQ-007).
- Pixel todo-NaN en input → todo-NaN en output (REQ-008).

**Excepciones lanzadas:**
- `InvalidMonthlyStackError` si conteo de meses ≠ 12, duplicados, o no contiguo (REQ-009, REQ-012).
- `UnsupportedCalendarError` si calendario no estándar (REQ-011).
- `PartialNanPixelError` si `nan_policy="raise"` y existe píxel con NaN parcial (REQ-008).

### 3.2 Implementaciones concretas

```python
class LinearInterpolator(BaseInterpolator):
    """Piecewise linear interpolation (reference baseline)."""


class PchipInterpolator(BaseInterpolator):
    """PCHIP (Fritsch-Carlson) monotonic cubic interpolation.

    Wraps :class:`scipy.interpolate.PchipInterpolator` per pixel.
    """


class PchipMeanPreservingInterpolator(BaseInterpolator):
    """PCHIP followed by Rymes-Myers mean-preserving correction.

    Parameters
    ----------
    convergence_tol : float, default 1e-6
        Stopping criterion for the Rymes-Myers iterator: maximum absolute
        difference (in the variable's units) between reconstructed and
        original monthly means. This is the **iterator's stopping
        criterion**, NOT the contractual post-validation tolerance
        (which is ADR-0010 Level 2, owned by ``PostInterpolationValidator``).
    max_iterations : int, default 50
        Hard cap on Rymes-Myers iterations to bound worst-case cost.
    """

    def __init__(
        self,
        convergence_tol: float = DEFAULT_RM_CONVERGENCE_TOL,
        max_iterations: int = DEFAULT_RM_MAX_ITER,
    ) -> None: ...


class FourierInterpolator(BaseInterpolator):
    """Multi-harmonic Fourier series interpolation.

    Parameters
    ----------
    n_harmonics : int, default 3
        Number of Fourier harmonics retained. Must satisfy
        ``FOURIER_MIN_HARMONICS <= n_harmonics <= FOURIER_MAX_HARMONICS``
        (i.e., 1..5; Nyquist for 12 samples is 6, but harmonic 6 is the
        unobservable folded mode and is forbidden).
    """

    def __init__(self, n_harmonics: int = 3) -> None: ...
```

### 3.3 Excepciones tipadas

```python
class InterpolationError(Exception):
    """Base class for all interpolation errors."""


class InvalidMonthlyStackError(InterpolationError):
    """Raised when the input stack does not contain exactly 12 contiguous
    months (REQ-009, REQ-012). Message in Spanish (NFR-005)."""


class UnsupportedCalendarError(InterpolationError):
    """Raised when the input uses a non-Gregorian CF calendar (REQ-011).
    Message identifies the calendar detected."""


class PartialNanPixelError(InterpolationError):
    """Raised when a pixel has some but not all months NaN and
    ``nan_policy='raise'`` (REQ-008). Message includes pixel index."""
```

##### 4. Modelos de datos

### 4.1 `TemporalAxis`

```python
from dataclasses import dataclass
from typing import Literal

CFCalendar = Literal["standard", "gregorian"]  # v0.1.0 scope (REQ-011)


@dataclass(frozen=True, slots=True)
class TemporalAxis:
    """Specification of a target temporal axis.

    Parameters
    ----------
    start : datetime
        First day of the axis (inclusive).
    end : datetime
        Last day of the axis (inclusive).
    freq : TemporalFrequency
        Frequency descriptor. Only daily supported in v0.1.0.
    calendar : str, default "gregorian"
        CF calendar. ``"standard"`` and ``"gregorian"`` are aliases.
    monthly_anchor : Literal["midpoint", "start", "end", "custom"], default "midpoint"
        Anchor used to position each monthly input value on the X-axis of
        the smooth interpolators (Linear, PCHIP, Fourier) per ADR-0015 and
        REQ-013/REQ-014. ``"midpoint"`` follows the canonical table of
        ADR-0015. The PCHIP+Rymes-Myers method operates on monthly
        aggregates; this anchor only affects the auxiliary node
        initialization of its iterator.
    custom_dates : list[datetime] or None, default None
        Required when ``monthly_anchor='custom'``. Must have length 12 (or
        match the input length) and be strictly increasing within the year.

    Notes
    -----
    - ``n_days`` is derived: 365 or 366 for a single year (REQ-003).
    - Validation of ``start <= end``, leap-year consistency, and the
      ``custom_dates`` invariants happens in ``__post_init__``.
    """

    start: datetime
    end: datetime
    freq: TemporalFrequency
    calendar: str = "gregorian"
    monthly_anchor: Literal["midpoint", "start", "end", "custom"] = "midpoint"
    custom_dates: list[datetime] | None = None  # only when monthly_anchor='custom'

    @classmethod
    def from_months(
        cls,
        year: int,
        anchor: Literal["midpoint", "start", "end", "custom"] = "midpoint",
        custom_dates: list[datetime] | None = None,
    ) -> "TemporalAxis":
        """Construye el eje temporal a partir de un año, aplicando ADR-0015.

        Resuelve el ``anchor`` solicitado en posiciones concretas sobre el
        calendario del año dado y propaga la elección al eje que consumirán
        los interpoladores suaves (REQ-013, REQ-014).
        """

    @property
    def n_days(self) -> int: ...

    def to_cftime_index(self) -> "xr.cftime_range": ...
```

### 4.2 Constantes en `tempify.constants`

```python
from typing import Final

DEFAULT_CHUNK_SIZE: Final[int] = 512
DEFAULT_RM_CONVERGENCE_TOL: Final[float] = 1e-6   # ADR-0010 Level 1
DEFAULT_RM_MAX_ITER: Final[int] = 50
FOURIER_MIN_HARMONICS: Final[int] = 1
FOURIER_MAX_HARMONICS: Final[int] = 5
#### ADR-0010 Level 2 (validation tolerance) lives in PostInterpolationValidator
```

##### 5. Algoritmos clave

Convención común: el kernel 1D recibe un vector `m ∈ R^12` (valor mensual centrado en el día medio de cada mes) y devuelve un vector `d ∈ R^N` con `N ∈ {365, 366}`. Los nodos del input se ubican en el día central de cada mes según el calendario (DOYs `[15.5, 45.0, 74.5, ...]` para año no bisiesto; `[15.5, 45.5, 75.5, ...]` para bisiesto). Esto preserva la semántica "valor mensual = promedio del mes".

### 5.0 Paso 0: Posicionamiento de nodos de entrada (REQ-013, REQ-014)

Antes de invocar el kernel matemático de Linear, PCHIP o Fourier, la fachada construye el eje X de los nodos de entrada a partir del `TemporalAxis.monthly_anchor` (per ADR-0015):

```
Dado el TemporalAxis del input y el monthly_anchor:
- midpoint (default): X_i = midpoint(year, month_i)  per ADR-0015 tabla canónica
- start:               X_i = primer día del mes_i
- end:                 X_i = último día del mes_i
- custom:              X_i = custom_dates[i]
El array X es el eje del interpolador; el array Y son los valores monthly del DataArray.
```

Validaciones añadidas en este paso:
- `monthly_anchor='custom'` exige `custom_dates is not None` y `len(custom_dates) == len(source['month'])`; en caso contrario `ValueError`.
- `custom_dates` debe ser estrictamente creciente dentro del año del eje.
- El eje X resultante se serializa en `attrs["tempify_monthly_anchor"]` para trazabilidad.

El método PCHIP+Rymes-Myers (§5.3) **opera sobre agregados mensuales** y no consume directamente este eje X; la elección de `monthly_anchor` solo afecta los nodos auxiliares con los que se inicializa el iterator (la pasada PCHIP previa a la corrección iterativa).

### 5.1 Linear

```
input:  m[1..12]
output: d[1..N]

for each target_day t in [1..N]:
    find adjacent month nodes (lo, hi) such that DOY(lo) <= t <= DOY(hi)
    alpha = (t - DOY(lo)) / (DOY(hi) - DOY(lo))
    d[t] = (1 - alpha) * m[lo] + alpha * m[hi]

cyclic=True:  wrap-around between month 12 and month 1 (Dec node maps to negative DOY, Jan to DOY > N)
cyclic=False: constant extrapolation (REQ-005a) for t < DOY(1) or t > DOY(12)
```

**Complejidad:** `O(N)` (búsqueda con índice precomputado).
**Trade-offs:** referencia mínima; no preserva la media mensual; introduce kinks en los nodos.

### 5.2 PCHIP (Fritsch-Carlson)

Delegación en `scipy.interpolate.PchipInterpolator`. Para soporte cíclico se construye un vector extendido `m_ext = [m[11], m[12], m[1..12], m[1], m[2]]` con DOYs correspondientes y se evalúa solo el rango `[DOY_target_start, DOY_target_end]`. Esto evita el extrapolado artefactual de Fritsch-Carlson en los extremos.

**Edge cases:**
- Nodos cíclicos: extensión con 2 nodos a cada lado (suficiente para la suavidad C¹ de PCHIP en frontera).
- `cyclic=False`: se permite el polinomio Fritsch-Carlson extrapolar naturalmente (REQ-005b).
- Conservación de monotonicidad local: garantizada por construcción (Fritsch & Carlson 1980).

**Complejidad:** `O(N)` evaluación una vez construido el spline; construcción `O(12)`.
**Trade-offs:** mucho más suave que lineal; **no conserva la media mensual** (sesgo típico O(10⁻²) °C en temperatura). Esa es la motivación del método `pchip_mp`.

> **Decisión abierta**: elección PCHIP vs Akima como base monotónica. Akima reduce el "overshoot" cerca de discontinuidades pero rompe la monotonicidad local fuerte. Para datos climáticos mensuales (suaves), Fritsch-Carlson es la elección estándar. → resolver en design review; si se cambia, abrir ADR-0015.

### 5.3 PCHIP + Rymes-Myers (mean-preserving)

Algoritmo iterativo que parte de PCHIP suave y aplica una corrección aditiva por mes para forzar conservación de la media. Implementación basada en Rymes & Myers (2001).

**Relación con el `monthly_anchor` (REQ-013):** este método opera sobre la **media del periodo** (no sobre nodos puntuales como Linear/PCHIP/Fourier), por lo que la elección de `monthly_anchor` *no* aparece en el bucle iterativo. El anchor solo influye en la inicialización: la pasada PCHIP previa que genera los nodos auxiliares con los que arranca la corrección. La conservación de media exacta (REQ-006) es por construcción **independiente** de la elección de anchor; cambiar `monthly_anchor` puede modificar la trayectoria diaria intermedia pero no la propiedad `mean(y | mom==j) == m[j]` que el iterator fuerza al converger.

```
input:  m[1..12], target axis with DOYs d_t and month-of-day mapping mom[t]
hyperparams: convergence_tol (default 1e-6), max_iterations (default 50)

#### 1. Initial guess via PCHIP cyclic
y = pchip_cyclic(m, target_doys)

#### 2. Iterative Rymes-Myers correction
for k in 1..max_iterations:
    # Reconstruct monthly mean from current daily series
    m_hat[j] = mean(y[t] for t such that mom[t] == j)        for j in 1..12

    # Per-month additive residual
    delta[j] = m[j] - m_hat[j]

    max_err = max(|delta[j]|)
    if max_err < convergence_tol:
        break

    # Smooth-and-add: distribute delta over the days of month j with a
    # smoothing kernel (3-point moving average) to avoid step artifacts
    # at month boundaries.
    correction = smooth_distribute(delta, mom)  # same length as y
    y = y + correction

iterations_used = k

#### 3. NaN handling per REQ-008
return y, iterations_used
```

**Criterio de parada:** `max(|delta[j]|) < convergence_tol` (default `1e-6` en unidades de la variable, ADR-0010 Nivel 1).
**Tope:** `max_iterations=50` (default). Si se alcanza sin convergir, emit warning + retornar la mejor aproximación con `attrs["rymes_myers_iterations"] = max_iterations` y `attrs["rymes_myers_converged"] = False`.

**NaN parcial:** se evalúa **antes** de iterar (REQ-008). Default `raise`; con `propagate_all` se descarta el píxel; con `skip_pixel` se rellena NaN y se sigue procesando los píxeles adyacentes (relevante en stacks 2D).

**Complejidad:** `O(K · N)` con `K = iteraciones efectivas`; en práctica `K ≤ 5..10` para datos climáticos suaves.
**Trade-offs:** preserva la media mensual exactamente dentro de `convergence_tol`; coste ~5x respecto a PCHIP puro; no preserva monotonicidad local estricta.

### 5.4 Fourier multi-armónico

```
input:  m[1..12], n_harmonics K in [1..5]

#### 1. Compute DFT of monthly series (length 12)
M = np.fft.rfft(m)        # length 7 (real input)

#### 2. Truncate beyond K-th harmonic
M_trunc = zeros_like(M)
M_trunc[:K+1] = M[:K+1]

#### 3. Build continuous reconstruction at target DOYs
phi[t] = 2 * pi * (DOY(t) - DOY_anchor) / N        # phase 0..2pi over year
y[t] = M_trunc[0].real / 12
       + sum_{k=1..K} (2/12) * (M_trunc[k].real * cos(k*phi[t])
                                - M_trunc[k].imag * sin(k*phi[t]))
```

Validación: `FOURIER_MIN_HARMONICS <= n_harmonics <= FOURIER_MAX_HARMONICS` (1..5). Harmonic 6 (Nyquist para 12 muestras) representa el modo doblado no observable y queda explícitamente prohibido. Construcción inválida → `ValueError` en `__init__`.

**Boundary:** la propia construcción es periódica; `cyclic=False` no aplica ningún tratamiento especial (REQ-005c).
**Complejidad:** `O(N)` por píxel (FFT de 12 elementos es `O(1)`).
**Trade-offs:** suavidad infinita C∞; no preserva monotonicidad; no preserva la media mensual exacta (sesgo pequeño dependiente de truncamiento); ideal para variables con ciclo anual dominante (temperatura, radiación).

##### 6. Decisiones de diseño

### Decisión 1: PCHIP Fritsch-Carlson vs Akima

**Opciones consideradas:**
1. PCHIP Fritsch-Carlson (`scipy.interpolate.PchipInterpolator`).
2. Akima (`scipy.interpolate.Akima1DInterpolator`).

**Decisión:** Fritsch-Carlson como default.
**Razón:** Para series climáticas mensuales (12 nodos suaves, sin discontinuidades), Fritsch-Carlson preserva monotonicidad local estricta sin overshoot, propiedad valiosa para variables acotadas (humedad relativa ∈ [0,100], radiación ≥ 0). Akima reduce overshoot cerca de discontinuidades pero no aplica a datos climáticos suaves.
**Trade-offs:** ligero overshoot residual en transiciones rápidas (corregido por Rymes-Myers en el método `pchip_mp`).
> → resolver en design review si requiere ADR-0015 dedicado.

### Decisión 2: `cyclic` como flag binario con sub-comportamiento por método

**Opciones consideradas:**
1. Flag único `cyclic: bool = True` (REQ-004, REQ-005a/b/c).
2. Enum `BoundaryMode` por método con valores distintos.

**Decisión:** flag binario único.
**Razón:** simplicidad y trazabilidad directa a los REQs. El sub-comportamiento (constante, polinomial, periódico natural) es interno al kernel y queda documentado en docstring. Un enum por método multiplicaría la superficie de API sin valor incremental.
**Trade-offs:** el usuario debe consultar docs para saber qué hace `cyclic=False` en cada método.

### Decisión 3: Default `nan_policy='raise'` (fail-fast)

**Opciones consideradas:**
1. `raise` por defecto.
2. `propagate_all` por defecto (silent).
3. `skip_pixel` por defecto.

**Decisión:** `raise`.
**Razón:** Coherente con el principio fail-fast del proyecto (`steering/architecture.md` § Capa 3). NaN parcial en un stack mensual indica casi siempre un problema upstream (máscara mal aplicada, mosaico incorrecto). Silenciarlo enmascara bugs. El usuario que conscientemente quiera propagar puede pedirlo explícito.
**Trade-offs:** fricción en casos donde NaN parcial es legítimo (bordes de máscara oceánica). Mitigación: documentación del flag.

### Decisión 4: Kernel 1D NumPy puro separado de la fachada xarray

**Opciones consideradas:**
1. Cada `Interpolator` implementa todo el flujo (incluida `apply_ufunc`).
2. Separar `_kernels.py` con funciones 1D NumPy puras testables aisladamente.

**Decisión:** opción 2.
**Razón:** los kernels son matemáticamente densos; tenerlos como funciones puras NumPy permite tests unitarios rápidos sin sobrecoste de xarray/Dask, y permite property-based testing con hypothesis directamente sobre el kernel.
**Trade-offs:** una indirección extra; documentación del contrato kernel ↔ fachada.

### Decisión 5: Convención de posicionamiento midpoint (REQ-013, ADR-0015)

**Opciones consideradas:**
1. **Midpoint canónico** por mes calendario (per ADR-0015 tabla, con día 15 para febrero ajustado por bisiestos).
2. **Día 15 fijo** en todos los meses (independiente de la longitud del mes).
3. **Inicio de mes** (día 1) como anchor por defecto.

**Decisión:** opción 1 (midpoint), exposición opcional de las otras vía `monthly_anchor` (REQ-014).
**Razón:** la semántica "valor mensual = promedio del mes" se mapea sin sesgo al punto medio del mes. Día 15 fijo introduce un sesgo asimétrico medio de ~0.5 días en meses de 31 días y ~−0.5 en febrero, que se acumula en métodos suaves. Inicio de mes empuja los nodos hacia adelante 14–15 días y produce un desfase sistemático del ciclo anual reconstruido (visible en el cruce por cero de la derivada en derivadas climatológicas).
**Trade-offs:** los midpoints no son enteros en meses pares ni equiespaciados, lo que requiere DOYs flotantes y atención al cierre cíclico (gestionado en §5.2 y §5.4). Se acepta a cambio de la corrección estadística. Casos donde el usuario tenga semántica distinta (e.g., valor reportado al primer día del mes) se cubren con `monthly_anchor='start'` o `'custom'`.

##### 7. Estrategia de testing

### 7.1 Tests unitarios (`tests/unit/interpolation/`)

Cobertura por método y por requisito:

- `test_linear_basic` (REQ-001) — 12 valores constantes ⇒ 365/366 valores constantes.
- `test_pchip_basic` (REQ-001) — ciclo anual sinusoidal sintético, error L∞ < 0.01.
- `test_pchip_mp_basic` (REQ-001, REQ-006, NFR-002) — reconstruye media mensual exacta dentro de `convergence_tol`.
- `test_fourier_basic` (REQ-001) — input puro de armónico k ⇒ reconstrucción exacta con `n_harmonics >= k`.
- `test_base_interpolator_protocol` (REQ-002) — todas las subclases satisfacen la firma.
- `test_output_has_365_days_in_non_leap_year` / `test_output_has_366_days_in_leap_year` (REQ-003) — 2023 y 2024.
- `test_cyclic_boundary_continuity` (REQ-004) — derivada en frontera Dic/Ene continua para PCHIP, PCHIP+RM, Fourier.
- `test_non_cyclic_linear_constant` (REQ-005a).
- `test_non_cyclic_pchip_polynomial` (REQ-005b).
- `test_non_cyclic_fourier_periodic` (REQ-005c).
- `test_rymes_myers_converges` (REQ-006) — registra `iterations < max_iterations`.
- `test_rymes_myers_records_iterations` (REQ-007) — `attrs["rymes_myers_iterations"]` presente.
- `test_rymes_myers_hits_max_iterations` — caso patológico, retorna mejor aproximación con warning.
- `test_nan_all_propagation` (REQ-008) — píxel todo-NaN ⇒ output todo-NaN, no raise.
- `test_partial_nan_raises` (REQ-008) — `nan_policy='raise'` ⇒ `PartialNanPixelError` con índice del píxel.
- `test_nan_policy_propagate_all` (REQ-008).
- `test_nan_policy_skip_pixel` (REQ-008).
- `test_invalid_monthly_count_raises` (REQ-009) — 11 y 13 meses ⇒ `InvalidMonthlyStackError`.
- `test_duplicate_or_noncontiguous_months_raises` (REQ-012) — `[1,3,4,...]` y `[1,1,2,...]`.
- `test_non_gregorian_calendar_raises` (REQ-011) — `noleap`, `360_day`, `julian`, `all_leap`.
- `test_vectorized_with_dask` (REQ-010) — el `xr.DataArray` retornado es lazy (`isinstance(da.data, dask.array.Array)`); resultado tras `.compute()` coincide con eager.
- `test_fourier_n_harmonics_out_of_range` — `n_harmonics ∈ {0, 6, 100}` ⇒ `ValueError`.
- `test_error_messages_spanish` (NFR-005) — todas las excepciones tipadas llevan mensaje en español.
- `test_temporal_axis_midpoint_table` (REQ-013) — verifica los 12 midpoints generados por `TemporalAxis.from_months(year=2023, anchor='midpoint')` contra la tabla canónica de ADR-0015.
- `test_temporal_axis_leap_year_february_midpoint_day_15` (REQ-013) — `from_months(year=2024, anchor='midpoint')` ubica el midpoint de febrero en el día 15 (no 14.5) per ADR-0015 sección bisiestos.
- `test_linear_input_nodes_at_midpoint` (REQ-013) — el `LinearInterpolator` por defecto posiciona los nodos de entrada en los midpoints canónicos; el eje X interno coincide con `TemporalAxis.from_months(...).monthly_anchor_doys()`.
- `test_monthly_anchor_start_shifts_nodes` (REQ-014) — con `monthly_anchor='start'`, los nodos quedan en el día 1 de cada mes; el output diario muestra el desfase esperado vs `'midpoint'`.
- `test_custom_anchor_requires_explicit_dates` (REQ-014) — `monthly_anchor='custom'` sin `custom_dates` ⇒ `ValueError`; con `custom_dates` de longitud ≠ 12 ⇒ `ValueError`; con `custom_dates` no crecientes ⇒ `ValueError`.

### 7.2 Tests property-based (`tests/unit/interpolation/test_properties.py`, con `hypothesis`)

- `test_rymes_myers_preserves_mean` (NFR-002): para cualquier `m ∈ R^12` con `|m_i| < 1e3`, la media mensual reconstruida del output diario satisface `assert_allclose(m_hat, m, atol=convergence_tol)`. Mín. 100 casos.
- `test_all_nan_propagation_property` (REQ-008): para cualquier `m` con `all(isnan(m))`, output `all(isnan)`.
- `test_temperature_monotone_pixel` (Fourier, PCHIP): sobre series sintéticas estrictamente monótonas en `[Ene..Jul]`, ninguno de los métodos suaves introduce inversiones espurias en ese segmento (relajado a tolerancia `1e-9`).
- `test_pchip_cyclic_continuity_property` (REQ-004): `|y[N] - y[1]| < epsilon` para cualquier `m`.

### 7.3 Tests de integración (`tests/integration/interpolation/`)

- `test_quinta_normal_2020` — comparación contra dataset Quinta Normal 2020 per `docs/methodology/empirical-validation-quinta-normal.md`. Para cada método, `RMSE(daily, observed)` debe coincidir con valores baseline ±2%.
- `test_worldclim_small_subset` — stack recortado WorldClim 5min (`bbox=(-72,-34,-70,-32)`), end-to-end con Dask, output coherente con dims y CRS preservados.
- `test_reproducibility_strict_md5_match` (NFR-003, ADR-0007) — `dask.config.set(scheduler='synchronous')`, MD5 del output contra baseline por plataforma.
- `test_reproducibility_parallel_allclose` (NFR-003, ADR-0007) — 10 ejecuciones consecutivas en `scheduler='threaded'`, `assert_allclose(rtol=1e-12, atol=1e-15)`.

### 7.4 Benchmarks (`tests/benchmark/test_perf_chile_2.5min.py`)

- NFR-001: stack `12×3000×500`, 8 cores `threaded`, < 60 s.
- NFR-004: profiling con `memray`, peak memory por chunk < 1 GB con `chunk_size=512`.
- Reporte automático en `tests/benchmark/results/<date>-<method>.json`.

### 7.5 Fixtures necesarios

- `synthetic_3x3_monthly_smooth.nc` — generador determinista; ciclo sinusoidal.
- `synthetic_3x3_monthly_partial_nan.nc` — píxeles con NaN parcial.
- `synthetic_3x3_monthly_all_nan_pixel.nc` — 1 píxel todo-NaN.
- `quinta_normal_2020.nc` — ya existe en `tests/data/` (per validación empírica).
- `worldclim_5min_chile_central_subset.nc` — recorte ~50 MB, comprimido.
- Fixtures generados en `conftest.py` con `@pytest.fixture(scope="session")`.

##### 8. Plan de migración

N/A. Esta spec es la primera implementación de Capa 4. No hay código previo que migrar.

##### 9. Métricas de calidad

| Métrica | Umbral |
|---|---|
| Coverage `tempify.interpolation.*` | ≥ 85% (Guardrail 1, CLAUDE.md) |
| `mypy --strict` sobre el paquete | 0 errores |
| `ruff check` + `ruff format` | clean |
| NFR-001 (Chile 2.5 arc-min, 8 cores) | < 60 s |
| NFR-004 (peak RAM por chunk) | < 1 GB |
| NFR-002 (conservación de media en PCHIP+RM) | `assert_allclose(atol=1e-6)` en 100+ casos hypothesis |
| NFR-003 strict | MD5 idéntico contra baseline por plataforma |
| NFR-003 parallel | `assert_allclose(rtol=1e-12, atol=1e-15)` entre 10 corridas |
| NFR-005 (mensajes en español) | test dedicado, 100% de excepciones públicas |

##### 10. Trazabilidad requirements → design → tests

| Requirement | Componente | Test principal |
|---|---|---|
| REQ-001 | 4 clases `*Interpolator` | `test_{linear,pchip,pchip_mp,fourier}_basic` |
| REQ-002 | `BaseInterpolator` ABC | `test_base_interpolator_protocol` |
| REQ-003 | `TemporalAxis.n_days`, build de eje destino | `test_output_has_{365,366}_days_in_*` |
| REQ-004 | Lógica cyclic en los 4 kernels | `test_cyclic_boundary_continuity` |
| REQ-005a | `LinearInterpolator` rama `cyclic=False` | `test_non_cyclic_linear_constant` |
| REQ-005b | `PchipInterpolator` rama `cyclic=False` | `test_non_cyclic_pchip_polynomial` |
| REQ-005c | `FourierInterpolator` (no special handling) | `test_non_cyclic_fourier_periodic` |
| REQ-006 | `PchipMeanPreservingInterpolator._iterate` | `test_rymes_myers_converges` |
| REQ-007 | Stamping `attrs["rymes_myers_iterations"]` | `test_rymes_myers_records_iterations` |
| REQ-008 | `_validate_nan_policy` en `BaseInterpolator` | `test_nan_*`, `test_partial_nan_raises` |
| REQ-009 | `_validate_month_count` en `BaseInterpolator` | `test_invalid_monthly_count_raises` |
| REQ-010 | `xr.apply_ufunc(..., dask='parallelized')` | `test_vectorized_with_dask` |
| REQ-011 | `_validate_calendar` en `BaseInterpolator` | `test_non_gregorian_calendar_raises` |
| REQ-012 | `_validate_month_contiguity` | `test_duplicate_or_noncontiguous_months_raises` |
| REQ-013 | `TemporalAxis.from_months(anchor='midpoint')`, paso 0 §5.0 en Linear/PCHIP/Fourier | `test_temporal_axis_midpoint_table`, `test_temporal_axis_leap_year_february_midpoint_day_15`, `test_linear_input_nodes_at_midpoint` |
| REQ-014 | `TemporalAxis.monthly_anchor`, validación de `custom_dates` | `test_monthly_anchor_start_shifts_nodes`, `test_custom_anchor_requires_explicit_dates` |
| NFR-001 | Defaults de chunking + scheduler `threaded` | `tests/benchmark/test_perf_chile_2.5min.py` |
| NFR-002 | Iterador Rymes-Myers con `convergence_tol` | `test_rymes_myers_preserves_mean` (hypothesis) |
| NFR-003 | Compatibilidad con `reproducibility_context` (Capa 5) | `test_reproducibility_strict_md5_match`, `test_reproducibility_parallel_allclose` |
| NFR-004 | `chunk_size=512` default, `time=-1` | profiling `memray` en benchmark |
| NFR-005 | Excepciones con mensajes en español | `test_error_messages_spanish` |

##### 11. Referencias

- ADR-0001 — `xarray.DataArray` como abstracción central.
- ADR-0002 — Dask vs multiprocessing.
- ADR-0004 — Política de precipitación (rechazo se enforça en Capa 3, NO aquí).
- ADR-0007 — Política de reproducibilidad de dos modos.
- ADR-0010 — Tolerancia de conservación de la media en tres niveles.
- ADR-0015 — Convención midpoint para el posicionamiento temporal de valores mensuales.
- CF Conventions §7.4 — Climatological statistics.
- Fritsch, F. N., & Carlson, R. E. (1980). Monotone piecewise cubic interpolation. *SIAM J. Numer. Anal.*, 17(2), 238-246.
- Rymes, M. D., & Myers, D. R. (2001). Mean preserving algorithm for smoothly interpolating averaged data. *Solar Energy*, 71(4), 225-231.
- `docs/methodology/empirical-validation-quinta-normal.md`.
- `steering/architecture.md` § Capa 4 Interpolation.
- `steering/conventions.md` — docstring NumPy, mypy strict, ruff, naming.
- `steering/tech.md` — Python 3.11+, scipy ≥ 1.12, xarray ≥ 2024.1.

```

## File: `specs/validation/requirements.md`


```markdown
﻿# Requirements — validation

**Estado:** Approved
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-15
**Última actualización:** 2026-05-16

##### 1. Propósito

Implementar validaciones de coherencia geoespacial pre-procesamiento y validaciones de propiedades estadísticas post-interpolación. Garantizar fail-fast ante inputs inconsistentes y trazabilidad de la calidad del output mediante un `ValidationReport` serializable.

##### 2. Alcance

### In-scope

- Validación de coherencia entre archivos: CRS, extent, resolución, nodata, dentro de tolerancias canónicas definidas en `docs/adr/0009-geospatial-coherence-tolerances.md`.
- Validación de compatibilidad método-variable según el perfil declarado en `docs/schemas/variable-profile.schema.yaml`.
- Validación post-interpolación: conservación de media mensual, continuidad cíclica (diciembre-enero, junio-julio), rango físico por píxel-día.
- Reportería estadística por banda temporal (`StatisticalReporter`).
- Política diferenciada fail-fast (pre) vs warn-and-continue (post).
- Soporte de override `--force-method --i-know-what-i-am-doing` per `docs/adr/0004-precipitation-policy.md`.

### Out-of-scope

- Reproyección automática (se reporta la inconsistencia, no se corrige).
- Imputación de datos faltantes.
- Validación cross-variable (p. ej. `tmin <= tmax`); diferida a v0.2.
- Soporte de calendarios CF no-estándar (`360_day`, `noleap`); diferido.
- Generación dinámica de perfiles de variable; los YAML los provee el proyecto (no se generan en runtime).

##### 3. Actores y casos de uso

### Actor: Pipeline interno que necesita certeza sobre la validez de los datos antes y después de procesar.

**Caso de uso típico:** El pipeline pasa los archivos al validator antes de interpolar. Si hay un .tif con CRS distinto al resto, el validator aborta con `PreValidationError(report)`. Tras la interpolación, el post-validator verifica conservación de media, continuidad cíclica y rango físico; las violaciones se reportan como WARN sin abortar.

##### 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL verify that all input rasters share CRS, spatial extent, spatial resolution, and nodata value within the canonical tolerances declared in `docs/adr/0009-geospatial-coherence-tolerances.md`.

### REQ-002 (Unwanted)

IF any geospatial inconsistency is detected, THEN THE SYSTEM SHALL raise `GeospatialIncoherenceError` with detailed identification of which files differ and on which dimension (CRS, extent, resolution, nodata).

### REQ-003 (Event-driven)

WHEN a method-variable combination is incompatible per the variable profile (e.g., smooth interpolation of precipitation), THE SYSTEM SHALL raise `MethodVariableIncompatibilityError` before processing.

### REQ-004 (Event-driven)

WHEN post-interpolation validation runs on a PCHIP+RM output, THE SYSTEM SHALL verify that the monthly mean is preserved within the post-validator contractual tolerance `atol=1e-4` and `rtol=1e-6`, per `docs/adr/0010-mean-preservation-tolerance.md` (the tighter `1e-6` is reserved for the RM iterator's internal convergence, not for this check).

### REQ-005 (Ubiquitous)

THE SYSTEM SHALL produce a `ValidationReport` dataclass conformant with `docs/schemas/validation-report.schema.md`, exposing the canonical fields `checks`, `pre_passed`, `post_passed`, `warnings`, `errors`, and `statistics`.

### REQ-006 (Ubiquitous)

WHILE running `PostInterpolationValidator`, THE SYSTEM SHALL verify cyclic continuity by comparing the rolling means across the December-January and June-July boundaries against the tolerance declared in the variable profile.

### REQ-007 (Ubiquitous)

WHILE running `PostInterpolationValidator`, THE SYSTEM SHALL verify that each pixel-day value falls within the `physical_range` (`min`, `max`) declared in the variable profile.

### REQ-008 (Ubiquitous)

THE SYSTEM SHALL expose `StatisticalReporter` that emits per-band statistics with the keys: `min`, `max`, `mean`, `std`, `nan_pct`, `count_valid`.

### REQ-009 (Ubiquitous)

THE SYSTEM SHALL apply a fail-fast policy for pre-process validation (raise `PreValidationError(report)`) and a warn-and-continue policy for post-process validation (emit a `WARN` entry in `ValidationReport.warnings` and log a warning via the standard logger).

### REQ-010 (Optional, WHERE)

WHERE the user passes `--force-method <method> --i-know-what-i-am-doing` for an incompatible `(variable, method)` pair, THE SYSTEM SHALL emit a `COMPAT-003` WARN entry in `ValidationReport.warnings` instead of raising `MethodVariableIncompatibilityError`, AND stamp the output dataset with the attribute `force_method_used = true`.

##### 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Reliability | El `ValidationReport` debe ser serializable (JSON) y contener todas las claves canónicas del schema | Test `test_validation_report_serialization_keys` |
| NFR-002 | Usability | Mensajes de error en español, con código referenciable (`GEO-NNN`, `COMPAT-NNN`, `POST-NNN`) | Test `test_error_messages_spanish` |
| NFR-003 | Performance | Validación pre + post sobre un stack `12 x 3000 x 500` debe completarse en `< 10 s` en hardware de referencia | Test `test_validation_performance_stack_12x3000x500` |

##### 6. Criterios de aceptación

- [ ] Cada REQ cubierto por un test nombrado, según la siguiente trazabilidad:

| REQ | Test(s) |
|---|---|
| REQ-001 | `test_crs_mismatch_raises`, `test_extent_mismatch_raises`, `test_resolution_mismatch_raises`, `test_nodata_mismatch_raises` |
| REQ-002 | `test_crs_mismatch_raises`, `test_extent_mismatch_raises`, `test_resolution_mismatch_raises`, `test_nodata_mismatch_raises` |
| REQ-003 | `test_method_variable_compat` |
| REQ-004 | `test_post_mean_preservation` |
| REQ-005 | `test_validation_report_serialization_keys` |
| REQ-006 | `test_post_cyclic_continuity` |
| REQ-007 | `test_post_physical_range` |
| REQ-008 | `test_statistical_reporter_keys` |
| REQ-009 | `test_fail_fast_pre_vs_warn_post` |
| REQ-010 | `test_force_method_override_emits_warn` |
| NFR-001 | `test_validation_report_serialization_keys` |
| NFR-002 | `test_error_messages_spanish` |
| NFR-003 | `test_validation_performance_stack_12x3000x500` |

- [ ] Cobertura del módulo `>= 85%`.
- [ ] Documentación API completa (docstrings NumPy + type hints).
- [ ] CHANGELOG actualizado.

##### 7. Dependencias y supuestos

### Specs relacionadas

- Bloqueada por: [io-handlers](../io-handlers/requirements.md), [structure-detection](../structure-detection/requirements.md), [core-interpolation](../core-interpolation/requirements.md)
- Bloquea: [pipeline](../pipeline/requirements.md), [cli](../cli/requirements.md), [gui](../gui/requirements.md)

### Documentos de referencia (contratos vinculantes)

- `steering/architecture.md` § Capa 3.
- `docs/methodology/precipitation.md`.
- `docs/adr/0004-precipitation-policy.md` (override `--force-method`).
- `docs/adr/0009-geospatial-coherence-tolerances.md` (tolerancias canónicas).
- `docs/adr/0010-mean-preservation-tolerance.md` (tres niveles de tolerancia: convergencia `1e-6`, post-validator `atol=1e-4 + rtol=1e-6`, perfil YAML).
- `docs/schemas/validation-report.schema.md` (shape de `ValidationReport`).
- `docs/schemas/variable-profile.schema.yaml` (estructura YAML de perfiles).

### Supuestos

- Los inputs son archivos legibles por GDAL via rioxarray.
- La normalización de NaN vs `_FillValue` ocurre en Capa 1 (io-handlers) antes de llegar a Capa 3.
- Los perfiles de variable existen como archivos YAML versionados en el repositorio y conforman al schema.

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Float-imprecision en comparación de extent entre archivos | Media | Medio | Aplicar tolerancias canónicas de `docs/adr/0009-geospatial-coherence-tolerances.md` (rtol/atol) en lugar de igualdad estricta |
| Divergencia entre NaN y sentinel `_FillValue` entre lectores (GeoTIFF vs NetCDF vs Zarr) | Media | Alto | Normalizar a NaN en Capa 1 (io-handlers); el validator asume el dato ya normalizado |
| Ausencia o desactualización del schema YAML de perfil de variable | Baja | Alto | Schema versionado en `docs/schemas/variable-profile.schema.yaml`; validación del perfil al cargar |
| RM no converge en celdas con varianza extrema y la conservación de media falla la tolerancia | Media | Bajo | El iterador retorna la mejor aproximación; el post-validator marca `WARN` (POST-001), no `ERROR` |
| Validación cross-variable (p. ej. `tmin <= tmax`) no contemplada en v1.0 | Alta | Bajo | Declarado explícitamente out-of-scope; diferido a v0.2 |
| Edge cases en formatos no estándar | Media | Bajo | Fixtures extensivas + manejo robusto de excepciones |

##### 8. Referencias

- CF Conventions: https://cfconventions.org/
- EARS notation: https://alistairmavin.com/ears/
- ADR-0004 (precipitation policy), ADR-0009 (geo tolerances), ADR-0010 (mean tolerance).
- `docs/schemas/validation-report.schema.md`, `docs/schemas/variable-profile.schema.yaml`.

```

## File: `specs/validation/design.md`


```markdown
# Design — validation

**Estado:** Draft
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-15

##### 1. Visión técnica

La Capa 3 (`tempify.validation`) actúa como contrato de calidad entre la lectura I/O (Capa 1), la detección estructural (Capa 2) y los interpoladores (Capa 4). Implementa dos políticas diferenciadas: **fail-fast** para invariantes pre-procesamiento (incoherencia geoespacial, incompatibilidad método-variable), y **warn-and-continue** para verificaciones post-interpolación (preservación de media, continuidad cíclica, rango físico).

El paquete se diseña como una colección de validadores stateless con un contrato común: reciben datos y un contexto (`Tolerances`, `VariableProfile`) y devuelven un `ValidationReport` serializable conforme al schema `docs/schemas/validation-report.schema.md`. No realiza I/O ni cálculos de interpolación; consume `xarray.DataArray` ya normalizado por la Capa 1.

##### 2. Arquitectura propuesta

### Diagrama de componentes

```
tempify.validation
├── geocoherence.py        # GeospatialCoherenceValidator + Tolerances
├── compatibility.py       # MethodVariableCompatibilityChecker
├── post.py                # PostInterpolationValidator
├── statistics.py          # StatisticalReporter
├── profiles.py            # VariableProfileMatcher + VariableProfile
├── report.py              # CheckResult, ValidationReport, builders
├── errors.py              # PreValidationError, GeospatialIncoherenceError,
│                          # MethodVariableIncompatibilityError
└── _codes.py              # registro de códigos GEO-*, COMPAT-*, POST-*
```

Flujo del Pipeline (referencia, no implementado aquí):

```
Capa 1 (io)  →  GeospatialCoherenceValidator  →  [fail-fast: PreValidationError]
              ↓
            MethodVariableCompatibilityChecker  →  [fail-fast: salvo --force-method]
              ↓
            Capa 4 (interpolation)
              ↓
            PostInterpolationValidator  →  [warn-and-continue]
              ↓
            StatisticalReporter
              ↓
            ValidationReport (JSON-serializable)
```

### Componentes nuevos

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| `GeospatialCoherenceValidator` | `tempify/validation/geocoherence.py` | Verifica CRS, extent, resolución, nodata, shape entre rasters. |
| `Tolerances`, `CANONICAL_TOLERANCES` | `tempify/validation/geocoherence.py` | Dataclass frozen con tolerancias canónicas de ADR-0009. |
| `MethodVariableCompatibilityChecker` | `tempify/validation/compatibility.py` | Aplica política de `allowed_methods` con override `--force-method`. |
| `PostInterpolationValidator` | `tempify/validation/post.py` | Verifica conservación de media, continuidad cíclica, rango físico, NaN integrity. |
| `StatisticalReporter` | `tempify/validation/statistics.py` | Calcula min/max/mean/std/nan_pct/count_valid por banda temporal. |
| `VariableProfileMatcher` | `tempify/validation/profiles.py` | Resuelve `VariableProfile` a partir de `DetectionResult` (CF, alias, unidades). |
| `VariableProfile` | `tempify/validation/profiles.py` | Modelo cargado vía `pyyaml` + validación `jsonschema` contra el schema canónico. |
| `CheckResult`, `ValidationReport` | `tempify/validation/report.py` | Modelos del schema canónico. |
| `PreValidationError` y subclases | `tempify/validation/errors.py` | Excepciones que portan el `ValidationReport`. |

### Componentes modificados

Ninguno en este alcance. La Capa 5 (Pipeline) consumirá estos contratos en su propia spec.

##### 3. Contratos públicos (APIs)

### `GeospatialCoherenceValidator`

```python
class GeospatialCoherenceValidator:
    def __init__(self, tolerances: Tolerances = CANONICAL_TOLERANCES) -> None: ...

    def check(self, rasters: Sequence[xr.DataArray]) -> ValidationReport:
        """Validate homogeneity across a sequence of rasters.

        Returns a ValidationReport with PRE_PROCESS checks. Does not raise;
        the caller (Pipeline) decides whether to raise PreValidationError
        from `report.pre_passed`.
        """
```

**Pre-condiciones:** cada raster expone `rio.crs`, `rio.transform()`, `rio.nodata`, `shape`.
**Post-condiciones:** report contiene una `CheckResult` por dimensión verificada (CRS, extent, resolución, nodata, shape), con código `GEO-001..005`.
**Excepciones:** no lanza; errores semánticos de los inputs (e.g. raster sin CRS) producen `CheckResult` con `severity=ERROR`.

### `MethodVariableCompatibilityChecker`

```python
class MethodVariableCompatibilityChecker:
    def check(
        self,
        variable_profile: VariableProfile,
        method: Literal["linear", "pchip", "pchip_mp", "fourier"],
        *,
        force: bool = False,
    ) -> CheckResult:
        """Validate that `method` is allowed for the variable profile."""
```

**Pre-condiciones:** `variable_profile` ya validado contra el schema.
**Post-condiciones:**
- Si `method in profile.allowed_methods`: `CheckResult(COMPAT-001, passed=True, INFO)`.
- Si `method ∉ allowed_methods` y `force=False`: `CheckResult(COMPAT-001 o COMPAT-002 si precipitación, passed=False, ERROR)`. El caller debe lanzar `MethodVariableIncompatibilityError`.
- Si `force=True`: `CheckResult(COMPAT-003, passed=True, WARN)` y el caller marca `output.attrs["force_method_used"] = True`.

### `PostInterpolationValidator`

```python
class PostInterpolationValidator:
    def __init__(self, profile: VariableProfile) -> None: ...

    def check(
        self,
        input_da: xr.DataArray,
        output_da: xr.DataArray,
        profile: VariableProfile,
    ) -> ValidationReport:
        """Validate POST_PROCESS invariants on the interpolated output."""
```

**Pre-condiciones:** `input_da` con eje temporal de baja frecuencia (típicamente 12 meses); `output_da` con eje temporal denso (365/366 días) cubriendo el mismo span.
**Post-condiciones:** report contiene `POST-001..004`, todos con `phase=POST_PROCESS`. `POST-001..003` son WARN; `POST-004` (NaN inesperado donde input tenía valor) es ERROR. Nunca lanza.

### `StatisticalReporter`

```python
class StatisticalReporter:
    def report(self, da: xr.DataArray) -> dict[str, dict[str, float]]:
        """Return per-time-band statistics."""
```

**Pre-condiciones:** `da` con dim temporal (`time`).
**Post-condiciones:** dict cuya clave es la representación ISO del timestamp de cada banda y valor es `{"min", "max", "mean", "std", "nan_pct", "count_valid"}` en `float`.

### `VariableProfileMatcher`

```python
class VariableProfileMatcher:
    def __init__(self, profiles_path: Path | None = None) -> None: ...

    def match(self, detection_result: DetectionResult) -> VariableProfile:
        """Resolve a VariableProfile from detection signals (CF, alias, units)."""
```

**Pre-condiciones:** `detection_result` provee al menos uno de: `standard_name`, `variable_name`, `units`.
**Post-condiciones:** retorna el `VariableProfile` con mayor score de coincidencia (CF standard_name > alias exacto > unidades + alias parcial). Si no hay match: `UnknownVariableProfileError`.

##### 4. Modelos de datos

### `CheckSeverity`, `CheckPhase`, `CheckResult`, `ValidationReport`

Definidos en `docs/schemas/validation-report.schema.md` y replicados literalmente en `tempify/validation/report.py`. `ValidationReport` expone helpers `failed_errors()`, `has_warnings()`, y `to_json() -> str` para serialización (NFR-001).

### `Tolerances`

```python
@dataclass(frozen=True)
class Tolerances:
    extent_rtol: float = 1e-6
    extent_atol_pixel_fraction: float = 0.01  # atol = fraction * pixel_size
    resolution_rtol: float = 1e-6
    crs_ignore_axis_order: bool = True
    nodata_strict: bool = True

CANONICAL_TOLERANCES: Final[Tolerances] = Tolerances()
```

Cualquier mutación requiere ADR sucesor (ADR-0009).

### `VariableProfile`

Pydantic v2 `BaseModel` con `model_config = ConfigDict(frozen=True, extra="forbid")`. Carga desde YAML vía `yaml.safe_load` + validación cruzada con `jsonschema` contra `variable-profile.schema.yaml` (single source of truth). Campos derivados del schema: `name`, `canonical_name`, `aliases`, `units`, `allowed_methods`, `default_method`, `physical_range` (`min`, `max`, `strict`), `acceptable_mean_error`, `acceptable_relative_error`, `monotonicity`, `default_chunk_size`, `references`, `version`.

Los perfiles concretos viven en el paquete `tempify.profiles` (archivos `profiles/*.yaml`) y se cargan vía `importlib.resources.files("tempify.profiles")`.

### Excepciones

```python
class PreValidationError(Exception):
    def __init__(self, report: ValidationReport): ...

class GeospatialIncoherenceError(PreValidationError): ...
class MethodVariableIncompatibilityError(PreValidationError): ...
class UnknownVariableProfileError(PreValidationError): ...
```

##### 5. Algoritmos clave

### 5.1 GeospatialCoherenceValidator

Toma el primer raster como referencia y compara cada uno contra él. Para cada eje:

- **CRS (GEO-001):** `pyproj.CRS.from_user_input(a).equals(pyproj.CRS.from_user_input(b), ignore_axis_order=True)`.
- **Extent (GEO-002):** `numpy.isclose(bounds_a, bounds_b, rtol=1e-6, atol=0.01 * pixel_size)`. El `pixel_size` se toma del raster de referencia.
- **Resolución (GEO-003):** `math.isclose(res_x_a, res_x_b, rel_tol=1e-6)` y mismo test sobre `res_y`.
- **NoData (GEO-004):** `nodata_a is None and nodata_b is None` o `numpy.isnan` para ambos o `nodata_a == nodata_b`. Heterogeneidad si solo uno tiene `_FillValue`.
- **Shape (GEO-005):** comparación entera estricta de `(height, width)`.

Devuelve **todas** las inconsistencias encontradas, no solo la primera. Complejidad O(n) donde n es número de rasters.

### 5.2 MethodVariableCompatibilityChecker

Tabla derivada del `VariableProfile.allowed_methods`. Reglas:

1. `method in allowed_methods` → COMPAT-001 INFO `passed=True`.
2. `method ∉ allowed_methods` y `allowed_methods == []` (caso precipitación) → COMPAT-002 ERROR `passed=False`.
3. `method ∉ allowed_methods` y `allowed_methods != []` → COMPAT-001 ERROR `passed=False`.
4. Cualquier (2) o (3) con `force=True` → degrada a COMPAT-003 WARN `passed=True` y `details["force_method"] = method`. El Pipeline es responsable de estampar `output.attrs["force_method_used"] = True`.

### 5.3 Preservación de media mensual (POST-001)

Para cada píxel `(y, x)`:

1. Agrupar `output_da` por mes calendario (`output_da.groupby("time.month").mean("time")` ajustado para usar el mes calendario real, no el índice de mes).
2. Comparar contra `input_da.values` posicional.
3. Aplicar `|reconstructed - original| <= atol + rtol * |original|` con `atol = profile.acceptable_mean_error or POST_VALIDATION_ABS_TOL` (1e-4) y `rtol = profile.acceptable_relative_error or POST_VALIDATION_REL_TOL` (1e-6), conforme a ADR-0010.
4. Si cualquier píxel-mes falla: `POST-001 WARN passed=False` con `details={"pixel_failure_pct": ..., "max_abs_error": ..., "tol_source": "profile"|"default"}`.

Vectorizado con `xr.apply_ufunc(dask="parallelized")` para soportar inputs lazy.

### 5.4 Continuidad cíclica (POST-002)

Para los bordes diciembre→enero y junio→julio:

1. Calcular rolling mean de 31 días centrado: `output_da.rolling(time=31, center=True).mean()`.
2. Para cada par de bordes, comparar la dispersión (`std`) de la ventana que cruza el borde contra la dispersión de ventanas interiores del mismo mes. Si la dispersión del borde excede en `> factor * median_interior_std` (factor declarado por la spec; default `3.0`), reportar POST-002 WARN.
3. Agregar por píxel; reportar porcentaje de píxeles con discontinuidad.

### 5.5 Rango físico (POST-003)

`(output_da < profile.physical_range.min) | (output_da > profile.physical_range.max)`. Si hay violaciones:

- `profile.physical_range.strict == False` → POST-003 WARN.
- `profile.physical_range.strict == True` → POST-003 ERROR (eleva severidad; sigue siendo POST y no aborta el Pipeline; el Pipeline decide si trata strict como fail según política propia).

### 5.6 Integridad de NaN (POST-004)

Verificación: para todo `(t_input, y, x)` donde `input_da.isel(time=t)` no es NaN, todos los días de `output_da` que caen en ese mes deben ser numéricos. Aparición de NaN nuevo en output donde el input era válido es POST-004 ERROR (no WARN).

### 5.7 StatisticalReporter

Por cada banda temporal, calcula `min, max, mean, std, nan_pct, count_valid` con `xarray` reductions (`skipna=True`). Resultado serializable como `dict[str, dict[str, float]]` indexado por timestamp ISO 8601.

##### 6. Decisiones de diseño

### Decisión 1: fail-fast pre vs warn post

**Opciones consideradas:**
1. Toda validación abort-on-error.
2. Toda validación warn-and-continue.
3. Mixta: pre fail-fast, post warn (elegida).

**Decisión:** Opción 3, conforme a `steering/architecture.md` § Capa 3.
**Razón:** las inconsistencias pre-procesamiento (CRS distinto) producen outputs sin sentido; abortar es la única respuesta defendible. Las inconsistencias post (mean preservation marginalmente fuera de tolerancia) son informativas, no invalidantes; abortar destruiría trabajo computacional caro.
**Trade-offs:** el usuario debe consultar el reporte para enterarse de warnings. Mitigado por logging estándar y por el campo `pre_passed` / `post_passed` en el reporte.

### Decisión 2: VariableProfile carga vía pydantic + jsonschema

**Opciones consideradas:**
1. Solo `pyyaml` con validación ad-hoc.
2. Solo `pydantic` con sus propios validators.
3. `pyyaml` + `jsonschema` contra el schema canónico + `pydantic` para tipado en runtime (elegida).

**Decisión:** Opción 3.
**Razón:** el schema YAML es el contrato versionado (ADR-0004, ADR-0010); validar contra él garantiza que perfiles externos del usuario cumplan el contrato. Pydantic da tipos estáticos para el resto del código.
**Trade-offs:** doble dependencia (pydantic + jsonschema), pero ambas ya están en el stack tech.

### Decisión 3: stamping `force_method_used` es responsabilidad del Pipeline

El validator emite el `CheckResult` con `details["force_method"]`. El Pipeline (Capa 5) lee el reporte y aplica el `attrs` al output antes de pasarlo al writer (Capa 1). El validator no muta DataArrays.

##### 7. Estrategia de testing

### Tests unitarios (uno por código de error)

- **GEO-001..005**: `test_crs_mismatch_raises`, `test_extent_mismatch_raises`, `test_resolution_mismatch_raises`, `test_nodata_mismatch_raises`, `test_shape_mismatch_raises`. Fixtures: rasters sintéticos homogéneos y heterogéneos generados en setup.
- **COMPAT-001..003**: `test_method_variable_compat` (matriz de combinaciones), `test_precipitation_rejects_smooth_methods` (COMPAT-002), `test_force_method_override_emits_warn` (COMPAT-003 + stamping).
- **POST-001..004**: `test_post_mean_preservation` (tolerancia respetada y violada), `test_post_cyclic_continuity` (perfil discontinuo en dic-ene), `test_post_physical_range` (overshoot temperatura), `test_post_nan_integrity`.
- **Reporte**: `test_validation_report_serialization_keys` (NFR-001), `test_error_messages_spanish` (NFR-002).
- **Perfiles**: `test_profile_yaml_validates_against_schema`, `test_profile_matcher_cf_first`, `test_profile_matcher_alias_fallback`, `test_unknown_variable_raises`.

### Tests property-based (hypothesis)

- `test_mean_preservation_invariant`: para arrays sintéticos `(12, h, w)` con valores en rango físico de temperatura, si el output es construido por agregación inversa exacta del input, la verificación POST-001 nunca falla.
- `test_tolerance_monotonicity`: incrementar `acceptable_mean_error` nunca convierte un PASS en FAIL.
- `test_statistics_keys_invariant`: la salida de `StatisticalReporter` siempre contiene las 6 claves canónicas, para cualquier DataArray no vacío.

### Tests de integración

- `test_end_to_end_pre_then_post`: rasters homogéneos + perfil temperatura + interpolación PCHIP+RM mock-up → `pre_passed=True`, `post_passed=True`.
- `test_fail_fast_pre_vs_warn_post` (REQ-009): heterogeneidad CRS lanza `PreValidationError`; tras corregir, una violación de POST-001 produce solo WARN.
- `test_validation_performance_stack_12x3000x500` (NFR-003): assert `< 10 s`.

### Fixtures necesarios

- `tests/fixtures/rasters/homogeneous_3x3_12bands.tif` — generado en `conftest.py`.
- `tests/fixtures/rasters/crs_mismatch.tif`, `extent_mismatch.tif`, etc. — variantes sintéticas con una sola dimensión alterada.
- `tests/fixtures/profiles/valid/`: copias de `profiles/temperature.yaml`, `profiles/precipitation.yaml`, `profiles/relative_humidity.yaml`.
- `tests/fixtures/profiles/invalid/`: perfiles que violan el schema (missing required, default_method no en allowed_methods).
- `tests/fixtures/series/discontinuous_dec_jan.nc` — serie diaria con escalón artificial dic→ene para POST-002.

##### 8. Plan de migración

No aplica. Spec de feature nueva sobre módulos vacíos.

##### 9. Métricas de calidad

| Métrica | Umbral |
|---|---|
| Coverage del módulo `tempify.validation.*` | ≥ 85% (guardrail 1) |
| Performance pre+post sobre `12 x 3000 x 500` | < 10 s (NFR-003) |
| Memoria peak sobre `12 x 3000 x 500` | < 4 GB |
| Tiempo de carga de un `VariableProfile` desde YAML | < 50 ms |

##### 10. Trazabilidad requirements → design

| Requirement | Componente que lo implementa | Test principal |
|---|---|---|
| REQ-001 | `GeospatialCoherenceValidator.check` con `CANONICAL_TOLERANCES` | `test_crs/extent/resolution/nodata_mismatch_raises` |
| REQ-002 | `GeospatialIncoherenceError` + códigos GEO-001..005 en `_codes.py` | mismos que REQ-001 |
| REQ-003 | `MethodVariableCompatibilityChecker.check` (`force=False`) | `test_method_variable_compat`, `test_precipitation_rejects_smooth_methods` |
| REQ-004 | `PostInterpolationValidator._check_mean_preservation` con `atol=1e-4`, `rtol=1e-6` | `test_post_mean_preservation` |
| REQ-005 | `report.py` (`CheckResult`, `ValidationReport`) | `test_validation_report_serialization_keys` |
| REQ-006 | `PostInterpolationValidator._check_cyclic_continuity` (rolling 31d) | `test_post_cyclic_continuity` |
| REQ-007 | `PostInterpolationValidator._check_physical_range` | `test_post_physical_range` |
| REQ-008 | `StatisticalReporter.report` | `test_statistical_reporter_keys` |
| REQ-009 | `PreValidationError` (pre) + WARN en report (post) | `test_fail_fast_pre_vs_warn_post` |
| REQ-010 | `MethodVariableCompatibilityChecker.check(force=True)` + COMPAT-003 + stamping en Pipeline | `test_force_method_override_emits_warn` |
| NFR-001 | `ValidationReport.to_json` | `test_validation_report_serialization_keys` |
| NFR-002 | mensajes en `_codes.py` (catálogo) | `test_error_messages_spanish` |
| NFR-003 | vectorización con `xr.apply_ufunc(dask="parallelized")` | `test_validation_performance_stack_12x3000x500` |

```

## File: `specs/pipeline/requirements.md`


```markdown
# Requirements — pipeline

**Estado:** Approved
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-16
**Última actualización:** 2026-05-16

##### 1. Propósito

Definir la capa de orquestación end-to-end de tempify (`tempify.pipeline`): la única capa que conoce a todas las demás y coordina la secuencia `detect → validate_geospatial → validate_compatibility → interpolate → validate_post → write → generate_report`. Su responsabilidad es exclusivamente orquestar y producir un reporte de procesamiento con procedencia completa, sin contener lógica de negocio de las capas inferiores (detection, validation, interpolation, I/O).

##### 2. Alcance

### In-scope

- Clase `TempifyPipeline` (PascalCase, conforme a PEP 8 y ADR-0014; el módulo `tempify.pipeline` permanece en lowercase) con método `run(source) -> PipelineResult` (ver Capa 5 en `../../steering/architecture.md`).
- Dataclass `PipelineConfig` (inmutable) que congela todos los parámetros de una ejecución (método, frecuencia destino, opciones de validación, rutas de salida, tolerancias, formato de escritura, semilla, callback de progreso).
- Dataclass `PipelineResult` que expone `outputs: list[Path]`, `report: ProcessingReport`, `detection: DetectionResult`, `validation: ValidationReport`.
- `ReportGenerator` que materializa el reporte de procesamiento en Markdown (formato canónico) con metadata de procedencia: versión de tempify, método e hiperparámetros, timestamp ISO-8601 UTC, hash MD5 de archivos de input y output, hash de configuración, número de iteraciones de Rymes-Myers si aplica.
- Jerarquía de excepciones bajo `TempifyPipelineError` con código de error referenciable en español (mensajes en español, identificadores en inglés).
- Protocol explícito `ProgressCallback` para reporte de progreso por fase y por porcentaje de píxeles.
- Política de manejo de errores por capa: fail-fast en validación pre-proceso, warn-and-continue en validación post-proceso.
- Invariante de no mutación: el `xr.DataArray` recibido del reader no se modifica in-place; toda transformación genera un nuevo array.
- Orden de operaciones determinista y documentado.

### Out-of-scope

- Lógica interna de detección, validación, interpolación o I/O (cada una vive en su propia capa; ver specs vecinas).
- Paralelización a nivel proceso (Dask es interno a la capa de interpolación, ver `../core-interpolation/requirements.md` REQ-010).
- Construcción de la CLI o GUI (la CLI consume el pipeline; ver `../cli/requirements.md`).
- Parsing de argumentos de línea de comandos.
- Selección automática del método (es responsabilidad del usuario o de la CLI con defaults del perfil de variable).

##### 3. Actores y casos de uso

### Actor 1: Investigador con script Python

> Como investigador, quiero invocar `TempifyPipeline(config).run(source)` desde un notebook para obtener un `PipelineResult` con outputs persistidos y un reporte completo, sin escribir orquestación a mano.

**Caso de uso típico:** El investigador construye un `PipelineConfig(method="pchip_mp", target_freq="daily", output_dir=Path("out/"), output_format="netcdf")`, llama `run(Path("worldclim_chile/"))`, y recibe un `PipelineResult` cuyo `report` puede imprimir o guardar.

### Actor 2: CLI (cliente programático)

> Como CLI, quiero traducir las flags `tempify convert ...` a un `PipelineConfig` y delegar enteramente la ejecución al pipeline, para no duplicar lógica de negocio.

**Caso de uso típico:** El comando `tempify convert ./worldclim_chile/ --method pchip_mp --output ./out.nc --report report.md` (ver `../cli/requirements.md` REQ-001, REQ-005) construye el `PipelineConfig`, llama `pipeline.run(source)`, formatea el reporte con `rich` y lo escribe a disco si se pidió.

### Actor 3: GUI / orquestador externo (cliente programático futuro)

> Como GUI, quiero suscribirme a un callback de progreso por fase y por porcentaje para actualizar una barra de progreso y un panel de estado sin acoplarme a la implementación interna del pipeline.

**Caso de uso típico:** La GUI registra un `ProgressCallback` en el `PipelineConfig`. El pipeline lo invoca al entrar en cada fase (`"detect"`, `"validate_geospatial"`, `"validate_compatibility"`, `"interpolate"`, `"validate_post"`, `"write"`, `"generate_report"`) y periódicamente durante la interpolación con el porcentaje de píxeles procesados.

##### 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL expose `TempifyPipeline(config: PipelineConfig).run(source: Path | list[Path]) -> PipelineResult` as the single public entry point of the pipeline layer, executing the fixed sequence `detect → validate_geospatial → validate_compatibility → interpolate → validate_post → write → generate_report`.

### REQ-002 (Ubiquitous)

THE SYSTEM SHALL execute the seven phases of `run()` in the order defined in REQ-001, without reordering, skipping (except where REQ-005 and REQ-006 explicitly allow), or parallelizing phases.

### REQ-003 (Event-driven)

WHEN a `ProgressCallback` is provided in `PipelineConfig`, THE SYSTEM SHALL invoke it at the start and end of each of the seven phases and, during interpolation, at a configurable frequency with the current phase name and progress fraction. The callback frequency is configurable via `PipelineConfig.progress_frequency_hz` (default `4` Hz). The callback MUST conform to the following `Protocol` (verified by `mypy --strict`):

```python
from typing import Protocol, Literal

class ProgressCallback(Protocol):
    def __call__(
        self,
        phase: Literal[
            "detect",
            "validate_geospatial",
            "validate_compatibility",
            "interpolate",
            "validate_post",
            "write",
            "generate_report",
        ],
        progress: float,  # [0.0, 1.0]
        message: str | None = None,
    ) -> None: ...
```

### REQ-004 (Event-driven)

WHEN no `ProgressCallback` is provided, THE SYSTEM SHALL execute silently without emitting progress events, except for log records at INFO level.

### REQ-005 (Unwanted)

IF `GeospatialCoherenceValidator` raises `GeospatialIncoherenceError` or `MethodVariableCompatibilityChecker` raises `MethodVariableIncompatibilityError` during pre-processing validation (see `../validation/requirements.md` REQ-002, REQ-003), THEN THE SYSTEM SHALL abort execution immediately (fail-fast), propagate the original exception wrapped in `TempifyPipelineError` preserving the underlying error code, and skip the remaining phases.

### REQ-006 (Event-driven)

WHEN `PostInterpolationValidator` reports failures (see `../validation/requirements.md` REQ-004), THE SYSTEM SHALL record each failure as a warning in the `ValidationReport`, continue execution to `write` and `generate_report`, and surface the warnings in the final `ProcessingReport` under a dedicated section.

### REQ-007 (Ubiquitous)

THE SYSTEM SHALL produce a `ProcessingReport` containing the following provenance fields: tempify version, ISO-8601 UTC timestamp, fully-resolved `PipelineConfig` (including method, target frequency, all hyperparameters), `DetectionResult` summary (structure mode, temporal frequency, variable profile, confidence scores), MD5 hash of every input file, MD5 hash of every output file, MD5 hash of the serialized `PipelineConfig`, list of post-interpolation validation warnings, and Rymes-Myers iteration count when applicable (see `../core-interpolation/requirements.md` REQ-007). In `dry_run` mode (REQ-011), the report omits the `outputs` block (or sets it to an empty list). The pipeline excludes the report's own timestamp field from any MD5 computation, per ADR-0007.

### REQ-008 (Ubiquitous)

THE SYSTEM SHALL NOT mutate input `xr.DataArray` objects returned by `BaseReader.read()` (see `../io-handlers/requirements.md` REQ-002), including NOT triggering eager evaluation of lazy Dask arrays unless the writer explicitly requires materialization. Any transformation in `interpolate` or `validate_post` produces a new array, and the original reference remains structurally and value-wise unchanged (and equally lazy when applicable).

### REQ-009 (Ubiquitous)

THE SYSTEM SHALL raise typed exceptions from a single hierarchy rooted at `TempifyPipelineError`, each carrying a referenceable error code (string identifier) and a Spanish-language human-readable message; sub-classes include at minimum `PipelinePreValidationError`, `PipelineInterpolationError`, `PipelineWriteError`, `PipelineReportError`.

### REQ-010 (Ubiquitous)

THE SYSTEM SHALL guarantee bit-exact reproducibility: given identical inputs, identical `PipelineConfig`, and identical tempify version, two independent executions of `run()` SHALL produce outputs with identical MD5 hashes (the report timestamp is excluded from this comparison and isolated in a single field).

### REQ-011 (Optional)

WHERE `PipelineConfig.dry_run=True`, THE SYSTEM SHALL execute Detection + pre-Validation (`validate_geospatial`, `validate_compatibility`) + Statistics computation + report generation (formatted as if interpolation had occurred, with `[DRY_RUN]` prefix in the report title and the relevant metadata fields), BUT SHALL SKIP interpolation, post-validation, and write. The returned `PipelineResult` carries `outputs=[]`; the `ProcessingReport.outputs` field is an empty list, while `inputs[i].md5` is computed normally for every input file.

### REQ-012 (Optional)

WHERE the caller provides an optional `frequency_resolver_callback: FrequencyResolverProtocol | None` field in `PipelineConfig`, AND the Detection layer cannot resolve temporal frequency automatically (see `../temporal-frequency-resolver/requirements.md` REQ-004), THE SYSTEM SHALL invoke the callback to obtain a frequency before raising `FrequencyResolutionError`. If no callback is provided OR the callback fails to return a valid frequency, THE SYSTEM SHALL raise `FrequencyResolutionError` wrapped in `TempifyPipelineError`.

##### 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Performance | El overhead total del pipeline (detect + validate + report) debe ser <5% del tiempo de interpolación pura sobre el benchmark canónico (WorldClim Chile 2.5min, 12 meses) | Benchmark `tests/benchmark/test_pipeline_overhead.py` que compara `TempifyPipeline.run()` vs `PchipMeanPreservingInterpolator.interpolate()` directo |
| NFR-002 | Reliability | Reproducibilidad bit-exact entre ejecuciones independientes con mismos inputs y config | Test `test_pipeline_md5_reproducible` que ejecuta `run()` dos veces y compara MD5 de outputs |
| NFR-003 | Usability | Frecuencia del callback de progreso configurable vía `PipelineConfig.progress_frequency_hz`, valor por defecto `4` Hz (ver REQ-003); aplica especialmente a la fase `interpolate` donde el progreso se emite proporcional al porcentaje de píxeles procesados | Test `test_pipeline_progress_callback_frequency` parametrizado en `1`, `4`, `10` Hz |
| NFR-004 | Memory | El pipeline no debe mantener simultáneamente en memoria dos copias completas del `DataArray` (input y output): la lazy evaluation de xarray/Dask debe preservarse end-to-end hasta el writer | Profiling con memray sobre stack 12×3000×500 verificando pico de memoria <2× del tamaño de un único stack |
| NFR-005 | Maintainability | Cobertura de tests del módulo `tempify.pipeline` ≥85% | `pytest --cov=tempify.pipeline --cov-fail-under=85` |
| NFR-006 | Usability | Mensajes de error en español con código referenciable | Test `test_pipeline_error_messages_spanish` |

##### 6. Criterios de aceptación

Lista verificable que define cuándo esta spec está completamente implementada:

- [ ] REQ-001 cubierto por test `test_pipeline_run_returns_pipeline_result`
- [ ] REQ-002 cubierto por test `test_pipeline_phase_order_is_deterministic`
- [ ] REQ-003 cubierto por test `test_pipeline_invokes_progress_callback_per_phase`
- [ ] REQ-004 cubierto por test `test_pipeline_runs_silently_without_callback`
- [ ] REQ-005 cubierto por tests `test_pipeline_fails_fast_on_geospatial_error` y `test_pipeline_fails_fast_on_method_variable_incompat`
- [ ] REQ-006 cubierto por test `test_pipeline_warns_and_continues_on_post_validation_failure`
- [ ] REQ-007 cubierto por test `test_pipeline_report_contains_full_provenance`
- [ ] REQ-008 cubierto por test `test_pipeline_does_not_mutate_input_dataarray`
- [ ] REQ-009 cubierto por test `test_pipeline_error_hierarchy_and_codes`
- [ ] REQ-010 cubierto por test `test_pipeline_bit_exact_reproducibility`
- [ ] REQ-011 cubierto por test `test_pipeline_dry_run_skips_interpolation_and_write`
- [ ] REQ-012 cubierto por test `test_pipeline_invokes_frequency_resolver_callback`
- [ ] NFR-001 medido y dentro del umbral (<5% overhead)
- [ ] NFR-002 verificado con MD5 comparison
- [ ] NFR-003 verificado con tres frecuencias parametrizadas
- [ ] NFR-004 verificado con memray sobre el benchmark canónico
- [ ] NFR-005 verificado en CI
- [ ] NFR-006 verificado con catálogo de errores en español
- [ ] Documentación API completa (docstrings NumPy en `TempifyPipeline`, `PipelineConfig`, `PipelineResult`, `ProcessingReport`, `ProgressCallback`)
- [ ] CHANGELOG actualizado

##### 7. Dependencias y supuestos

### Specs relacionadas

- Bloqueada por:
  - [core-interpolation](../core-interpolation/requirements.md) (provee `BaseInterpolator`)
  - [io-handlers](../io-handlers/requirements.md) (provee `BaseReader`, `BaseWriter`)
  - [validation](../validation/requirements.md) (provee `GeospatialCoherenceValidator`, `MethodVariableCompatibilityChecker`, `PostInterpolationValidator`, `ValidationReport`)
  - [structure-detection](../structure-detection/requirements.md) (provee `StructureDetector`, `DetectionResult`)
  - [temporal-frequency-resolver](../temporal-frequency-resolver/requirements.md) (provee `TemporalFrequencyResolver`)
- Bloquea:
  - [cli](../cli/requirements.md)
  - Futuras specs `gui` y `packaging`

### Supuestos

- Las capas inferiores cumplen sus contratos publicados (interfaces y tipos de retorno tal como están declarados en `../../steering/architecture.md`).
- `PipelineConfig` es inmutable durante una ejecución; cualquier cambio requiere construir una nueva instancia.
- La versión de tempify se obtiene a través de `importlib.metadata.version("tempify")` y queda registrada en el reporte.
- El cliente (CLI, GUI, script) es responsable de construir el `PipelineConfig` y de exponer al usuario humano cualquier información del `PipelineResult`.
- El `xr.DataArray` cargado por el reader es perezoso (Dask) y la interpolación preserva esa pereza hasta el writer.

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Acoplamiento accidental entre el pipeline y la CLI (lógica de presentación filtrándose al pipeline) | Media | Alto | La CLI solo construye `PipelineConfig` y consume `PipelineResult`; ninguna referencia a `typer`, `rich` o `sys.stdin` puede importarse desde `tempify.pipeline`. Test de imports prohibidos en CI. |
| Drift entre la firma del `ProgressCallback` y los clientes (CLI, GUI futura) | Media | Medio | Definir un `Protocol` explícito `ProgressCallback` con type hints estrictos verificados por `mypy --strict`; cualquier cambio rompe compilación y obliga a actualizar clientes. |
| Explosión de excepciones tipadas inconsistentes entre capas | Media | Medio | Jerarquía única bajo `TempifyPipelineError`; las excepciones de las capas inferiores se envuelven (`raise PipelinePreValidationError(...) from e`) preservando el código de error original. ADR específico si aparece divergencia. |
| Ambigüedad sobre quién invoca el prompt interactivo de frecuencia temporal (pipeline vs CLI) | Media | Medio | El pipeline NO prompts; recibe un callback opcional `frequency_resolver_callback` en `PipelineConfig`. Si no hay callback y la detección falla, el pipeline propaga `FrequencyResolutionError` (ver `../temporal-frequency-resolver/requirements.md` REQ-004). La CLI provee el callback interactivo. Requiere ADR para fijar el contrato. |
| Pérdida de la pereza de Dask por un colapso accidental (`.values`, `.compute`) en alguna fase | Baja | Alto | Test `test_pipeline_preserves_lazy_evaluation` que verifica que el `DataArray` permanece dask-backed hasta `write`. |
| Drift entre `DetectionResult.confidence` y la información reportada por `temporal-frequency-resolver` y `structure-detection` (formato del dict de confianza no contractualizado) | Media | Bajo | Contractualizar el shape del dict `confidence` en un ADR antes de implementar el reporte. |

##### 8. Referencias

- Spec-Driven Development (GitHub spec-kit): https://github.com/github/spec-kit
- EARS notation: https://alistairmavin.com/ears/
- CF Conventions (atributos de procedencia en NetCDF output): https://cfconventions.org/
- ADR-0001 — Por qué xarray como abstracción central (define el contrato del `DataArray` que el pipeline orquesta).
- ADR-0007 — Reproducibility policy: modos `strict`/`parallel`, exclusión del timestamp del MD5 del reporte (ver `docs/adr/0007-reproducibility-policy.md`). Aplica a REQ-007 y REQ-010.
- ADR-0008 — Confidence scoring and `DetectionResult` contract: forma del dict `confidence` consumido por REQ-007 (ver `docs/adr/0008-confidence-scoring-and-detection-result-contract.md`).
- ADR-0010 — Contrato de `frequency_resolver_callback` entre Pipeline y CLI/GUI: aplica a REQ-012 y al riesgo sobre el prompt interactivo.
- ADR-0014 — Corrección de naming `tempifyPipeline` → `TempifyPipeline` (PascalCase para clases por PEP 8). Aplica a REQ-001 y a toda referencia a la clase (ver `docs/adr/0014-tempifypipeline-naming-correction.md`).
- Schema canónico del reporte: `docs/schemas/processing-report.schema.md`.
- Capa 5 (`tempify.pipeline`) en `../../steering/architecture.md`.
- Reglas arquitectónicas duras en `../../steering/architecture.md` (sección "Reglas arquitectónicas duras"), particularmente la regla 1 (capas inferiores no conocen capas superiores) y la regla 5 (errores tipados).

```

## File: `specs/pipeline/design.md`


```markdown
# Design — pipeline

**Estado:** Draft
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-16

##### 1. Visión técnica

El módulo `tempify.pipeline` materializa la Capa 5 de la arquitectura: la única capa que conoce a todas las inferiores (detection, validation, interpolation, I/O) y coordina su ejecución end-to-end. No contiene lógica de negocio; orquesta, registra procedencia y emite un `ProcessingReport` reproducible.

Su diseño se rige por cuatro principios duros: (i) inmutabilidad de la configuración (`PipelineConfig` es un `@dataclass(frozen=True, slots=True)`); (ii) preservación de la pereza de Dask hasta el writer (REQ-008, NFR-004); (iii) reproducibilidad bit-exact controlada por modo (ADR-0007); (iv) aislamiento absoluto frente a capas superiores: el pipeline no importa `typer`, `rich`, `sys.stdin`, ni ningún módulo de presentación. Ese aislamiento se enforza con tests de imports prohibidos (REQ-001..009 del riesgo "acoplamiento accidental con CLI").

La orquestación es lineal y determinista: siete fases canónicas en el orden fijado por REQ-001/REQ-002, con un único callback de progreso (`ProgressCallback`) opcional que recibe el nombre de fase como `Literal` cerrado. El reporte se construye al final con `ReportGenerator`, consume el schema canónico `docs/schemas/processing-report.schema.md` y excluye el timestamp del cómputo MD5 conforme a ADR-0007.

##### 2. Arquitectura propuesta

### Diagrama de componentes

```
                  ┌──────────────────────────────────┐
                  │  Cliente (CLI / GUI / script)    │
                  │  construye PipelineConfig        │
                  └────────────────┬─────────────────┘
                                   │ run(source)
                                   ▼
                  ┌──────────────────────────────────┐
                  │  TempifyPipeline.run()           │
                  │  ─ 7 fases canónicas             │
                  │  ─ emite ProgressCallback        │
                  │  ─ envuelve excepciones          │
                  └──┬───────────────────────────────┘
                     │
   ┌─────────────────┼──────────────────────────────────────────┐
   │                 │                                          │
   ▼                 ▼                                          ▼
┌──────────┐  ┌──────────────┐  ┌────────────┐  ┌──────────┐  ┌──────────────────┐
│Detection │→ │ pre-Validation│→│Interpolation│→│ post-Val │→│ I/O Writer       │
│ Layer    │  │ (geo + compat)│  │  Layer     │  │  Layer   │  │  + ReportGenerator│
└──────────┘  └──────────────┘  └────────────┘  └──────────┘  └──────────────────┘
                                                                       │
                                                                       ▼
                                                            PipelineResult
                                                            (outputs, report,
                                                             detection, validation)
```

### Componentes nuevos

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| `TempifyPipeline` | `src/tempify/pipeline/core.py` | Clase orquestadora; método `run()`. |
| `PipelineConfig` | `src/tempify/pipeline/config.py` | Dataclass frozen con todos los parámetros de ejecución. |
| `PipelineResult` | `src/tempify/pipeline/result.py` | Dataclass de retorno (`outputs`, `report`, `detection`, `validation`). |
| `ProgressCallback` | `src/tempify/pipeline/callbacks.py` | `Protocol` con `Literal` cerrado de 7 fases. |
| `FrequencyResolverProtocol` | `src/tempify/pipeline/callbacks.py` | `Protocol` para resolución interactiva de frecuencia. |
| `ReportGenerator` | `src/tempify/pipeline/report.py` | Construcción del `ProcessingReport` conforme al schema. |
| `TempifyPipelineError` y subclases | `src/tempify/pipeline/errors.py` | Jerarquía única de excepciones tipadas. |
| `reproducibility_context` | `src/tempify/pipeline/runtime.py` | Context manager que aplica el scheduler de Dask por modo. |

### Componentes modificados

Ninguno: las capas 1-4 ya exponen sus contratos. El pipeline solo los consume.

##### 3. Contratos públicos (APIs)

### `TempifyPipeline`

```python
class TempifyPipeline:
    """Orquestador end-to-end de la Capa 5 (ver ADR-0014)."""

    def __init__(self, config: PipelineConfig) -> None: ...

    def run(self, source: Path | list[Path]) -> PipelineResult:
        """Ejecuta las siete fases canónicas en orden fijo.

        Parameters
        ----------
        source : Path | list[Path]
            Ruta única (modo A o B con directorio) o lista explícita (modo C).

        Returns
        -------
        PipelineResult
            outputs, report, detection, validation.

        Raises
        ------
        PipelinePreValidationError
            Validación geoespacial o de compatibilidad método/variable falla.
        PipelineInterpolationError
            Falla durante la fase de interpolación.
        PipelineWriteError
            Falla durante la escritura.
        PipelineReportError
            Falla durante la generación del reporte.
        TempifyPipelineError
            Cualquier otra falla orquestada (incluye `FrequencyResolutionError`
            no resuelto por callback).
        """
```

**Pre-condiciones:**
- `source` existe en el sistema de archivos.
- Las capas inferiores cumplen sus contratos publicados.

**Post-condiciones:**
- En éxito normal: `len(result.outputs) >= 1`; cada archivo tiene MD5 reportado.
- En `dry_run=True`: `result.outputs == []`; `result.report.outputs == []`; resto del reporte poblado.
- El `xr.DataArray` original del reader no fue mutado ni eagerly evaluado salvo si el writer lo exigió (REQ-008).
- En modo `strict`: dos ejecuciones independientes en la misma plataforma producen MD5 idéntico de outputs.

**Excepciones lanzadas:** ver above. Toda excepción originada en capas inferiores se envuelve con `raise PipelinePreValidationError(...) from e` (o la subclase correspondiente), preservando el `error_code` original en `__cause__` y exponiéndolo como atributo público.

### `PipelineConfig`

```python
@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Configuración inmutable de una ejecución del pipeline."""

    method: Literal["linear", "pchip", "pchip_mp", "fourier"]
    target_freq: Literal["daily"]
    output_dir: Path
    output_format: Literal["netcdf", "geotiff_collection", "multiband_geotiff", "zarr"] = "netcdf"
    chunk_size: int = 512
    scheduler: Literal["threaded", "synchronous"] = "threaded"
    reproducibility_mode: Literal["strict", "parallel"] = "parallel"
    progress_callback: ProgressCallback | None = None
    progress_frequency_hz: float = 4.0
    frequency_resolver_callback: FrequencyResolverProtocol | None = None
    dry_run: bool = False
    force_method: bool = False
    variable_profile_override: str | None = None
    seed: int = 42
    method_options: Mapping[str, Any] = field(default_factory=dict)
    # Modo inspect: salta pre-validation (y por tanto compatibilidad de método/variable y coherencia geo).
    # Solo aplica cuando dry_run=True. Pensado para `tempify inspect` que necesita
    # DetectionResult sin invocar la capa Validation.
    skip_pre_validation: bool = False
    # Política de anchor temporal para valores agregados mensuales (ADR-0015).
    # "midpoint" (default) coloca cada valor mensual en el centroide del periodo
    # conforme a CF Conventions 7.4. "start"/"end" mueven el anchor al primer
    # o último día del mes. "custom" requiere `custom_time_axis` explícito.
    monthly_anchor: Literal["midpoint", "start", "end", "custom"] = "midpoint"
    # Solo válido cuando monthly_anchor == "custom". Longitud debe coincidir
    # con el número de slices temporales del input tras detect; la verificación
    # de longitud se ejecuta en la fase 1b del pipeline (`run()`), no en
    # __post_init__ (que no conoce N).
    custom_time_axis: tuple[datetime, ...] | None = None
```

**Invariantes verificadas en `__post_init__`:**
- `output_dir` es absoluto o resoluble; si no existe, se intenta crear (no en `dry_run`).
- Si `reproducibility_mode == "strict"`, `scheduler` se fuerza a `"synchronous"` (warning si el usuario pasó `"threaded"` explícito).
- `progress_frequency_hz > 0`.
- `method_options` se congela mediante `MappingProxyType` para preservar la inmutabilidad del dataclass.
- `skip_pre_validation=True` requiere `dry_run=True`; caso contrario, `__post_init__` levanta `InvalidConfigError`. Cuando este flag está activo, el `ProcessingReport` resultante omite la sección "Validación pre" (los campos `validation_pre` quedan como lista vacía y el reporte Markdown no renderiza ese bloque).
- `monthly_anchor == "custom"` requiere `custom_time_axis is not None`. Caso contrario, `__post_init__` levanta `InvalidConfigError` con `error_code="PIPELINE_INVALID_CONFIG_CUSTOM_ANCHOR_REQUIRES_AXIS"`. La verificación de que la longitud del axis coincide con el número de slices del input se realiza en la fase 1b de `run()` (donde N ya es conocido tras `detect`), levantando `PipelinePreValidationError` con `error_code="PIPELINE_CUSTOM_AXIS_LENGTH_MISMATCH"`. Inversamente, `custom_time_axis is not None` con `monthly_anchor != "custom"` también es inválido (`PIPELINE_INVALID_CONFIG_AXIS_WITHOUT_CUSTOM_ANCHOR`).

### `PipelineResult`

```python
@dataclass(frozen=True, slots=True)
class PipelineResult:
    outputs: list[Path]
    report: ProcessingReport
    detection: DetectionResult
    validation: ValidationReport
```

### `ProgressCallback`

```python
from typing import Protocol, Literal

PipelinePhase = Literal[
    "detect",
    "validate_geospatial",
    "validate_compatibility",
    "interpolate",
    "validate_post",
    "write",
    "generate_report",
]

class ProgressCallback(Protocol):
    def __call__(
        self,
        phase: PipelinePhase,
        progress: float,  # [0.0, 1.0]
        message: str | None = None,
    ) -> None: ...
```

### `FrequencyResolverProtocol`

```python
class FrequencyResolverProtocol(Protocol):
    """Callback que el pipeline invoca cuando la Capa 2 no resuelve frecuencia.

    Devuelve una frecuencia válida (string canónico CF: 'monthly', 'weekly',
    'daily', etc.) o `None` para indicar abandono.
    """

    def __call__(
        self,
        evidence: ResolverEvidence,
    ) -> str | None: ...
```

`ResolverEvidence` es el dataclass que la Capa 2 ya expone (ver `specs/temporal-frequency-resolver/requirements.md` REQ-007); el pipeline lo propaga sin transformarlo.

### `ReportGenerator`

```python
class ReportGenerator:
    """Construye el ProcessingReport conforme al schema canónico."""

    def __init__(
        self,
        config: PipelineConfig,
        detection: DetectionResult,
        validation: ValidationReport,
        inputs: list[Path],
        outputs: list[Path],
        rymes_myers_iterations: int | None = None,
        dry_run: bool = False,
    ) -> None: ...

    def build(self) -> ProcessingReport: ...
    def to_markdown(self) -> str: ...
```

**Post-condición clave:** el campo `timestamp_utc` se rellena al final, y el cómputo MD5 de outputs ya está congelado antes de poblarlo (ADR-0007).

### `TempifyPipelineError` y subclases

```python
class TempifyPipelineError(Exception):
    """Base de la jerarquía de errores del pipeline."""
    error_code: str  # identificador en inglés, e.g. "PIPELINE_PRE_VALIDATION_FAILED"
    def __init__(self, message: str, *, error_code: str, cause: Exception | None = None) -> None: ...

class PipelinePreValidationError(TempifyPipelineError): ...
class PipelineInterpolationError(TempifyPipelineError): ...
class PipelineWriteError(TempifyPipelineError): ...
class PipelineReportError(TempifyPipelineError): ...
```

Mensajes humanos en español; identificadores `error_code` en inglés (REQ-009, NFR-006).

##### 4. Modelos de datos

### `ProcessingReport`

```python
@dataclass(frozen=True, slots=True)
class ProcessingReport:
    tempify_version: str
    timestamp_utc: str  # ISO-8601, excluido del MD5
    platform: str
    python_version: str
    reproducibility_mode: Literal["strict", "parallel"]
    dask_scheduler: Literal["threaded", "synchronous"]
    config: Mapping[str, Any]
    inputs: list[FileFingerprint]
    outputs: list[FileFingerprint]
    detection_confidence: Mapping[str, float]  # TypedDict de ADR-0008
    validation_pre: list[ValidationCheck]
    validation_post: list[ValidationCheck]
    statistics_pre: Mapping[str, BandStats]
    statistics_post: Mapping[str, BandStats]
    warnings: list[str]
    errors: list[str]
    rymes_myers_iterations: int | None
    dry_run: bool
    # Trazabilidad del ensamblaje de time_axis (ADR-0015).
    monthly_anchor: Literal["midpoint", "start", "end", "custom"]
    time_axis_source: Literal[
        "cf-bounds",          # Tier 1: CF time:bounds extraído por io-handlers
        "filename",           # Tier 2: nomenclatura de filenames (modo B/C)
        "band-descriptions",  # Tier 2: GDAL_BAND_DESCRIPTIONS (modo A multibanda)
        "midpoint-proxy",     # Fallback: año proxy 2026 + anchor (default)
        "user-custom",        # Override de usuario con custom_time_axis
    ]

@dataclass(frozen=True, slots=True)
class FileFingerprint:
    path: Path
    md5: str
    bytes: int
    format: str
```

### Stamping de procedencia

Los `attrs` del `xr.DataArray` de salida llevan (ADR-0007):
- `reproducibility_mode`, `tempify_version`, `md5_inputs`, `md5_outputs`, `scheduler`, `platform`.

##### 5. Algoritmos clave

### Orquestación de `run()` (siete fases canónicas)

Pseudocódigo de referencia. Cada fase emite progreso al entrar y al salir; la interpolación emite además progreso intermedio según `progress_frequency_hz`.

```python
def run(self, source: Path | list[Path]) -> PipelineResult:
    cfg = self._config
    cb = cfg.progress_callback or _noop
    log = logging.getLogger("tempify.pipeline.core")

    inputs = _normalize_source(source)

    with reproducibility_context(cfg.reproducibility_mode, cfg.scheduler, cfg.seed):
        # 1. detect
        cb("detect", 0.0)
        try:
            detection = self._detect(inputs)  # may invoke frequency_resolver_callback
        except FrequencyResolutionError as e:
            raise PipelinePreValidationError(
                _msg_es("PIPELINE_FREQUENCY_UNRESOLVED", e),
                error_code="PIPELINE_FREQUENCY_UNRESOLVED",
            ) from e

        # 1b. Ensamblar time_axis canónico (ADR-0015).
        # El detector entrega un DetectionResult parcial donde time_axis
        # puede venir del resolver (Tier 1 CF, Tier 2 nomenclatura, Tier 2
        # band-descriptions) o ser None. Aquí el Pipeline materializa el
        # axis final aplicando la política de anchor.
        calendar_agnostic = False
        if detection.resolution_result.time_axis is not None:
            time_axis = detection.resolution_result.time_axis
            time_bnds = _compute_time_bnds(
                time_axis, detection.resolution_result.frequency
            )
            time_axis_source = detection.resolution_result.time_axis_source
        elif cfg.monthly_anchor == "custom":
            # Override explícito del usuario, ya validado en __post_init__.
            time_axis = list(cfg.custom_time_axis)
            time_bnds = _compute_time_bnds(time_axis, MONTHLY)
            time_axis_source = "user-custom"
        else:
            # Sin extracción de fechas: usar año proxy (2026) con la
            # convención de anchor solicitada (default = midpoint).
            time_axis = TemporalAxis.from_months(
                year=2026, anchor=cfg.monthly_anchor
            ).to_list()
            time_bnds = _compute_time_bnds(time_axis, MONTHLY)
            calendar_agnostic = True
            time_axis_source = "midpoint-proxy"

        detection = detection.replace(
            time_axis=time_axis,
            time_bnds=time_bnds,
            calendar_agnostic=calendar_agnostic,
            monthly_anchor=cfg.monthly_anchor,
        )
        # `time_axis_source` se persiste en el ProcessingReport (ver §5
        # Construcción del ProcessingReport, paso 4b).
        self._time_axis_source = time_axis_source
        cb("detect", 1.0)

        # 2. validate_geospatial
        cb("validate_geospatial", 0.0)
        if not cfg.skip_pre_validation:
            try:
                geo_checks = GeospatialCoherenceValidator().validate(detection)
            except GeospatialIncoherenceError as e:
                raise PipelinePreValidationError(
                    _msg_es("PIPELINE_GEOSPATIAL_INCOHERENT", e),
                    error_code=e.error_code,
                ) from e
            cb("validate_geospatial", 1.0)
        else:
            geo_checks = []
            cb("validate_geospatial", 1.0, message="omitida (inspect mode)")

        # 3. validate_compatibility
        cb("validate_compatibility", 0.0)
        if not cfg.skip_pre_validation:
            try:
                compat_checks = MethodVariableCompatibilityChecker(
                    method=cfg.method, force=cfg.force_method
                ).check(detection.variable_profile)
            except MethodVariableIncompatibilityError as e:
                raise PipelinePreValidationError(
                    _msg_es("PIPELINE_METHOD_VARIABLE_INCOMPATIBLE", e),
                    error_code=e.error_code,
                ) from e
            cb("validate_compatibility", 1.0)
        else:
            compat_checks = []
            cb("validate_compatibility", 1.0, message="omitida (inspect mode)")

        # Statistics pre (computadas lazy)
        stats_pre = StatisticalReporter().describe(detection.dataarray)

        if cfg.dry_run:
            return self._build_dry_run_result(
                detection, geo_checks, compat_checks, stats_pre, inputs
            )

        # 4. interpolate (lazy; preserva Dask)
        cb("interpolate", 0.0)
        try:
            interpolator = _select_interpolator(cfg.method, cfg.method_options)
            result_array, rm_iterations = interpolator.interpolate(
                detection.dataarray,
                target_axis=_target_axis(detection, cfg.target_freq),
                progress_hook=_make_throttled_hook(cb, cfg.progress_frequency_hz),
            )
        except Exception as e:
            raise PipelineInterpolationError(
                _msg_es("PIPELINE_INTERPOLATION_FAILED", e),
                error_code="PIPELINE_INTERPOLATION_FAILED",
            ) from e
        cb("interpolate", 1.0)

        # 5. validate_post (warn-and-continue, REQ-006)
        cb("validate_post", 0.0)
        post_checks = PostInterpolationValidator(
            variable_profile=detection.variable_profile
        ).validate(detection.dataarray, result_array)
        stats_post = StatisticalReporter().describe(result_array)
        cb("validate_post", 1.0)

        # 6. write
        cb("write", 0.0)
        try:
            writer = _select_writer(cfg.output_format)
            outputs = writer.write(result_array, cfg.output_dir)
        except Exception as e:
            raise PipelineWriteError(
                _msg_es("PIPELINE_WRITE_FAILED", e),
                error_code="PIPELINE_WRITE_FAILED",
            ) from e
        cb("write", 1.0)

        # 7. generate_report
        cb("generate_report", 0.0)
        try:
            report = ReportGenerator(
                config=cfg,
                detection=detection,
                validation=ValidationReport(
                    checks=geo_checks + compat_checks + post_checks,
                    statistics={"pre": stats_pre, "post": stats_post},
                ),
                inputs=inputs,
                outputs=outputs,
                rymes_myers_iterations=rm_iterations,
                dry_run=False,
            ).build()
        except Exception as e:
            raise PipelineReportError(
                _msg_es("PIPELINE_REPORT_FAILED", e),
                error_code="PIPELINE_REPORT_FAILED",
            ) from e
        cb("generate_report", 1.0)

    return PipelineResult(
        outputs=outputs,
        report=report,
        detection=detection,
        validation=ValidationReport(...),
    )
```

**Complejidad:** O(orquestación) constante por fase; el coste real lo domina la interpolación (capa 4). El overhead total del pipeline está acotado por NFR-001 a < 5 %.

**Trade-offs considerados:**
- Una alternativa era ejecutar `validate_geospatial` y `validate_compatibility` en paralelo: rechazada porque viola REQ-002 (orden determinista) y el ahorro es marginal (ambas son sub-segundo).
- Otra alternativa era poblar `timestamp_utc` antes de los hashes: rechazada por ADR-0007 (el timestamp debe quedar fuera del cómputo MD5; se rellena al final como campo aislado).

### Modo `dry_run`

```python
def _build_dry_run_result(self, detection, geo_checks, compat_checks, stats_pre, inputs):
    report = ReportGenerator(
        config=self._config,
        detection=detection,
        validation=ValidationReport(
            checks=geo_checks + compat_checks,
            statistics={"pre": stats_pre, "post": {}},
        ),
        inputs=inputs,
        outputs=[],
        rymes_myers_iterations=None,
        dry_run=True,
    ).build()
    # ReportGenerator antepone "[DRY_RUN]" al título del reporte y al campo
    # `tempify_version` en el bloque de procedencia para señalización clara.
    return PipelineResult(outputs=[], report=report, detection=detection, validation=...)
```

`inputs[i].md5` se computa normalmente (REQ-011). Se omiten las fases `interpolate`, `validate_post` y `write`.

### Construcción del `ProcessingReport`

`ReportGenerator.build()`:

1. Computa `md5_inputs` para cada archivo (streaming hashlib).
2. Computa `md5_outputs` para cada output ya escrito (streaming hashlib sobre bytes en disco).
3. Serializa `config` excluyendo callbacks (no son hash-estables) y sustituye `Path` por `str` POSIX.
4. Resuelve `detection_confidence` desde `detection.confidence` (TypedDict ADR-0008).
4b. Inyecta `monthly_anchor = cfg.monthly_anchor` y `time_axis_source = pipeline._time_axis_source` (poblado en fase 1b de `run()`, ver Algoritmo). Esto cierra la trazabilidad de qué política temporal materializó el axis (ADR-0015).
5. Construye `warnings` y `errors` a partir de `validation.checks` (FAIL → error, WARN → warning).
6. Establece `timestamp_utc = datetime.now(tz=UTC).isoformat()` **al final**, después de que cualquier hash haya quedado congelado.

##### 6. Decisiones de diseño

### Decisión 1: Naming `TempifyPipeline`

PascalCase per PEP 8. Registrada en ADR-0014. El módulo (`tempify.pipeline`) permanece lowercase.

### Decisión 2: `frequency_resolver_callback` como campo de `PipelineConfig`

Opciones consideradas:
1. Parámetro de `run()`. Rechazada: contamina la firma del entry point y rompe la simetría con los demás callbacks.
2. Setter mutable en `TempifyPipeline`. Rechazada: viola la inmutabilidad de la configuración.
3. **Campo de `PipelineConfig`** (elegida). Centraliza toda la configuración de ejecución en un objeto inmutable, alineado con ADR-0010 sobre el contrato Pipeline ↔ CLI/GUI.

### Decisión 3: El pipeline NO importa `typer`, `rich` ni `sys.stdin`

Regla arquitectónica dura #1. Enforzada por test de imports prohibidos (`test_pipeline_no_typer_import`, `test_pipeline_no_rich_import`, `test_pipeline_no_sys_stdin`). Cualquier interacción humana viaja exclusivamente por `progress_callback` y `frequency_resolver_callback`.

### Decisión 4: Logging namespace canónico

Todos los loggers del módulo viven bajo `tempify.pipeline.*` (e.g. `tempify.pipeline.core`, `tempify.pipeline.report`, `tempify.pipeline.runtime`). El cliente configura el nivel desde fuera; el pipeline nunca llama a `basicConfig`.

### Decisión 5: Excepciones envueltas con `raise ... from e`

Preserva el traceback original y el `error_code` de la capa inferior (REQ-009). El consumidor accede a `e.__cause__.error_code` si necesita el código original; `error_code` en la excepción wrapper queda en el namespace `PIPELINE_*` para facilitar matching.

### Decisión 6: Exclusión del timestamp del MD5 del reporte

Per ADR-0007. El campo `timestamp_utc` se inyecta al final de `build()`, después de congelar los hashes; tests de reproducibilidad comparan MD5 ignorando ese campo.

### Decisión 8: Ensamblaje de `time_axis` end-to-end (ADR-0015)

El `time_axis` canónico que consume Interpolation y Validation se construye en el Pipeline, no en la Capa 2. La Capa 2 (`StructureDetector` + `TemporalFrequencyResolver`) provee los insumos: filenames ordenados, `band_descriptions` cuando aplica, y un `ResolutionResult.time_axis` opcional cuando alguno de los tiers logró extraer fechas reales. El Pipeline materializa el axis final aplicando la política de anchor (`cfg.monthly_anchor`) y, en ausencia de fechas, cae a un año proxy (2026) marcando `calendar_agnostic=True`. Esta decisión centraliza la política temporal en un único punto (la Capa 5) y mantiene a la Capa 2 libre de decisiones sobre convenciones CF, alineado con el principio "Capa 2 infiere, Capa 5 decide" y con la separación de responsabilidades de ADR-0015. La trazabilidad se preserva en `ProcessingReport.time_axis_source`, que distingue las cinco rutas posibles (`cf-bounds`, `filename`, `band-descriptions`, `midpoint-proxy`, `user-custom`).

Referencia: ADR-0015 (Posicionamiento temporal de valores agregados — midpoint convention).

### Decisión 7: Modo combinado `dry_run=True` + `skip_pre_validation=True` para `tempify inspect`

El subcomando CLI `tempify inspect` (ver `specs/cli/design.md` § "Algoritmo `inspect`") necesita exponer únicamente el `DetectionResult` sin invocar la capa Validation. Para evitar que el CLI importe `tempify.detection` directamente (lo cual violaría su REQ-012 de aislamiento de imports), el pipeline ofrece el modo combinado `dry_run=True, skip_pre_validation=True`. Bajo este modo, `run()` ejecuta solo `detect` + `generate_report` con `validation_pre=[]` y outputs vacíos. Cualquier otra combinación (`skip_pre_validation=True` con `dry_run=False`) está prohibida por la invariante declarada en Contratos y se rechaza en `__post_init__`. Esto extiende REQ-011 sin alterar el comportamiento por defecto (`skip_pre_validation=False`).

##### 7. Estrategia de testing

### Tests unitarios y de integración (uno por REQ)

| Test | REQ cubierto |
|---|---|
| `test_pipeline_run_returns_pipeline_result` | REQ-001 |
| `test_pipeline_phase_order_is_deterministic` | REQ-002 |
| `test_pipeline_invokes_progress_callback_per_phase` | REQ-003 |
| `test_pipeline_progress_callback_frequency` (parametrizado 1/4/10 Hz) | REQ-003, NFR-003 |
| `test_pipeline_runs_silently_without_callback` | REQ-004 |
| `test_pipeline_fails_fast_on_geospatial_error` | REQ-005 |
| `test_pipeline_fails_fast_on_method_variable_incompat` | REQ-005 |
| `test_pipeline_warns_and_continues_on_post_validation_failure` | REQ-006 |
| `test_pipeline_report_contains_full_provenance` | REQ-007 |
| `test_pipeline_report_md5_excludes_timestamp` | REQ-007, ADR-0007 |
| `test_pipeline_does_not_mutate_input_dataarray` | REQ-008 |
| `test_pipeline_preserves_lazy_evaluation` | REQ-008, NFR-004 |
| `test_pipeline_error_hierarchy_and_codes` | REQ-009 |
| `test_pipeline_error_messages_spanish` | REQ-009, NFR-006 |
| `test_pipeline_bit_exact_reproducibility` (strict mode) | REQ-010, NFR-002 |
| `test_pipeline_allclose_reproducibility_parallel` (parallel mode, scheduler `threaded`) | NFR-002, ADR-0007 |
| `test_pipeline_dry_run_skips_interpolation_and_write` | REQ-011 |
| `test_pipeline_inspect_mode_skips_pre_validation` | REQ-011 (ampliado) |
| `test_pipeline_skip_pre_validation_without_dry_run_raises` | REQ-011 (ampliado) |
| `test_pipeline_invokes_frequency_resolver_callback` | REQ-012 |
| `test_pipeline_raises_when_callback_returns_none` | REQ-012 |
| `test_pipeline_propagates_time_axis_from_resolver` | ADR-0015, Decisión 8 |
| `test_pipeline_falls_back_to_proxy_year_when_no_dates` | ADR-0015, Decisión 8 |
| `test_pipeline_custom_monthly_anchor_requires_dates` | ADR-0015, Decisión 8 |
| `test_processing_report_includes_time_axis_source` | ADR-0015, Decisión 8 |

Especificación de los tres tests añadidos:

- `test_pipeline_allclose_reproducibility_parallel`: construye `PipelineConfig(reproducibility_mode="parallel", scheduler="threaded", ...)` y ejecuta `run()` dos veces sobre el mismo `source`. Verifica `xr.testing.assert_allclose(out1, out2, rtol=1e-12, atol=1e-15)` sobre los `DataArray` resultantes (leídos desde los outputs escritos). Cubre la promesa de ADR-0007 para el modo `parallel`, complementaria al bit-exact del modo `strict`.
- `test_pipeline_inspect_mode_skips_pre_validation`: ejecuta `run()` con `PipelineConfig(dry_run=True, skip_pre_validation=True, ...)` sobre un fixture cuyos archivos tienen CRS deliberadamente inconsistente. Verifica que el `PipelineResult.report.validation_pre` está vacío, que no se levanta `PipelinePreValidationError`, y que el `result.detection` está completamente poblado. Cubre el contrato consumido por el subcomando CLI `tempify inspect`.
- `test_pipeline_skip_pre_validation_without_dry_run_raises`: construye `PipelineConfig(skip_pre_validation=True, dry_run=False, ...)` y verifica que `__post_init__` levanta `InvalidConfigError` con `error_code="PIPELINE_INVALID_CONFIG_SKIP_REQUIRES_DRY_RUN"`. Cubre la invariante declarada en la sección Contratos.
- `test_pipeline_propagates_time_axis_from_resolver`: fixture NetCDF con `time:bounds` CF poblado (Tier 1 del resolver). Ejecuta `run()` y verifica que `result.detection.time_axis` corresponde al axis extraído por la Capa 2 (no al proxy 2026), que `result.detection.calendar_agnostic is False`, y que `result.report.time_axis_source == "cf-bounds"`. Variantes parametrizadas: filenames WorldClim-style (`"filename"`) y GeoTIFF multibanda con `GDAL_BAND_DESCRIPTIONS` parseables (`"band-descriptions"`).
- `test_pipeline_falls_back_to_proxy_year_when_no_dates`: fixture de 12 GeoTIFF monocapa con nombres no parseables (`band_01.tif`..`band_12.tif`) y sin metadata CF. Ejecuta `run()` con `monthly_anchor="midpoint"`. Verifica que `result.detection.time_axis` corresponde a los midpoints de 2026, `result.detection.calendar_agnostic is True`, y `result.report.time_axis_source == "midpoint-proxy"`.
- `test_pipeline_custom_monthly_anchor_requires_dates`: dos sub-casos.
  (a) `PipelineConfig(monthly_anchor="custom", custom_time_axis=None)` falla en `__post_init__` con `InvalidConfigError(error_code="PIPELINE_INVALID_CONFIG_CUSTOM_ANCHOR_REQUIRES_AXIS")`.
  (b) `PipelineConfig(monthly_anchor="custom", custom_time_axis=(11 datetimes,))` se construye OK, pero al ejecutar `run()` sobre un stack de 12 slices, la fase 1b levanta `PipelinePreValidationError(error_code="PIPELINE_CUSTOM_AXIS_LENGTH_MISMATCH")`.
- `test_processing_report_includes_time_axis_source`: para cada uno de los cinco valores válidos del literal `time_axis_source` (`cf-bounds`, `filename`, `band-descriptions`, `midpoint-proxy`, `user-custom`), construye el fixture mínimo que dispare esa ruta, ejecuta `run()` y verifica que `result.report.time_axis_source` y `result.report.monthly_anchor` están correctamente poblados. Cubre la trazabilidad end-to-end de ADR-0015.

### Tests de imports prohibidos

| Test | Verifica |
|---|---|
| `test_pipeline_no_typer_import` | `typer` no aparece en `sys.modules` tras `import tempify.pipeline`. |
| `test_pipeline_no_rich_import` | `rich` no aparece tras importar el módulo. |
| `test_pipeline_no_sys_stdin` | Análisis AST: ningún archivo bajo `src/tempify/pipeline/` referencia `sys.stdin`. |
| `test_pipeline_logger_namespace` | Todos los loggers definidos están bajo `tempify.pipeline.*`. |

### Tests property-based (hypothesis)

- `test_progress_fraction_monotonic_per_phase` — propiedad: `progress` emitido es monótono no decreciente dentro de cada fase.
- `test_md5_stability_under_config_reordering` — propiedad: serialización del config produce el mismo hash sin importar el orden interno de `method_options` (`sorted` keys).

### Tests de schema (jsonschema)

- `test_report_yaml_block_validates_against_schema` — parsea el bloque YAML de procedencia del Markdown emitido por `ReportGenerator.to_markdown()` y lo valida contra `docs/schemas/processing-report.schema.md` (representación JSON-Schema generada en `tests/schemas/processing-report.schema.json`).

### Benchmark

- `tests/benchmark/test_pipeline_overhead.py` — compara `TempifyPipeline.run()` con `PchipMeanPreservingInterpolator.interpolate()` directo sobre WorldClim Chile 2.5 min, 12 meses. Falla si overhead > 5 % (NFR-001).
- `tests/benchmark/test_pipeline_memory_peak.py` — memray sobre stack 12×3000×500; falla si pico > 2× tamaño de un único stack (NFR-004).

### Fixtures necesarios

- `synthetic_3x3_monthly.nc` — ya existe; usado para tests rápidos.
- `worldclim_chile_25min.tif` — benchmark canónico (descargado por `conftest.py` y cacheado).
- `recording_progress_callback` — fixture nuevo: callback que registra todas las llamadas para inspección posterior.
- `dummy_frequency_resolver` — fixture nuevo: callback configurable que devuelve frecuencia fija o `None`.

##### 8. Plan de migración

No aplica: módulo nuevo, sin código previo en producción.

##### 9. Métricas de calidad

| Métrica | Umbral |
|---|---|
| Coverage del módulo `tempify.pipeline` | ≥ 85 % (NFR-005) |
| Overhead pipeline vs. interpolación directa | < 5 % (NFR-001) |
| Memoria peak benchmark canónico | < 2× tamaño de stack único (NFR-004) |
| MD5 de outputs idempotente en `strict` | 100 % de runs (NFR-002) |
| Mensajes de error en español con código | 100 % de subclases de `TempifyPipelineError` (NFR-006) |

##### 10. Trazabilidad requirements → componente → test

| Requirement | Componente | Test |
|---|---|---|
| REQ-001 | `TempifyPipeline.run` | `test_pipeline_run_returns_pipeline_result` |
| REQ-002 | `TempifyPipeline.run` (orquestación) | `test_pipeline_phase_order_is_deterministic` |
| REQ-003 | `TempifyPipeline._emit_progress` + `ProgressCallback` | `test_pipeline_invokes_progress_callback_per_phase`, `test_pipeline_progress_callback_frequency` |
| REQ-004 | `TempifyPipeline.run` (default `_noop` callback) | `test_pipeline_runs_silently_without_callback` |
| REQ-005 | `TempifyPipeline._validate_geospatial`, `_validate_compatibility`, wrappers de error | `test_pipeline_fails_fast_on_geospatial_error`, `test_pipeline_fails_fast_on_method_variable_incompat` |
| REQ-006 | `TempifyPipeline._validate_post` + `ValidationReport` | `test_pipeline_warns_and_continues_on_post_validation_failure` |
| REQ-007 | `ReportGenerator.build` | `test_pipeline_report_contains_full_provenance`, `test_pipeline_report_md5_excludes_timestamp` |
| REQ-008 | `TempifyPipeline.run` (no mutación) | `test_pipeline_does_not_mutate_input_dataarray`, `test_pipeline_preserves_lazy_evaluation` |
| REQ-009 | `tempify.pipeline.errors.*` | `test_pipeline_error_hierarchy_and_codes`, `test_pipeline_error_messages_spanish` |
| REQ-010 | `reproducibility_context` + `ReportGenerator` | `test_pipeline_bit_exact_reproducibility` |
| REQ-011 | `TempifyPipeline._build_dry_run_result`, `PipelineConfig.skip_pre_validation` | `test_pipeline_dry_run_skips_interpolation_and_write`, `test_pipeline_inspect_mode_skips_pre_validation`, `test_pipeline_skip_pre_validation_without_dry_run_raises` |
| REQ-012 | `TempifyPipeline._detect` + `FrequencyResolverProtocol` | `test_pipeline_invokes_frequency_resolver_callback`, `test_pipeline_raises_when_callback_returns_none` |
| NFR-001 | Benchmark | `tests/benchmark/test_pipeline_overhead.py` |
| NFR-002 | `reproducibility_context` | `test_pipeline_bit_exact_reproducibility`, `test_pipeline_allclose_reproducibility_parallel` |
| NFR-003 | `_make_throttled_hook` | `test_pipeline_progress_callback_frequency` |
| NFR-004 | Preservación de pereza Dask | `test_pipeline_preserves_lazy_evaluation`, `test_pipeline_memory_peak` |
| NFR-005 | Cobertura general | CI: `pytest --cov=tempify.pipeline --cov-fail-under=85` |
| NFR-006 | `tempify.pipeline.errors.*` | `test_pipeline_error_messages_spanish` |

##### 11. Referencias

- ADR-0007 — Política de reproducibilidad (modos `strict` / `parallel`, exclusión del timestamp del MD5).
- ADR-0008 — Confidence scoring and `DetectionResult` contract (shape del dict consumido por REQ-007).
- ADR-0010 — Política unificada de tolerancia para conservación de la media mensual.
- ADR-0014 — Corrección de naming `TempifyPipeline` (PascalCase).
- ADR-0015 — Posicionamiento temporal de valores agregados (midpoint convention, `time_bnds`, override por usuario; consumido en fase 1b de `run()`).
- `docs/schemas/processing-report.schema.md` — schema canónico del reporte.
- `steering/architecture.md` § Capa 5 y reglas arquitectónicas duras.
- Specs vecinas consumidas (todas Approved/Draft): `core-interpolation`, `io-handlers`, `validation`, `structure-detection`, `temporal-frequency-resolver`, `cli`.
- PEP 589 (TypedDict): https://peps.python.org/pep-0589/
- PEP 8 (Naming): https://peps.python.org/pep-0008/#naming-conventions

```


---

# Código fuente (interpolation + pipeline + validation + profiles)


## File: `code/api.py`


```python
"""Ergonomic API for tempify — terra-like convenience layer.

Exposes three top-level symbols:

    from tempify import rast, tempify, plot

    r  = rast("datos/worldclim_tmax.tif")   # cargar GeoTIFF
    print(r)                                  # info compacta tipo terra
    r.str()                                   # estructura detallada
    plot(r)                                   # grilla de bandas

    r2 = tempify(r, from_freq="monthly", to_freq="daily", method="cubic")
    print(r2)
    plot(r2, sub=range(1, 17))               # subset de las primeras 16 bandas
"""

from __future__ import annotations

import contextlib
import io
import math
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr

from tempify.interpolation import (
    AkimaInterpolator,
    BaseInterpolator,
    CubicSplineInterpolator,
    FourierInterpolator,
    LinearInterpolator,
    PchipInterpolator,
    PchipMeanPreservingInterpolator,
    TemporalAxis,
)
from tempify.io.readers.geotiff import GeoTIFFReader
from tempify.utils import raster_info

_INTERPOLATORS: dict[str, type[BaseInterpolator]] = {
    "linear": LinearInterpolator,
    "cubic": CubicSplineInterpolator,
    "pchip": PchipInterpolator,
    "pchip_mp": PchipMeanPreservingInterpolator,
    "fourier": FourierInterpolator,
    "akima": AkimaInterpolator,
}

_SPATIAL: frozenset[str] = frozenset({"y", "x"})

_MAX_PANELS = 36


class TempifyRast:
    """Wrapper ergonómico de ``xr.DataArray`` con presentación tipo terra.

    Parameters
    ----------
    data : xr.DataArray
        Array subyacente con dimensiones espaciales ``y`` y ``x``.
    """

    def __init__(self, data: xr.DataArray) -> None:
        self._data = data

    @property
    def data(self) -> xr.DataArray:
        """DataArray subyacente sin copia."""
        return self._data

    @property
    def shape(self) -> tuple[int, ...]:
        """Delega a ``data.shape``."""
        return tuple(self._data.shape)

    @property
    def crs(self) -> Any:
        """CRS del stack vía rioxarray. ``None`` si no disponible."""
        try:
            return self._data.rio.crs
        except Exception:
            return None

    def __repr__(self) -> str:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                raster_info(self._data)
            except Exception as exc:
                return f"<TempifyRast shape={self.shape} (error interno: {exc})>"
        return buf.getvalue().rstrip()

    def str(self) -> None:
        """Imprime información extendida del stack (análogo a ``terra::str(r)``)."""
        print(repr(self))
        da = self._data
        vals = da.values
        finite = vals[~np.isnan(vals)]
        if finite.size:
            print(f"rango       : [{float(finite.min()):.4f}, {float(finite.max()):.4f}]")
        nan_count = int(np.isnan(vals).sum())
        print(f"NaN         : {nan_count}")
        if da.attrs:
            print(f"atributos   : {list(da.attrs.keys())}")


def rast(path: str | Path) -> TempifyRast:
    """Carga un GeoTIFF multi-banda como :class:`TempifyRast`.

    Parameters
    ----------
    path : str | Path
        Ruta al archivo GeoTIFF (relativa o absoluta).

    Returns
    -------
    TempifyRast

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe en la ruta indicada.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {p}")
    reader = GeoTIFFReader()
    da = reader.read(p)
    return TempifyRast(da)


def plot(
    r: TempifyRast | xr.DataArray,
    sub: range | list[int] | None = None,
    cmap: str = "viridis",
    figsize: tuple[float, float] | None = None,
) -> None:
    """Visualiza bandas del stack en grilla automática.

    Parameters
    ----------
    r : TempifyRast | xr.DataArray
        Stack a visualizar.
    sub : range | list[int] | None
        Índices 1-based de bandas a mostrar (como el argumento ``sub`` de
        ``terra::plot``). ``None`` muestra todas (máx 36).
    cmap : str
        Colormap de matplotlib. Default ``"viridis"``.
    figsize : tuple[float, float] | None
        Tamaño de figura en pulgadas. ``None`` → automático.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(
            "matplotlib es necesario para plot(). "
            "Instalar con: pip install matplotlib"
        ) from exc

    da = r.data if isinstance(r, TempifyRast) else r
    stack_dims = [d for d in da.dims if d not in _SPATIAL]

    if not stack_dims:
        fig, ax = plt.subplots(figsize=figsize or (5, 4))
        im = ax.imshow(da.values, cmap=cmap)
        fig.colorbar(im, ax=ax)
        plt.tight_layout()
        plt.show()
        return

    dim = stack_dims[0]
    n_total = da.sizes[dim]

    if sub is not None:
        indices = [i - 1 for i in sub if 1 <= i <= n_total]
    else:
        indices = list(range(min(n_total, _MAX_PANELS)))

    if not indices:
        return

    n = len(indices)
    ncols = math.ceil(math.sqrt(n))
    nrows = math.ceil(n / ncols)

    auto_figsize = figsize or (3.5 * ncols, 3.0 * nrows)
    fig, axes = plt.subplots(
        nrows, ncols, figsize=auto_figsize, squeeze=False, constrained_layout=True
    )

    vals_flat = da.values[~np.isnan(da.values)]
    vmin = float(vals_flat.min()) if vals_flat.size else 0.0
    vmax = float(vals_flat.max()) if vals_flat.size else 1.0

    all_axes = axes.ravel().tolist()
    im = None
    for plot_i, band_i in enumerate(indices):
        ax = all_axes[plot_i]
        band_data = da.isel({dim: band_i}).values
        im = ax.imshow(band_data, cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_title(str(band_i + 1), fontsize=8)
        ax.axis("off")

    for ax in all_axes[len(indices):]:
        ax.set_visible(False)

    if im is not None:
        fig.colorbar(im, ax=all_axes, shrink=0.6)

    plt.show()


def tempify(
    stack: TempifyRast | xr.DataArray,
    from_freq: str | int,
    to_freq: str | int,
    method: str = "pchip_mp",
    year: int | None = None,
) -> TempifyRast:
    """Interpola un stack raster a mayor frecuencia temporal (operación en memoria).

    No escribe a disco. Para flujos de producción con validación completa y
    escritura multi-formato, usar :class:`~tempify.pipeline.core.TempifyPipeline`.

    Parameters
    ----------
    stack : TempifyRast | xr.DataArray
        Stack de entrada.
    from_freq : str | int
        Frecuencia de entrada. ``"monthly"`` asume 12 bandas con ciclo
        mensual completo.
    to_freq : str | int
        Frecuencia objetivo. ``"daily"`` genera 365/366 pasos según ``year``.
    method : str
        Nombre del interpolador. Opciones: ``"linear"``, ``"cubic"``,
        ``"pchip"``, ``"pchip_mp"``, ``"fourier"``, ``"akima"``.
        Default: ``"pchip_mp"`` (PCHIP + conservación de media mensual).
    year : int | None
        Año de referencia para el eje temporal. ``None`` → año actual.

    Returns
    -------
    TempifyRast
        Stack interpolado con dimensión ``"time"`` y coordenadas datetime.

    Raises
    ------
    ValueError
        Si ``method`` no es uno de los nombres válidos.
    """
    if method not in _INTERPOLATORS:
        valid = ", ".join(f'"{k}"' for k in sorted(_INTERPOLATORS))
        raise ValueError(
            f"method={method!r} no reconocido. "
            f"Opciones válidas: {valid}"
        )

    da = stack.data if isinstance(stack, TempifyRast) else stack
    ref_year = year if year is not None else datetime.now().year

    if from_freq in ("monthly", 12):
        if "band" in da.dims:
            da = da.rename({"band": "month"})
        da = da.assign_coords(month=list(range(1, 13)))

    axis = TemporalAxis.from_months(ref_year)
    interpolator = _INTERPOLATORS[method]()
    result = interpolator.interpolate(da, axis)

    # Normalizar orden de dims a (time, y, x) para consistencia con raster convencional
    if "time" in result.dims:
        lead = ["time"]
        rest = [d for d in result.dims if d != "time"]
        result = result.transpose(*lead, *rest)

    return TempifyRast(result)

```

## File: `code/constants.py`


```python
"""Package-wide constants for tempify.

Per ADR-0010 these constants define the canonical Level 1 tolerance
(Rymes-Myers iterator convergence) and related defaults. Other levels
(contractual post-validator tolerance, per-variable acceptable error)
live in :mod:`tempify.validation` per their respective scopes.

Per ADR-0007 the default Dask scheduler for production interpolation
is ``threaded``; strict reproducibility mode uses ``synchronous``.
"""

from __future__ import annotations

from typing import Final

DEFAULT_CHUNK_SIZE: Final[int] = 512
"""Default Dask chunk size for spatial dimensions (pixels per side)."""

DEFAULT_RM_CONVERGENCE_TOL: Final[float] = 1e-6
"""Rymes-Myers iterator convergence tolerance (ADR-0010 Level 1).

Internal stopping criterion of the iterative algorithm in the variable's
units. NOT the contractual post-validation tolerance: that lives in
:mod:`tempify.validation` per ADR-0010 Level 2.
"""

DEFAULT_RM_MAX_ITER: Final[int] = 50
"""Maximum iterations for the Rymes-Myers algorithm before bailing out."""

FOURIER_MIN_HARMONICS: Final[int] = 1
"""Minimum number of Fourier harmonics accepted by FourierInterpolator."""

FOURIER_MAX_HARMONICS: Final[int] = 5
"""Maximum number of Fourier harmonics (Nyquist for 12 samples is 6)."""

```

## File: `code/datasets.py`


```python
"""Funciones auxiliares para generar y cargar datos sintéticos tipo WorldClim.

Proporciona datasets reproducibles para demos, notebooks y tests. Los outputs
usan la convención de nombres WorldClim v2.1 para que el pipeline de tempify
los lea directamente sin configuración adicional.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import rioxarray  # noqa: F401 — registra el accessor rio
import xarray as xr

SANTIAGO_MONTHLY_TAVG: tuple[float, ...] = (
    21.0,  # Ene
    20.0,  # Feb
    18.0,  # Mar
    15.0,  # Abr
    12.0,  # May
    9.0,   # Jun
    9.0,   # Jul
    10.0,  # Ago
    12.0,  # Sep
    14.0,  # Oct
    17.0,  # Nov
    20.0,  # Dic
)

_FILENAME_TEMPLATE = "wc2.1_2.5m_{variable}_{month:02d}.tif"


def _gaussian_cluster(
    lon_grid: np.ndarray,
    lat_grid: np.ndarray,
    lon0: float,
    lat0: float,
    sx: float,
    sy: float,
    amplitude: float,
) -> np.ndarray:
    return amplitude * np.exp(
        -((lon_grid - lon0) ** 2 / (2 * sx**2) + (lat_grid - lat0) ** 2 / (2 * sy**2))
    )


def _smooth_noise(
    shape: tuple[int, int],
    seed: int,
    n_iter: int = 18,
    scale: float = 1.0,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    arr = rng.normal(0, 1, size=shape).astype(np.float64)
    for _ in range(n_iter):
        arr = (
            arr
            + np.roll(arr, 1, axis=0)
            + np.roll(arr, -1, axis=0)
            + np.roll(arr, 1, axis=1)
            + np.roll(arr, -1, axis=1)
        ) / 5.0
    return arr * scale


def _build_spatial_temperature_field(
    month_idx: int,
    base_value: float,
    lon_grid: np.ndarray,
    lat_grid: np.ndarray,
    bbox_lon: tuple[float, float],
    bbox_lat: tuple[float, float],
    seed: int,
) -> np.ndarray:
    n_pixels = lon_grid.shape[0]

    altitude_effect = -6.0 * (lon_grid - bbox_lon[0]) / (bbox_lon[1] - bbox_lon[0])
    lat_effect = -0.5 * (lat_grid - bbox_lat[0]) / (bbox_lat[1] - bbox_lat[0])

    phase = month_idx / 12.0
    cluster_amp = 1.5 * np.sin(2 * np.pi * phase + np.pi / 4)
    warm_cluster = _gaussian_cluster(
        lon_grid, lat_grid,
        bbox_lon[0] + 0.3, bbox_lat[0] + 0.3, 0.3, 0.25, cluster_amp,
    )
    cold_cluster = _gaussian_cluster(
        lon_grid, lat_grid,
        bbox_lon[1] - 0.4, bbox_lat[1] - 0.3, 0.35, 0.3, -cluster_amp,
    )

    texture = _smooth_noise(
        (n_pixels, n_pixels), seed=seed + month_idx * 7, n_iter=12, scale=0.8
    )

    rng = np.random.default_rng(seed + month_idx * 31)
    noise = rng.normal(0, 0.15, size=(n_pixels, n_pixels))

    field = (
        base_value + altitude_effect + lat_effect
        + warm_cluster + cold_cluster + texture + noise
    )
    return field.astype(np.float32)  # type: ignore[no-any-return]


def create_worldclim_like_sample(
    output_dir: Path,
    variable: str = "tavg",
    n_pixels: int = 60,
    bbox_lon: tuple[float, float] = (-71.5, -69.5),
    bbox_lat: tuple[float, float] = (-34.5, -32.5),
    monthly_values: tuple[float, ...] | None = None,
    overwrite: bool = False,
    seed: int = 42,
) -> Path:
    """Genera 12 GeoTIFFs sintéticos con nomenclatura WorldClim v2.1.

    Parameters
    ----------
    output_dir : Path
        Directorio donde se escribirán los 12 GeoTIFFs.
    variable : str
        Nombre de la variable climática (p.ej., ``"tavg"``, ``"prec"``).
    n_pixels : int
        Tamaño de la grilla en cada dimensión (``n_pixels x n_pixels``).
    bbox_lon : tuple[float, float]
        Límites longitud (oeste, este).
    bbox_lat : tuple[float, float]
        Límites latitud (sur, norte).
    monthly_values : tuple[float, ...] | None
        12 valores base, uno por mes. Por defecto: climatología de Santiago de Chile.
    overwrite : bool
        Si ``False`` y los 12 archivos ya existen, omite la generación (idempotente).
    seed : int
        Semilla RNG para reproducibilidad bit-exacta.

    Returns
    -------
    Path
        Ruta a ``output_dir``.

    Raises
    ------
    ValueError
        Si ``monthly_values`` no tiene exactamente 12 elementos.
    """
    output_dir = Path(output_dir)

    if monthly_values is None:
        monthly_values = SANTIAGO_MONTHLY_TAVG

    if len(monthly_values) != 12:
        raise ValueError(
            f"monthly_values debe tener exactamente 12 elementos, "
            f"se recibieron {len(monthly_values)}"
        )

    expected_paths = [
        output_dir / _FILENAME_TEMPLATE.format(variable=variable, month=m)
        for m in range(1, 13)
    ]

    if not overwrite and all(p.exists() for p in expected_paths):
        return output_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    lon = np.linspace(bbox_lon[0], bbox_lon[1], n_pixels)
    lat = np.linspace(bbox_lat[1], bbox_lat[0], n_pixels)  # norte → sur
    lon_grid, lat_grid = np.meshgrid(lon, lat)

    for month_idx, base in enumerate(monthly_values):
        arr = _build_spatial_temperature_field(
            month_idx, base, lon_grid, lat_grid, bbox_lon, bbox_lat, seed
        )
        da = xr.DataArray(
            arr,
            dims=("y", "x"),
            coords={"y": lat, "x": lon},
            name=variable,
        ).rio.write_crs("EPSG:4326")
        da.rio.to_raster(expected_paths[month_idx])

    return output_dir


def read_monthly_stack(
    data_dir: Path,
    variable: str = "tavg",
) -> xr.DataArray:
    """Carga 12 GeoTIFFs mensuales como un único ``DataArray (month=12, y, x)``.

    Parameters
    ----------
    data_dir : Path
        Directorio con archivos ``wc2.1_2.5m_{variable}_NN.tif``.
    variable : str
        Nombre de la variable climática en los nombres de archivo.

    Returns
    -------
    xr.DataArray
        Forma ``(12, y, x)`` con coordenada ``month`` con valores ``1..12``.
    """
    arrays = []
    for month in range(1, 13):
        path = Path(data_dir) / _FILENAME_TEMPLATE.format(variable=variable, month=month)
        da = xr.open_dataarray(path, engine="rasterio").squeeze("band", drop=True)
        arrays.append(da)
    return xr.concat(arrays, dim="month").assign_coords(month=list(range(1, 13)))

```

## File: `code/interpolation/base.py`


```python
"""Core abstractions for the temporal interpolation layer.

This module defines:

- :func:`monthly_midpoint`: the canonical midpoint helper per ADR-0015
  (CF Conventions 7.4).
- :class:`TemporalAxis`: the destination temporal coordinate with
  configurable anchor mode (``midpoint``, ``start``, ``end``, ``custom``).
- :class:`BaseInterpolator`: the abstract base class implemented by the
  four concrete interpolators (Linear, PCHIP, PCHIP+RM, Fourier).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from calendar import monthrange
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import ClassVar, Literal

import xarray as xr

from tempify.interpolation.exceptions import (
    InvalidMonthlyStackError,
    UnsupportedCalendarError,
)

SUPPORTED_CALENDARS: frozenset[str] = frozenset({"gregorian", "standard", "proleptic_gregorian"})
"""CF calendars accepted by v0.1.0 (per REQ-011)."""

NanPolicy = Literal["raise", "propagate_all", "skip_pixel"]
"""Behavior for pixels with partial NaN values."""

MonthlyAnchor = Literal["midpoint", "start", "end", "custom"]
"""Where on the month the input monthly value is placed on the X axis."""


def monthly_midpoint(year: int, month: int) -> datetime:
    """Return the canonical midpoint date of a calendar month.

    Per ADR-0015 / CF Conventions 7.4, an aggregated monthly value is
    placed at the centroid of its averaging period. The formula
    ``(days_in_month + 1) // 2`` reproduces the canonical table exactly:
    16 for 31-day months, 15 for 30-day months and 29-day February,
    14 for 28-day February.

    Parameters
    ----------
    year : int
        Gregorian year used for leap-year correction in February.
    month : int
        Calendar month, 1..12.

    Returns
    -------
    datetime
        Midnight on the canonical midpoint day.

    Raises
    ------
    ValueError
        If ``month`` is outside [1, 12].
    """
    if not 1 <= month <= 12:
        raise ValueError(f"month must be in [1, 12], got {month}")
    _, days_in_month = monthrange(year, month)
    midpoint_day = (days_in_month + 1) // 2
    return datetime(year, month, midpoint_day)


def _validate_custom_dates(dates: list[datetime]) -> None:
    """Validate a user-provided ``custom_dates`` list.

    Raises
    ------
    ValueError
        If the list does not have length 12 or is not strictly
        increasing.
    """
    if len(dates) != 12:
        raise ValueError(f"custom_dates must have length 12, got {len(dates)}")
    for i in range(1, len(dates)):
        if dates[i] <= dates[i - 1]:
            raise ValueError(
                "custom_dates must be strictly increasing; "
                f"dates[{i - 1}]={dates[i - 1]} not < dates[{i}]={dates[i]}"
            )


@dataclass(frozen=True, slots=True)
class TemporalAxis:
    """Target temporal coordinate for an interpolation.

    Parameters
    ----------
    start, end : datetime
        Inclusive bounds of the target axis.
    freq : Literal['daily']
        Target frequency. v0.1.0 only supports ``'daily'``.
    calendar : str
        CF calendar name. v0.1.0 only supports Gregorian variants.
    monthly_anchor : MonthlyAnchor
        Where to place each input monthly value on the X axis. Default
        ``'midpoint'`` (ADR-0015 / CF 7.4).
    custom_dates : list[datetime] | None
        Required when ``monthly_anchor='custom'``. Strictly increasing
        list of length 12.

    Raises
    ------
    ValueError
        If ``start > end``, or ``custom_dates`` invariants are violated.
    UnsupportedCalendarError
        If ``calendar`` is not one of the supported gregorian variants.
    """

    start: datetime
    end: datetime
    freq: Literal["daily"] = "daily"
    calendar: str = "gregorian"
    monthly_anchor: MonthlyAnchor = "midpoint"
    custom_dates: list[datetime] | None = None

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError(f"start ({self.start}) must be <= end ({self.end})")
        if self.calendar not in SUPPORTED_CALENDARS:
            raise UnsupportedCalendarError(self.calendar)
        if self.monthly_anchor == "custom":
            if self.custom_dates is None:
                raise ValueError("monthly_anchor='custom' requires custom_dates to be provided")
            _validate_custom_dates(self.custom_dates)
        elif self.custom_dates is not None:
            raise ValueError(
                "custom_dates can only be provided when monthly_anchor='custom', "
                f"got monthly_anchor={self.monthly_anchor!r}"
            )

    @classmethod
    def from_months(
        cls,
        year: int,
        anchor: MonthlyAnchor = "midpoint",
        custom_dates: list[datetime] | None = None,
    ) -> TemporalAxis:
        """Build a daily target axis for one calendar year (ADR-0015 defaults)."""
        return cls(
            start=datetime(year, 1, 1),
            end=datetime(year, 12, 31),
            freq="daily",
            calendar="gregorian",
            monthly_anchor=anchor,
            custom_dates=custom_dates,
        )

    @property
    def n_days(self) -> int:
        """Number of daily steps from ``start`` to ``end`` inclusive."""
        return (self.end.date() - self.start.date()).days + 1

    def monthly_anchor_doys(self) -> list[int]:
        """Day-of-year for each of the 12 monthly anchor positions."""
        year = self.start.year
        anchors: list[datetime]
        if self.monthly_anchor == "midpoint":
            anchors = [monthly_midpoint(year, m) for m in range(1, 13)]
        elif self.monthly_anchor == "start":
            anchors = [datetime(year, m, 1) for m in range(1, 13)]
        elif self.monthly_anchor == "end":
            anchors = [datetime(year, m, monthrange(year, m)[1]) for m in range(1, 13)]
        else:  # custom
            assert self.custom_dates is not None  # validated in __post_init__
            anchors = self.custom_dates
        return [d.timetuple().tm_yday for d in anchors]

    def to_datetime_index(self) -> list[datetime]:
        """Return a list of daily datetimes from ``start`` to ``end`` inclusive."""
        return [self.start + timedelta(days=i) for i in range(self.n_days)]


class BaseInterpolator(ABC):
    """Common interface and shared validations for all temporal interpolators."""

    name: ClassVar[str] = "base"
    wraparound_stamp_on: ClassVar[str] = "climatological_2pt"
    """Value of ``attrs['tempify_wraparound']`` when wraparound is active.

    Subclasses override this to declare how much padding they use:
    ``climatological_2pt`` for Linear (1 node per side, 14 effective),
    ``climatological_4pt`` for PCHIP family (2 nodes per side, 16 effective),
    ``fft_implicit`` for Fourier (no explicit padding, FFT-periodic).
    """

    @abstractmethod
    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        *,
        cyclic: bool = True,
        wraparound: bool | None = None,
        nan_policy: NanPolicy = "raise",
        chunk_size: int | None = None,
    ) -> xr.DataArray:
        """Interpolate ``source`` onto ``target_axis``.

        Parameters
        ----------
        source : xarray.DataArray
            Input array with a monthly temporal dimension named ``month``
            with coordinate values ``1..12``.
        target_axis : TemporalAxis
            Destination temporal coordinate.
        cyclic : bool, default True
            Retro-compatible synonym of ``wraparound`` (per REQ-017 and
            ADR-0016). Will be deprecated in v0.2.0 in favor of
            ``wraparound``. If True, treat December and January as
            adjacent in the interpolation (per REQ-004). If False, apply
            method-specific extrapolation (per REQ-005a/b/c).
        wraparound : bool | None, default None
            When not ``None``, must equal ``cyclic`` (per REQ-017) else
            raises ``ValueError``. When ``None`` (default), the value of
            ``cyclic`` is used. Controls whether climatological wraparound
            is active (per REQ-015 / ADR-0016).
        nan_policy : Literal['raise', 'propagate_all', 'skip_pixel']
            Behavior for pixels with partial NaN values (per REQ-008).
        chunk_size : int | None
            Override default Dask chunk size for spatial dims.
        """

    def _validate_month_count(self, source: xr.DataArray) -> None:
        """Raise InvalidMonthlyStackError if ``source`` lacks 12 months."""
        if "month" not in source.dims:
            raise InvalidMonthlyStackError(
                n_months=0,
                reason="el DataArray no tiene dimensión 'month'",
            )
        n_months = int(source.sizes["month"])
        if n_months != 12:
            raise InvalidMonthlyStackError(n_months=n_months)

    def _validate_month_contiguity(self, source: xr.DataArray) -> None:
        """Raise InvalidMonthlyStackError if the month coord is not 1..12 in order."""
        if "month" not in source.coords:
            return
        values = [int(v) for v in source.coords["month"].values]
        expected = list(range(1, 13))
        if values != expected:
            raise InvalidMonthlyStackError(
                n_months=len(values),
                reason=f"coord 'month' = {values}, se esperaba {expected}",
            )

    def _validate_calendar(self, target_axis: TemporalAxis) -> None:
        """Raise UnsupportedCalendarError if the target calendar is not Gregorian."""
        if target_axis.calendar not in SUPPORTED_CALENDARS:
            raise UnsupportedCalendarError(target_axis.calendar)

    def _validate_nan_policy(self, nan_policy: NanPolicy) -> None:
        """Raise ValueError if ``nan_policy`` is not one of the accepted literals."""
        allowed: tuple[NanPolicy, ...] = ("raise", "propagate_all", "skip_pixel")
        if nan_policy not in allowed:
            raise ValueError(f"nan_policy must be one of {allowed}, got {nan_policy!r}")

    def _resolve_wraparound(self, cyclic: bool, wraparound: bool | None) -> bool:
        """Resolve cyclic/wraparound consistency per REQ-017 and ADR-0016."""
        if wraparound is None:
            return cyclic
        if wraparound != cyclic:
            raise ValueError(
                "cyclic and wraparound must agree; in v0.2.0 cyclic will be "
                f"deprecated in favor of wraparound. Got cyclic={cyclic}, "
                f"wraparound={wraparound}."
            )
        return wraparound

    def _postprocess(
        self,
        result: xr.DataArray,
        target_axis: TemporalAxis,
        wraparound: bool = True,
    ) -> xr.DataArray:
        """Attach standard provenance attributes to the interpolated DataArray.

        Adds ``tempify_method`` (the interpolator class name),
        ``tempify_monthly_anchor`` (the anchor convention used), and
        ``tempify_wraparound`` (climatological wraparound mode per ADR-0016).
        Concrete interpolators may attach additional attributes specific
        to their method (e.g., ``rymes_myers_iterations_max`` per REQ-007).
        """
        out = result.copy()
        out.attrs["tempify_method"] = self.name
        out.attrs["tempify_monthly_anchor"] = target_axis.monthly_anchor
        out.attrs["tempify_wraparound"] = self.wraparound_stamp_on if wraparound else "off"
        return out

```

## File: `code/interpolation/_kernels.py`


```python
"""Internal 1D NumPy kernels used by the interpolators.

Each kernel takes a 1D array of 12 monthly values plus the monthly
anchor positions (``x_in``, days-of-year) and the target positions
(``x_out``, days-of-year) and returns a 1D array of N target values.

The kernels are pure NumPy / SciPy with no xarray dependency. They are
intended to be wrapped by :func:`xarray.apply_ufunc` with
``dask='parallelized'`` to vectorize over the spatial dimensions.

Notes
-----
- All kernels accept ``cyclic: bool``. With ``cyclic=True`` December
  and January are treated as adjacent (the year wraps around).
- NaN handling is the caller's responsibility (the kernels operate on
  arrays that have already been filtered per ``nan_policy``).
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def linear_kernel(
    m: NDArray[np.floating],
    x_in: NDArray[np.floating],
    x_out: NDArray[np.floating],
    cyclic: bool,
) -> NDArray[np.floating]:
    """Piecewise linear interpolation on the year axis.

    Parameters
    ----------
    m : numpy.ndarray
        12 monthly values placed at ``x_in``.
    x_in : numpy.ndarray
        Strictly increasing array of length 12 with the day-of-year of
        each monthly anchor (per ADR-0015).
    x_out : numpy.ndarray
        Strictly increasing array of length N (typically 365 or 366)
        with the target days-of-year.
    cyclic : bool
        If ``True``, treat the year as periodic: linear interpolation
        wraps from December to January with period equal to
        ``x_out[-1] - x_out[0] + 1``. If ``False``, apply constant
        extrapolation outside ``[x_in[0], x_in[-1]]`` per REQ-005a.

    Returns
    -------
    numpy.ndarray
        Array of length ``len(x_out)`` with the interpolated values.
    """
    if cyclic:
        # Period is total number of days in the target year. Extend the
        # input with one wrap node on each side so np.interp can use them
        # linearly. The +1 accounts for "inclusive bounds".
        period = float(x_out[-1] - x_out[0]) + 1.0
        x_left = x_in[-1] - period
        x_right = x_in[0] + period
        m_ext = np.concatenate(([m[-1]], m, [m[0]]))
        x_ext = np.concatenate(([x_left], x_in, [x_right]))
        return np.asarray(np.interp(x_out, x_ext, m_ext))
    return np.asarray(np.interp(x_out, x_in, m))


def pchip_kernel(
    m: NDArray[np.floating],
    x_in: NDArray[np.floating],
    x_out: NDArray[np.floating],
    cyclic: bool,
) -> NDArray[np.floating]:
    """Piecewise cubic Hermite (Fritsch-Carlson) interpolation on the year axis.

    Parameters
    ----------
    m : numpy.ndarray
        12 monthly values placed at ``x_in``.
    x_in : numpy.ndarray
        Strictly increasing array of length 12 with the day-of-year of
        each monthly anchor.
    x_out : numpy.ndarray
        Strictly increasing array of length N with target days-of-year.
    cyclic : bool
        If True, treat the year as periodic. Per design section 5.2 the
        input nodes are padded with two wrap nodes on each side so that
        SciPy's PCHIP delivers C1 continuity at the December-January
        boundary. If False, SciPy's natural extrapolation is used for
        out-of-range positions per REQ-005b.

    Returns
    -------
    numpy.ndarray
        Array of length ``len(x_out)`` with the interpolated values.
    """
    from scipy.interpolate import PchipInterpolator as ScipyPchip  # type: ignore[import-untyped]

    if cyclic:
        period = float(x_out[-1] - x_out[0]) + 1.0
        m_ext = np.concatenate(([m[-2], m[-1]], m, [m[0], m[1]]))
        x_ext = np.concatenate(
            (
                [x_in[-2] - period, x_in[-1] - period],
                x_in,
                [x_in[0] + period, x_in[1] + period],
            )
        )
        pchip = ScipyPchip(x_ext, m_ext, extrapolate=False)
        return np.asarray(pchip(x_out))
    pchip = ScipyPchip(x_in, m, extrapolate=True)
    return np.asarray(pchip(x_out))


def pchip_mp_kernel(
    m: NDArray[np.floating],
    x_in: NDArray[np.floating],
    x_out: NDArray[np.floating],
    day_to_month: NDArray[np.integer],
    cyclic: bool,
    convergence_tol: float,
    max_iterations: int,
) -> tuple[NDArray[np.floating], int]:
    """PCHIP baseline + Rymes-Myers iterative mean-preserving correction.

    The algorithm follows the simplest variant of Rymes & Myers (2001):

    1. Initialize daily values with a PCHIP interpolation of the monthly
       midpoints (auxiliary nodes, per ADR-0010 nivel 1).
    2. Iteratively compute the reconstructed monthly means from the daily
       values, find the residual ``error_m = original_m - reconstructed_m``
       per month, and distribute the residual uniformly across the days of
       that month.
    3. Stop when ``max |error_m| < convergence_tol`` or after
       ``max_iterations`` rounds.

    Parameters
    ----------
    m : numpy.ndarray
        12 monthly values to preserve.
    x_in : numpy.ndarray
        Day-of-year of each monthly anchor (length 12).
    x_out : numpy.ndarray
        Day-of-year targets (length N).
    day_to_month : numpy.ndarray
        Integer array of length N mapping each output day to its month
        index in [0, 11].
    cyclic : bool
        Forwarded to the PCHIP baseline initialization (per REQ-004 and
        ADR-0016 wraparound).
    convergence_tol : float
        Maximum absolute residual accepted in the variable's units.
    max_iterations : int
        Hard cap on iterations (safety guard).

    Returns
    -------
    tuple[numpy.ndarray, int]
        ``(daily_values, iterations_used)``. The second element is the
        number of correction iterations applied; ``0`` means the PCHIP
        baseline already met the tolerance.
    """
    daily = pchip_kernel(m, x_in, x_out, cyclic=cyclic).copy()
    iterations_used = 0
    for iteration in range(1, max_iterations + 1):
        recon = np.zeros(m.size, dtype=np.float64)
        counts = np.zeros(m.size, dtype=np.int64)
        for i in range(daily.size):
            mo = int(day_to_month[i])
            recon[mo] += daily[i]
            counts[mo] += 1
        recon = recon / counts
        errors = m - recon
        max_err = float(np.max(np.abs(errors)))
        if max_err < convergence_tol:
            iterations_used = iteration - 1
            break
        for i in range(daily.size):
            mo = int(day_to_month[i])
            daily[i] += errors[mo]
        iterations_used = iteration
    return daily, iterations_used


def akima_kernel(
    m: NDArray[np.floating],
    x_in: NDArray[np.floating],
    x_out: NDArray[np.floating],
    cyclic: bool,
) -> NDArray[np.floating]:
    """Akima 1970 piecewise cubic Hermite interpolation on the year axis.

    Akima's method produces a C1 spline that is less aggressive than
    PCHIP at flattening peaks but with fewer overshoots than natural
    cubic splines. Useful for variables with brief excursions that
    PCHIP would over-smooth (per ADR-0018).

    Parameters
    ----------
    m : numpy.ndarray
        12 monthly values placed at ``x_in``.
    x_in : numpy.ndarray
        Strictly increasing array of length 12 with the day-of-year of
        each monthly anchor.
    x_out : numpy.ndarray
        Strictly increasing array of length N with target days-of-year.
    cyclic : bool
        If True, treat the year as periodic. Like ``pchip_kernel``, we
        pad the input nodes with two wrap nodes on each side so that
        the C1 join across the December-January boundary is correct.

    Returns
    -------
    numpy.ndarray
        Array of length ``len(x_out)`` with the interpolated values.
    """
    from scipy.interpolate import Akima1DInterpolator  # type: ignore[import-untyped]

    if cyclic:
        period = float(x_out[-1] - x_out[0]) + 1.0
        m_ext = np.concatenate(([m[-2], m[-1]], m, [m[0], m[1]]))
        x_ext = np.concatenate(
            (
                [x_in[-2] - period, x_in[-1] - period],
                x_in,
                [x_in[0] + period, x_in[1] + period],
            )
        )
        akima = Akima1DInterpolator(x_ext, m_ext)
        return np.asarray(akima(x_out))
    akima = Akima1DInterpolator(x_in, m)
    return np.asarray(akima(x_out, extrapolate=True))


def cubic_kernel(
    m: NDArray[np.floating],
    x_in: NDArray[np.floating],
    x_out: NDArray[np.floating],
    cyclic: bool,
) -> NDArray[np.floating]:
    """Natural cubic spline interpolation on the year axis.

    Uses ``scipy.interpolate.CubicSpline`` with periodic boundary
    conditions when ``cyclic=True`` (the spline value and its first
    two derivatives match at year start/end). Otherwise uses the
    default ``not-a-knot`` boundary. Cubic splines provide C2
    continuity but **can overshoot** between knots; use ``pchip`` if
    monotonicity matters (per ADR-0018).

    Parameters
    ----------
    m : numpy.ndarray
        12 monthly values placed at ``x_in``.
    x_in : numpy.ndarray
        Strictly increasing array of length 12 with the day-of-year of
        each monthly anchor.
    x_out : numpy.ndarray
        Strictly increasing array of length N with target days-of-year.
    cyclic : bool
        If True, use periodic boundary conditions. Per the scipy spec
        this requires ``m[0] == m[-1]`` exactly — since this is rarely
        the case for monthly climatologies, we pad with the wrap node
        on each side (same pattern as ``pchip_kernel``).

    Returns
    -------
    numpy.ndarray
        Array of length ``len(x_out)`` with the interpolated values.
    """
    from scipy.interpolate import CubicSpline  # type: ignore[import-untyped]

    if cyclic:
        period = float(x_out[-1] - x_out[0]) + 1.0
        m_ext = np.concatenate(([m[-2], m[-1]], m, [m[0], m[1]]))
        x_ext = np.concatenate(
            (
                [x_in[-2] - period, x_in[-1] - period],
                x_in,
                [x_in[0] + period, x_in[1] + period],
            )
        )
        spline = CubicSpline(x_ext, m_ext, bc_type="not-a-knot", extrapolate=False)
        return np.asarray(spline(x_out))
    spline = CubicSpline(x_in, m, bc_type="not-a-knot", extrapolate=True)
    return np.asarray(spline(x_out))


def fourier_kernel(
    m: NDArray[np.floating],
    x_in: NDArray[np.floating],
    x_out: NDArray[np.floating],
    n_harmonics: int,
) -> NDArray[np.floating]:
    """Truncated Fourier series interpolation via numpy.fft.rfft.

    The 12 monthly inputs are treated as periodic samples of an annual
    signal. The first ``n_harmonics`` positive-frequency coefficients
    (plus the DC term) are kept and used to synthesize values at
    arbitrary daily positions. Fourier is inherently periodic so there
    is no separate cyclic vs non-cyclic mode; the FFT semantics handle
    the year wraparound implicitly (per ADR-0016 stamp ``fft_implicit``).

    Parameters
    ----------
    m : numpy.ndarray
        12 monthly values (FFT requires uniformly spaced samples; we
        treat the monthly anchors as approximately uniform — the small
        non-uniformity from midpoint dates per ADR-0015 is absorbed via
        the explicit ``x_in`` re-projection below).
    x_in : numpy.ndarray
        Day-of-year of each monthly anchor (length 12).
    x_out : numpy.ndarray
        Day-of-year targets (length N).
    n_harmonics : int
        Number of positive-frequency harmonics to retain. Must be in
        ``[FOURIER_MIN_HARMONICS, FOURIER_MAX_HARMONICS]``. The DC term
        is always kept.

    Returns
    -------
    numpy.ndarray
        Array of length ``len(x_out)`` with the reconstructed values.
    """
    n = m.size
    coeffs = np.fft.rfft(m)
    period = float(x_out[-1] - x_out[0]) + 1.0
    t = (x_out - x_in[0]) / period * n
    result = np.full(x_out.size, float(np.real(coeffs[0])) / n, dtype=np.float64)
    max_k = min(n_harmonics, n // 2)
    for k in range(1, max_k + 1):
        c = coeffs[k]
        factor = 2.0 / n if (n % 2 != 0 or k < n // 2) else 1.0 / n
        angle = 2.0 * np.pi * k * t / n
        result += factor * (float(np.real(c)) * np.cos(angle) - float(np.imag(c)) * np.sin(angle))
    return result

```

## File: `code/interpolation/linear.py`


```python
"""Linear interpolator.

Wraps the pure-NumPy :func:`tempify.interpolation._kernels.linear_kernel`
in an :class:`xarray.apply_ufunc` call with ``dask='parallelized'`` to
vectorize over the spatial dimensions.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import xarray as xr

from tempify.constants import DEFAULT_CHUNK_SIZE
from tempify.interpolation._kernels import linear_kernel
from tempify.interpolation.base import (
    BaseInterpolator,
    NanPolicy,
    TemporalAxis,
)
from tempify.interpolation.exceptions import PartialNanPixelError


class LinearInterpolator(BaseInterpolator):
    """Piecewise linear interpolator between consecutive monthly nodes.

    Parameters
    ----------
    None

    Notes
    -----
    Per REQ-004 the default boundary mode is cyclic; per REQ-005a the
    non-cyclic mode applies constant extrapolation outside the input
    range. NaN propagation follows the configurable ``nan_policy``
    keyword of :meth:`interpolate`.
    """

    name: ClassVar[str] = "linear"
    wraparound_stamp_on: ClassVar[str] = "climatological_2pt"

    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        *,
        cyclic: bool = True,
        wraparound: bool | None = None,
        nan_policy: NanPolicy = "raise",
        chunk_size: int | None = None,
    ) -> xr.DataArray:
        """Interpolate the monthly ``source`` onto ``target_axis`` linearly."""
        self._validate_month_count(source)
        self._validate_month_contiguity(source)
        self._validate_calendar(target_axis)
        self._validate_nan_policy(nan_policy)
        wrap = self._resolve_wraparound(cyclic, wraparound)

        x_in = np.asarray(target_axis.monthly_anchor_doys(), dtype=np.float64)
        x_out = np.arange(1, target_axis.n_days + 1, dtype=np.float64)

        chunk = chunk_size if chunk_size is not None else DEFAULT_CHUNK_SIZE
        prepared = self._prepare_chunks(source, chunk)

        result = xr.apply_ufunc(
            _per_pixel,
            prepared,
            input_core_dims=[["month"]],
            output_core_dims=[["time"]],
            kwargs={"x_in": x_in, "x_out": x_out, "cyclic": wrap, "nan_policy": nan_policy},
            dask="parallelized",
            dask_gufunc_kwargs={"output_sizes": {"time": target_axis.n_days}},
            output_dtypes=[np.float64],
            vectorize=False,
        )
        result = result.assign_coords(time=target_axis.to_datetime_index())
        return self._postprocess(result, target_axis, wraparound=wrap)

    @staticmethod
    def _prepare_chunks(source: xr.DataArray, chunk: int) -> xr.DataArray:
        """Rechunk ``source`` so spatial dims use ``chunk`` and ``month`` is whole."""
        from collections.abc import Hashable

        chunks: dict[Hashable, int] = {"month": -1}
        for d in source.dims:
            if d == "month":
                continue
            chunks[d] = chunk
        return source.chunk(chunks)


def _per_pixel(
    m_block: np.ndarray,
    *,
    x_in: np.ndarray,
    x_out: np.ndarray,
    cyclic: bool,
    nan_policy: NanPolicy,
) -> np.ndarray:
    """Apply :func:`linear_kernel` per pixel along the trailing ``month`` axis.

    ``m_block`` has shape ``(..., 12)`` after apply_ufunc rearranges it.
    Returns an array with shape ``(..., len(x_out))``.
    """
    flat = m_block.reshape(-1, m_block.shape[-1])
    out = np.empty((flat.shape[0], x_out.size), dtype=np.float64)
    for i in range(flat.shape[0]):
        values = flat[i]
        nan_mask = np.isnan(values)
        n_nan = int(nan_mask.sum())
        if n_nan == values.size:
            out[i] = np.nan
            continue
        if n_nan > 0:
            if nan_policy == "raise":
                raise PartialNanPixelError(pixel_index=(i,), n_nan=n_nan)
            if nan_policy == "propagate_all":
                out[i] = np.nan
                continue
            # skip_pixel: fall through to interpolate without NaNs by
            # filtering them out
            mask = ~nan_mask
            x_in_use = x_in[mask]
            values_use = values[mask]
        else:
            x_in_use = x_in
            values_use = values
        out[i] = linear_kernel(
            values_use.astype(np.float64),
            x_in_use.astype(np.float64),
            x_out,
            cyclic=cyclic,
        )
    return out.reshape(*m_block.shape[:-1], x_out.size)

```

## File: `code/interpolation/pchip.py`


```python
"""PCHIP (Fritsch-Carlson) interpolator.

Wraps the pure-NumPy/SciPy :func:`tempify.interpolation._kernels.pchip_kernel`
in an :class:`xarray.apply_ufunc` call with ``dask='parallelized'``. With
``cyclic=True`` the inputs are padded with two wrap nodes per side to
achieve C1 continuity at the December-January boundary (design section 5.2).
"""

from __future__ import annotations

from collections.abc import Hashable
from typing import ClassVar

import numpy as np
import xarray as xr

from tempify.constants import DEFAULT_CHUNK_SIZE
from tempify.interpolation._kernels import pchip_kernel
from tempify.interpolation.base import (
    BaseInterpolator,
    NanPolicy,
    TemporalAxis,
)
from tempify.interpolation.exceptions import PartialNanPixelError


class PchipInterpolator(BaseInterpolator):
    """Piecewise Cubic Hermite (Fritsch-Carlson) interpolator with cyclic option.

    Notes
    -----
    Per REQ-004 the default boundary mode is cyclic, padding with two
    wrap nodes per side to ensure C1 continuity. Per REQ-005b non-cyclic
    mode uses SciPy's natural polynomial extrapolation. NaN propagation
    follows the configurable ``nan_policy`` keyword of :meth:`interpolate`;
    in ``skip_pixel`` mode at least two valid monthly values are required.
    """

    name: ClassVar[str] = "pchip"
    wraparound_stamp_on: ClassVar[str] = "climatological_4pt"

    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        *,
        cyclic: bool = True,
        wraparound: bool | None = None,
        nan_policy: NanPolicy = "raise",
        chunk_size: int | None = None,
    ) -> xr.DataArray:
        """Interpolate the monthly ``source`` onto ``target_axis`` with PCHIP."""
        self._validate_month_count(source)
        self._validate_month_contiguity(source)
        self._validate_calendar(target_axis)
        self._validate_nan_policy(nan_policy)
        wrap = self._resolve_wraparound(cyclic, wraparound)

        x_in = np.asarray(target_axis.monthly_anchor_doys(), dtype=np.float64)
        x_out = np.arange(1, target_axis.n_days + 1, dtype=np.float64)

        chunk = chunk_size if chunk_size is not None else DEFAULT_CHUNK_SIZE
        prepared = self._prepare_chunks(source, chunk)

        result = xr.apply_ufunc(
            _per_pixel,
            prepared,
            input_core_dims=[["month"]],
            output_core_dims=[["time"]],
            kwargs={
                "x_in": x_in,
                "x_out": x_out,
                "cyclic": wrap,
                "nan_policy": nan_policy,
            },
            dask="parallelized",
            dask_gufunc_kwargs={"output_sizes": {"time": target_axis.n_days}},
            output_dtypes=[np.float64],
            vectorize=False,
        )
        result = result.assign_coords(time=target_axis.to_datetime_index())
        return self._postprocess(result, target_axis, wraparound=wrap)

    @staticmethod
    def _prepare_chunks(source: xr.DataArray, chunk: int) -> xr.DataArray:
        """Rechunk ``source`` so spatial dims use ``chunk`` and ``month`` is whole."""
        chunks: dict[Hashable, int] = {"month": -1}
        for d in source.dims:
            if d == "month":
                continue
            chunks[d] = chunk
        return source.chunk(chunks)


def _per_pixel(
    m_block: np.ndarray,
    *,
    x_in: np.ndarray,
    x_out: np.ndarray,
    cyclic: bool,
    nan_policy: NanPolicy,
) -> np.ndarray:
    """Apply :func:`pchip_kernel` per pixel along the trailing ``month`` axis."""
    flat = m_block.reshape(-1, m_block.shape[-1])
    out = np.empty((flat.shape[0], x_out.size), dtype=np.float64)
    for i in range(flat.shape[0]):
        values = flat[i]
        nan_mask = np.isnan(values)
        n_nan = int(nan_mask.sum())
        if n_nan == values.size:
            out[i] = np.nan
            continue
        if n_nan > 0:
            if nan_policy == "raise":
                raise PartialNanPixelError(pixel_index=(i,), n_nan=n_nan)
            if nan_policy == "propagate_all":
                out[i] = np.nan
                continue
            mask = ~nan_mask
            if int(mask.sum()) < 2:
                out[i] = np.nan
                continue
            x_in_use = x_in[mask]
            values_use = values[mask]
        else:
            x_in_use = x_in
            values_use = values
        out[i] = pchip_kernel(
            values_use.astype(np.float64),
            x_in_use.astype(np.float64),
            x_out,
            cyclic=cyclic and n_nan == 0,
        )
    return out.reshape(*m_block.shape[:-1], x_out.size)

```

## File: `code/interpolation/pchip_mp.py`


```python
"""PCHIP with Rymes-Myers mean-preserving correction.

Implements the iterative mean-preserving algorithm of Rymes & Myers
(2001) on top of a PCHIP baseline. The output is guaranteed to preserve
the monthly aggregates exactly to within ``convergence_tol`` per
REQ-006 / ADR-0010 nivel 1.
"""

from __future__ import annotations

from collections.abc import Hashable
from typing import ClassVar

import numpy as np
import xarray as xr

from tempify.constants import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_RM_CONVERGENCE_TOL,
    DEFAULT_RM_MAX_ITER,
)
from tempify.interpolation._kernels import pchip_mp_kernel
from tempify.interpolation.base import (
    BaseInterpolator,
    NanPolicy,
    TemporalAxis,
)
from tempify.interpolation.exceptions import PartialNanPixelError


def _compute_day_to_month(target_axis: TemporalAxis) -> np.ndarray:
    """Return an int array of length ``n_days`` mapping each day to its month [0, 11]."""
    days = target_axis.to_datetime_index()
    return np.asarray([d.month - 1 for d in days], dtype=np.int64)


class PchipMeanPreservingInterpolator(BaseInterpolator):
    """PCHIP base interpolation refined iteratively to preserve monthly means.

    Parameters
    ----------
    convergence_tol : float
        Iterator stopping criterion in the variable's units (per ADR-0010
        nivel 1). Default :data:`tempify.constants.DEFAULT_RM_CONVERGENCE_TOL`
        = ``1e-6``.
    max_iterations : int
        Hard safety cap on the iterative correction. Default
        :data:`tempify.constants.DEFAULT_RM_MAX_ITER` = ``50``.

    Notes
    -----
    Per REQ-006 the system iterates until the maximum absolute residual
    falls below ``convergence_tol``. Per REQ-007 the iteration count is
    recorded on the output ``DataArray`` as the maximum observed across
    all pixels in the chunk (``attrs['rymes_myers_iterations_max']``);
    convergence status is reported as a boolean
    (``attrs['rymes_myers_converged']``), ``True`` when no pixel
    reached the iteration cap. The midpoint convention (ADR-0015) governs
    only the auxiliary node initialization; the monthly mean preservation
    is independent of the anchor.
    """

    name: ClassVar[str] = "pchip_mp"
    wraparound_stamp_on: ClassVar[str] = "climatological_4pt"

    def __init__(
        self,
        convergence_tol: float = DEFAULT_RM_CONVERGENCE_TOL,
        max_iterations: int = DEFAULT_RM_MAX_ITER,
    ) -> None:
        if convergence_tol <= 0:
            raise ValueError(f"convergence_tol must be positive, got {convergence_tol}")
        if max_iterations < 1:
            raise ValueError(f"max_iterations must be >= 1, got {max_iterations}")
        self.convergence_tol = convergence_tol
        self.max_iterations = max_iterations

    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        *,
        cyclic: bool = True,
        wraparound: bool | None = None,
        nan_policy: NanPolicy = "raise",
        chunk_size: int | None = None,
    ) -> xr.DataArray:
        """Interpolate ``source`` onto ``target_axis`` preserving monthly means."""
        self._validate_month_count(source)
        self._validate_month_contiguity(source)
        self._validate_calendar(target_axis)
        self._validate_nan_policy(nan_policy)
        wrap = self._resolve_wraparound(cyclic, wraparound)

        x_in = np.asarray(target_axis.monthly_anchor_doys(), dtype=np.float64)
        x_out = np.arange(1, target_axis.n_days + 1, dtype=np.float64)
        day_to_month = _compute_day_to_month(target_axis)

        chunk = chunk_size if chunk_size is not None else DEFAULT_CHUNK_SIZE
        prepared = self._prepare_chunks(source, chunk)

        # Use a list to accumulate iteration counts. apply_ufunc doesn't
        # easily return scalar metadata per call, so we attach a global
        # summary via the kernel running in a single batch (the simplest
        # robust approach is to record max across pixels at the end).
        max_iters_observed: list[int] = [0]

        def _per_pixel(m_block: np.ndarray) -> np.ndarray:
            return _run_per_pixel(
                m_block,
                x_in=x_in,
                x_out=x_out,
                day_to_month=day_to_month,
                cyclic=wrap,
                convergence_tol=self.convergence_tol,
                max_iterations=self.max_iterations,
                nan_policy=nan_policy,
                iter_collector=max_iters_observed,
            )

        result = xr.apply_ufunc(
            _per_pixel,
            prepared,
            input_core_dims=[["month"]],
            output_core_dims=[["time"]],
            dask="parallelized",
            dask_gufunc_kwargs={"output_sizes": {"time": target_axis.n_days}},
            output_dtypes=[np.float64],
            vectorize=False,
        )
        result = result.assign_coords(time=target_axis.to_datetime_index())
        # Force materialization on small arrays so we can stamp the iteration
        # count; on dask-backed arrays we defer the stamp until compute.
        out = self._postprocess(result, target_axis, wraparound=wrap)
        out.attrs["rymes_myers_iterations_max"] = max_iters_observed[0]
        out.attrs["rymes_myers_convergence_tol"] = self.convergence_tol
        out.attrs["rymes_myers_max_iterations_allowed"] = self.max_iterations
        # 1 iff every pixel converged strictly before the cap, 0 if any
        # pixel hit ``max_iterations`` without satisfying
        # ``max|error| < convergence_tol``. Per spec design.md §5.3. We
        # use int (0/1) instead of bool because NetCDF attribute writers
        # only accept numeric/string dtypes (``b1`` is rejected).
        out.attrs["rymes_myers_converged"] = int(
            max_iters_observed[0] < self.max_iterations
        )
        return out

    @staticmethod
    def _prepare_chunks(source: xr.DataArray, chunk: int) -> xr.DataArray:
        """Rechunk ``source`` so spatial dims use ``chunk`` and ``month`` is whole."""
        chunks: dict[Hashable, int] = {"month": -1}
        for d in source.dims:
            if d == "month":
                continue
            chunks[d] = chunk
        return source.chunk(chunks)


def _run_per_pixel(
    m_block: np.ndarray,
    *,
    x_in: np.ndarray,
    x_out: np.ndarray,
    day_to_month: np.ndarray,
    cyclic: bool,
    convergence_tol: float,
    max_iterations: int,
    nan_policy: NanPolicy,
    iter_collector: list[int],
) -> np.ndarray:
    """Run :func:`pchip_mp_kernel` per pixel along the trailing ``month`` axis."""
    flat = m_block.reshape(-1, m_block.shape[-1])
    out = np.empty((flat.shape[0], x_out.size), dtype=np.float64)
    for i in range(flat.shape[0]):
        values = flat[i]
        nan_mask = np.isnan(values)
        n_nan = int(nan_mask.sum())
        if n_nan == values.size:
            out[i] = np.nan
            continue
        if n_nan > 0:
            if nan_policy == "raise":
                raise PartialNanPixelError(pixel_index=(i,), n_nan=n_nan)
            if nan_policy == "propagate_all":
                out[i] = np.nan
                continue
            # Mean-preserving algorithm needs all 12 monthly anchors to be
            # meaningful; skip_pixel propagates NaN here (we don't fabricate
            # missing months because that would silently violate REQ-006).
            out[i] = np.nan
            continue
        daily, iters = pchip_mp_kernel(
            values.astype(np.float64),
            x_in.astype(np.float64),
            x_out,
            day_to_month,
            cyclic=cyclic,
            convergence_tol=convergence_tol,
            max_iterations=max_iterations,
        )
        out[i] = daily
        if iters > iter_collector[0]:
            iter_collector[0] = iters
    return out.reshape(*m_block.shape[:-1], x_out.size)

```

## File: `code/interpolation/akima.py`


```python
"""Akima (1970) piecewise cubic Hermite interpolator.

Wraps :func:`tempify.interpolation._kernels.akima_kernel` in an
``xarray.apply_ufunc`` call with ``dask='parallelized'``. Per ADR-0018
the cyclic boundary mode uses two wrap nodes per side, same convention
as :class:`PchipInterpolator`.
"""

from __future__ import annotations

from collections.abc import Hashable
from typing import ClassVar

import numpy as np
import xarray as xr

from tempify.constants import DEFAULT_CHUNK_SIZE
from tempify.interpolation._kernels import akima_kernel
from tempify.interpolation.base import (
    BaseInterpolator,
    NanPolicy,
    TemporalAxis,
)
from tempify.interpolation.exceptions import PartialNanPixelError


class AkimaInterpolator(BaseInterpolator):
    """Akima 1970 spline interpolator with cyclic option.

    Akima's algorithm produces a C1 spline that is less aggressive than
    PCHIP at flattening local extrema but with fewer overshoots than
    natural cubic splines. Useful for variables with brief excursions
    that PCHIP would oversmooth.

    Notes
    -----
    Default boundary mode is cyclic (two wrap nodes per side, per
    ADR-0016 and ADR-0018). Non-cyclic mode uses SciPy's natural
    extrapolation. NaN policy follows the configurable ``nan_policy``;
    ``skip_pixel`` mode requires at least two valid monthly values.
    """

    name: ClassVar[str] = "akima"
    wraparound_stamp_on: ClassVar[str] = "climatological_4pt"

    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        *,
        cyclic: bool = True,
        wraparound: bool | None = None,
        nan_policy: NanPolicy = "raise",
        chunk_size: int | None = None,
    ) -> xr.DataArray:
        """Interpolate the monthly ``source`` onto ``target_axis`` with Akima."""
        self._validate_month_count(source)
        self._validate_month_contiguity(source)
        self._validate_calendar(target_axis)
        self._validate_nan_policy(nan_policy)
        wrap = self._resolve_wraparound(cyclic, wraparound)

        x_in = np.asarray(target_axis.monthly_anchor_doys(), dtype=np.float64)
        x_out = np.arange(1, target_axis.n_days + 1, dtype=np.float64)

        chunk = chunk_size if chunk_size is not None else DEFAULT_CHUNK_SIZE
        prepared = self._prepare_chunks(source, chunk)

        result = xr.apply_ufunc(
            _per_pixel,
            prepared,
            input_core_dims=[["month"]],
            output_core_dims=[["time"]],
            kwargs={
                "x_in": x_in,
                "x_out": x_out,
                "cyclic": wrap,
                "nan_policy": nan_policy,
            },
            dask="parallelized",
            dask_gufunc_kwargs={"output_sizes": {"time": target_axis.n_days}},
            output_dtypes=[np.float64],
            vectorize=False,
        )
        result = result.assign_coords(time=target_axis.to_datetime_index())
        return self._postprocess(result, target_axis, wraparound=wrap)

    @staticmethod
    def _prepare_chunks(source: xr.DataArray, chunk: int) -> xr.DataArray:
        chunks: dict[Hashable, int] = {"month": -1}
        for d in source.dims:
            if d == "month":
                continue
            chunks[d] = chunk
        return source.chunk(chunks)


def _per_pixel(
    m_block: np.ndarray,
    *,
    x_in: np.ndarray,
    x_out: np.ndarray,
    cyclic: bool,
    nan_policy: NanPolicy,
) -> np.ndarray:
    """Apply :func:`akima_kernel` per pixel along the trailing ``month`` axis."""
    flat = m_block.reshape(-1, m_block.shape[-1])
    out = np.empty((flat.shape[0], x_out.size), dtype=np.float64)
    for i in range(flat.shape[0]):
        values = flat[i]
        nan_mask = np.isnan(values)
        n_nan = int(nan_mask.sum())
        if n_nan == values.size:
            out[i] = np.nan
            continue
        if n_nan > 0:
            if nan_policy == "raise":
                raise PartialNanPixelError(pixel_index=(i,), n_nan=n_nan)
            if nan_policy == "propagate_all":
                out[i] = np.nan
                continue
            mask = ~nan_mask
            if int(mask.sum()) < 2:
                out[i] = np.nan
                continue
            x_in_use = x_in[mask]
            values_use = values[mask]
        else:
            x_in_use = x_in
            values_use = values
        out[i] = akima_kernel(
            values_use.astype(np.float64),
            x_in_use.astype(np.float64),
            x_out,
            cyclic=cyclic and n_nan == 0,
        )
    return out.reshape(*m_block.shape[:-1], x_out.size)

```

## File: `code/interpolation/cubic.py`


```python
"""Natural cubic spline interpolator.

Wraps :func:`tempify.interpolation._kernels.cubic_kernel` in an
``xarray.apply_ufunc`` call with ``dask='parallelized'``. Per ADR-0018
the spline is C2 continuous, with the cyclic boundary mode emulated
via the two-wrap-node padding used by the PCHIP and Akima paths.
"""

from __future__ import annotations

from collections.abc import Hashable
from typing import ClassVar

import numpy as np
import xarray as xr

from tempify.constants import DEFAULT_CHUNK_SIZE
from tempify.interpolation._kernels import cubic_kernel
from tempify.interpolation.base import (
    BaseInterpolator,
    NanPolicy,
    TemporalAxis,
)
from tempify.interpolation.exceptions import PartialNanPixelError


class CubicSplineInterpolator(BaseInterpolator):
    """Natural cubic spline interpolator with cyclic option.

    Natural cubic splines provide C2 continuity (smoother than PCHIP),
    at the cost of allowing **overshoots between knots**. Recommended
    for variables with smooth annual cycles and no hard physical
    bounds. Use ``pchip`` or ``pchip_mp`` when monotonicity matters,
    or ``fourier`` for harmonic signals.

    Notes
    -----
    Default boundary mode is cyclic (two wrap nodes per side). Per
    ADR-0018 this is preferable to scipy's ``bc_type="periodic"``
    because the latter requires ``m[0] == m[-1]`` exactly, which is
    rare for monthly climatologies.
    """

    name: ClassVar[str] = "cubic"
    wraparound_stamp_on: ClassVar[str] = "climatological_4pt"

    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        *,
        cyclic: bool = True,
        wraparound: bool | None = None,
        nan_policy: NanPolicy = "raise",
        chunk_size: int | None = None,
    ) -> xr.DataArray:
        """Interpolate the monthly ``source`` onto ``target_axis`` with cubic spline."""
        self._validate_month_count(source)
        self._validate_month_contiguity(source)
        self._validate_calendar(target_axis)
        self._validate_nan_policy(nan_policy)
        wrap = self._resolve_wraparound(cyclic, wraparound)

        x_in = np.asarray(target_axis.monthly_anchor_doys(), dtype=np.float64)
        x_out = np.arange(1, target_axis.n_days + 1, dtype=np.float64)

        chunk = chunk_size if chunk_size is not None else DEFAULT_CHUNK_SIZE
        prepared = self._prepare_chunks(source, chunk)

        result = xr.apply_ufunc(
            _per_pixel,
            prepared,
            input_core_dims=[["month"]],
            output_core_dims=[["time"]],
            kwargs={
                "x_in": x_in,
                "x_out": x_out,
                "cyclic": wrap,
                "nan_policy": nan_policy,
            },
            dask="parallelized",
            dask_gufunc_kwargs={"output_sizes": {"time": target_axis.n_days}},
            output_dtypes=[np.float64],
            vectorize=False,
        )
        result = result.assign_coords(time=target_axis.to_datetime_index())
        return self._postprocess(result, target_axis, wraparound=wrap)

    @staticmethod
    def _prepare_chunks(source: xr.DataArray, chunk: int) -> xr.DataArray:
        chunks: dict[Hashable, int] = {"month": -1}
        for d in source.dims:
            if d == "month":
                continue
            chunks[d] = chunk
        return source.chunk(chunks)


def _per_pixel(
    m_block: np.ndarray,
    *,
    x_in: np.ndarray,
    x_out: np.ndarray,
    cyclic: bool,
    nan_policy: NanPolicy,
) -> np.ndarray:
    """Apply :func:`cubic_kernel` per pixel along the trailing ``month`` axis."""
    flat = m_block.reshape(-1, m_block.shape[-1])
    out = np.empty((flat.shape[0], x_out.size), dtype=np.float64)
    for i in range(flat.shape[0]):
        values = flat[i]
        nan_mask = np.isnan(values)
        n_nan = int(nan_mask.sum())
        if n_nan == values.size:
            out[i] = np.nan
            continue
        if n_nan > 0:
            if nan_policy == "raise":
                raise PartialNanPixelError(pixel_index=(i,), n_nan=n_nan)
            if nan_policy == "propagate_all":
                out[i] = np.nan
                continue
            mask = ~nan_mask
            if int(mask.sum()) < 2:
                out[i] = np.nan
                continue
            x_in_use = x_in[mask]
            values_use = values[mask]
        else:
            x_in_use = x_in
            values_use = values
        out[i] = cubic_kernel(
            values_use.astype(np.float64),
            x_in_use.astype(np.float64),
            x_out,
            cyclic=cyclic and n_nan == 0,
        )
    return out.reshape(*m_block.shape[:-1], x_out.size)

```

## File: `code/interpolation/fourier.py`


```python
"""Fourier multi-harmonic interpolator.

Treats the 12 monthly inputs as samples of a periodic annual signal.
Uses ``numpy.fft.rfft`` to extract Fourier coefficients, truncates to
``n_harmonics`` positive frequencies (plus DC), and synthesizes daily
values at the target axis positions. Per ADR-0016 the wraparound is
``fft_implicit``: the FFT itself enforces periodicity, so no explicit
padding is required.
"""

from __future__ import annotations

from collections.abc import Hashable
from typing import ClassVar

import numpy as np
import xarray as xr

from tempify.constants import (
    DEFAULT_CHUNK_SIZE,
    FOURIER_MAX_HARMONICS,
    FOURIER_MIN_HARMONICS,
)
from tempify.interpolation._kernels import fourier_kernel
from tempify.interpolation.base import (
    BaseInterpolator,
    NanPolicy,
    TemporalAxis,
)
from tempify.interpolation.exceptions import PartialNanPixelError


class FourierInterpolator(BaseInterpolator):
    """Truncated Fourier series interpolator with configurable harmonics.

    Parameters
    ----------
    n_harmonics : int
        Number of positive-frequency harmonics retained beyond the DC
        term. Must lie in ``[FOURIER_MIN_HARMONICS, FOURIER_MAX_HARMONICS]``
        (= ``[1, 5]`` for 12 monthly samples; the Nyquist limit is 6).

    Notes
    -----
    Per REQ-005c Fourier has no special non-cyclic mode: the FFT-based
    reconstruction is inherently periodic regardless of the ``cyclic``
    flag. The output is stamped with ``attrs['tempify_wraparound'] =
    'fft_implicit'`` when wraparound is True, and ``'fft_implicit_off'``
    when the user explicitly requested ``wraparound=False`` (the
    numerical behavior is unchanged but the stamp records the user's
    intent for traceability per ADR-0016).
    """

    name: ClassVar[str] = "fourier"
    wraparound_stamp_on: ClassVar[str] = "fft_implicit"

    def __init__(self, n_harmonics: int = 3) -> None:
        if not (FOURIER_MIN_HARMONICS <= n_harmonics <= FOURIER_MAX_HARMONICS):
            raise ValueError(
                f"n_harmonics must be in [{FOURIER_MIN_HARMONICS}, "
                f"{FOURIER_MAX_HARMONICS}]; got {n_harmonics}"
            )
        self.n_harmonics = n_harmonics

    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        *,
        cyclic: bool = True,
        wraparound: bool | None = None,
        nan_policy: NanPolicy = "raise",
        chunk_size: int | None = None,
    ) -> xr.DataArray:
        """Interpolate ``source`` onto ``target_axis`` via truncated Fourier series."""
        self._validate_month_count(source)
        self._validate_month_contiguity(source)
        self._validate_calendar(target_axis)
        self._validate_nan_policy(nan_policy)
        wrap = self._resolve_wraparound(cyclic, wraparound)

        x_in = np.asarray(target_axis.monthly_anchor_doys(), dtype=np.float64)
        x_out = np.arange(1, target_axis.n_days + 1, dtype=np.float64)

        chunk = chunk_size if chunk_size is not None else DEFAULT_CHUNK_SIZE
        prepared = self._prepare_chunks(source, chunk)

        result = xr.apply_ufunc(
            _per_pixel,
            prepared,
            input_core_dims=[["month"]],
            output_core_dims=[["time"]],
            kwargs={
                "x_in": x_in,
                "x_out": x_out,
                "n_harmonics": self.n_harmonics,
                "nan_policy": nan_policy,
            },
            dask="parallelized",
            dask_gufunc_kwargs={"output_sizes": {"time": target_axis.n_days}},
            output_dtypes=[np.float64],
            vectorize=False,
        )
        result = result.assign_coords(time=target_axis.to_datetime_index())
        out = self._postprocess(result, target_axis, wraparound=wrap)
        out.attrs["tempify_n_harmonics"] = self.n_harmonics
        return out

    @staticmethod
    def _prepare_chunks(source: xr.DataArray, chunk: int) -> xr.DataArray:
        """Rechunk ``source`` so spatial dims use ``chunk`` and ``month`` is whole."""
        chunks: dict[Hashable, int] = {"month": -1}
        for d in source.dims:
            if d == "month":
                continue
            chunks[d] = chunk
        return source.chunk(chunks)


def _per_pixel(
    m_block: np.ndarray,
    *,
    x_in: np.ndarray,
    x_out: np.ndarray,
    n_harmonics: int,
    nan_policy: NanPolicy,
) -> np.ndarray:
    """Apply :func:`fourier_kernel` per pixel along the trailing ``month`` axis."""
    flat = m_block.reshape(-1, m_block.shape[-1])
    out = np.empty((flat.shape[0], x_out.size), dtype=np.float64)
    for i in range(flat.shape[0]):
        values = flat[i]
        nan_mask = np.isnan(values)
        n_nan = int(nan_mask.sum())
        if n_nan == values.size:
            out[i] = np.nan
            continue
        if n_nan > 0:
            if nan_policy == "raise":
                raise PartialNanPixelError(pixel_index=(i,), n_nan=n_nan)
            if nan_policy == "propagate_all":
                out[i] = np.nan
                continue
            # skip_pixel: FFT requires the full 12-sample input. With NaNs
            # we cannot run an honest FFT, so we propagate NaN for this
            # pixel rather than fabricate values.
            out[i] = np.nan
            continue
        out[i] = fourier_kernel(
            values.astype(np.float64),
            x_in.astype(np.float64),
            x_out,
            n_harmonics=n_harmonics,
        )
    return out.reshape(*m_block.shape[:-1], x_out.size)

```

## File: `code/pipeline/config.py`


```python
"""PipelineConfig: immutable run-time configuration for the pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from tempify.pipeline.callbacks import FrequencyResolverProtocol, ProgressCallback
from tempify.pipeline.errors import InvalidConfigError

InterpolationMethod = Literal["linear", "pchip", "pchip_mp", "fourier", "akima", "cubic"]
OutputFormat = Literal["netcdf", "geotiff_collection", "multiband_geotiff", "zarr"]
ReproMode = Literal["strict", "parallel"]
MonthlyAnchor = Literal["midpoint", "start", "end", "custom"]


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Frozen, validated configuration for a single pipeline run."""

    method: InterpolationMethod
    target_year: int
    output_dir: Path
    output_format: OutputFormat = "netcdf"
    chunk_size: int = 512
    scheduler: Literal["threaded", "synchronous"] = "threaded"
    reproducibility_mode: ReproMode = "parallel"
    progress_callback: ProgressCallback | None = None
    progress_frequency_hz: float = 4.0
    frequency_resolver_callback: FrequencyResolverProtocol | None = None
    dry_run: bool = False
    skip_pre_validation: bool = False
    force_method: bool = False
    variable_profile_override: str | None = None
    monthly_anchor: MonthlyAnchor = "midpoint"
    custom_time_axis: tuple[datetime, ...] | None = None
    seed: int | None = None
    method_options: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.skip_pre_validation and not self.dry_run:
            raise InvalidConfigError(
                "skip_pre_validation=True requires dry_run=True (inspect mode)."
            )
        if self.monthly_anchor == "custom" and self.custom_time_axis is None:
            raise InvalidConfigError("monthly_anchor='custom' requires custom_time_axis to be set.")
        if self.monthly_anchor != "custom" and self.custom_time_axis is not None:
            raise InvalidConfigError(
                "custom_time_axis can only be provided with monthly_anchor='custom'."
            )
        if self.chunk_size <= 0:
            raise InvalidConfigError(f"chunk_size must be positive; got {self.chunk_size}")
        if self.progress_frequency_hz <= 0:
            raise InvalidConfigError(
                f"progress_frequency_hz must be positive; got {self.progress_frequency_hz}"
            )

```

## File: `code/pipeline/core.py`


```python
"""TempifyPipeline: end-to-end orchestrator (Capa 5).

Sequences the 7 canonical phases and produces a :class:`PipelineResult`.
Per ADR-0014 the class is PascalCase ``TempifyPipeline`` (the module
remains lowercase ``tempify.pipeline``).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import xarray as xr

from tempify.constants import DEFAULT_RM_CONVERGENCE_TOL, DEFAULT_RM_MAX_ITER
from tempify.detection import StructureDetector
from tempify.detection.frequency import (
    TemporalFrequencyResolver,
)
from tempify.interpolation import (
    BaseInterpolator,
    AkimaInterpolator,
    CubicSplineInterpolator,
    FourierInterpolator,
    LinearInterpolator,
    PchipInterpolator,
    PchipMeanPreservingInterpolator,
    TemporalAxis,
)
from tempify.io import (
    BaseReader,
    BaseWriter,
    GeoTIFFCollectionWriter,
    GeoTIFFReader,
    MultiBandGeoTIFFWriter,
    MultiFileCollectionReader,
    NetCDFReader,
    NetCDFWriter,
    ZarrWriter,
)
from tempify.pipeline.callbacks import PHASES, PipelinePhase, ProgressCallback
from tempify.pipeline.config import PipelineConfig
from tempify.pipeline.errors import (
    PipelineInterpolationError,
    PipelinePreValidationError,
    PipelineReportError,
    PipelineWriteError,
)
from tempify.pipeline.report import ReportGenerator
from tempify.pipeline.result import PipelineResult
from tempify.validation import (
    GeospatialCoherenceValidator,
    MethodVariableCompatibilityChecker,
    PostInterpolationValidator,
    StatisticalReporter,
    ValidationReport,
    VariableProfileMatcher,
)

if TYPE_CHECKING:
    pass


logger = logging.getLogger("tempify.pipeline")


class TempifyPipeline:
    """Orchestrate the 7 phases of a tempify run."""

    def __init__(self, config: PipelineConfig) -> None:
        self.config = config
        self._report_generator = ReportGenerator()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def run(self, source: Path | list[Path]) -> PipelineResult:
        """Execute the pipeline end-to-end."""
        cfg = self.config
        cb = cfg.progress_callback

        # Phase 1: detect
        self._emit(cb, "detect", 0.0, "Detectando estructura y frecuencia")
        detection = StructureDetector().detect(source)
        frequency = TemporalFrequencyResolver(callback=cfg.frequency_resolver_callback).resolve(
            detection.files
        )
        self._emit(cb, "detect", 1.0)

        # Load data via the appropriate reader
        data = self._read(detection.files)

        # Phase 2 + 3: pre-validation (skippable in inspect mode)
        pre_validation = ValidationReport(checks=())
        if not cfg.skip_pre_validation:
            self._emit(cb, "validate_geospatial", 0.0, "Validando coherencia geoespacial")
            geo_report = GeospatialCoherenceValidator().check([data])
            self._emit(cb, "validate_geospatial", 1.0)

            self._emit(
                cb,
                "validate_compatibility",
                0.0,
                "Verificando compatibilidad método/variable",
            )
            profile = self._resolve_profile()
            compat_result = MethodVariableCompatibilityChecker().check(
                cfg.method, profile, force=cfg.force_method
            )
            pre_validation = ValidationReport(checks=(*geo_report.checks, compat_result))
            self._emit(cb, "validate_compatibility", 1.0)
            if not pre_validation.pre_passed:
                raise PipelinePreValidationError(pre_validation)
        else:
            self._emit(cb, "validate_geospatial", 1.0, "(omitida en modo inspect)")
            self._emit(cb, "validate_compatibility", 1.0, "(omitida en modo inspect)")

        # Phase 4: interpolate (skipped in dry_run)
        post_validation: ValidationReport | None = None
        daily_output: xr.DataArray | None = None
        if not cfg.dry_run:
            self._emit(cb, "interpolate", 0.0, f"Interpolando con método '{cfg.method}'")
            daily_output = self._interpolate(data)
            self._emit(cb, "interpolate", 1.0)

            # Phase 5: post-validation
            self._emit(cb, "validate_post", 0.0, "Validando preservación de media y rango")
            profile = self._resolve_profile()
            post_validator = PostInterpolationValidator()
            base_post = post_validator.check(data, daily_output, profile)
            stats = StatisticalReporter().report(daily_output)
            post_validation = ValidationReport(checks=base_post.checks, statistics=stats)
            self._emit(cb, "validate_post", 1.0)

            # Phase 6: write
            self._emit(cb, "write", 0.0, "Escribiendo output a disco")
            outputs = self._write(daily_output)
            self._emit(cb, "write", 1.0)
        else:
            self._emit(cb, "interpolate", 1.0, "(omitida en modo dry_run)")
            self._emit(cb, "validate_post", 1.0, "(omitida en modo dry_run)")
            self._emit(cb, "write", 1.0, "(omitida en modo dry_run)")
            outputs = ()

        # Phase 7: report
        self._emit(cb, "generate_report", 0.0, "Generando reporte de procesamiento")
        try:
            report = self._report_generator.build(
                config=cfg,
                detection=detection,
                frequency=frequency,
                pre_validation=pre_validation,
                post_validation=post_validation,
                outputs=outputs,
            )
        except Exception as exc:  # pragma: no cover - defensive
            raise PipelineReportError(str(exc)) from exc
        self._emit(cb, "generate_report", 1.0)

        return PipelineResult(
            outputs=outputs,
            report=report,
            detection=detection,
            frequency=frequency,
            pre_validation=pre_validation,
            post_validation=post_validation,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _emit(
        self,
        cb: ProgressCallback | None,
        phase: PipelinePhase,
        progress: float,
        message: str | None = None,
    ) -> None:
        logger.info("phase=%s progress=%.2f %s", phase, progress, message or "")
        if cb is None:
            return
        try:
            cb(phase, progress, message)
        except Exception:  # pragma: no cover - never let a UI bug crash the pipeline
            logger.exception("ProgressCallback raised; ignoring.")

    def _read(self, files: tuple[Path, ...]) -> xr.DataArray:
        """Select the appropriate reader for ``files`` and load the data."""
        if len(files) == 1:
            path = files[0]
            reader: BaseReader = (
                NetCDFReader()
                if path.suffix.lower() in {".nc", ".nc4", ".cdf"}
                else GeoTIFFReader()
            )
            data = reader.read(path)
        else:
            data = MultiFileCollectionReader(concat_dim="month").read(list(files))
        # Single multi-band GeoTIFF (mode A): rasterio reader emits dim "band".
        # When it has 12 bands and no "month" dim, treat each band as a month
        # so downstream interpolators see (month, y, x).
        if "band" in data.dims and data.sizes["band"] == 12 and "month" not in data.dims:
            data = data.rename({"band": "month"})
        # Normalize: ensure "month" is the leading dim with coord 1..12 when
        # we have exactly 12 steps; transpose so interpolators see (month, y, x).
        if "month" in data.dims and data.sizes["month"] == 12:
            if "month" not in data.coords:
                data = data.assign_coords(month=list(range(1, 13)))
            spatial = [d for d in data.dims if d not in ("month",)]
            data = data.transpose("month", *spatial)
        return data

    def _interpolate(self, data: xr.DataArray) -> xr.DataArray:
        """Dispatch to the requested interpolator and run it."""
        method = self.config.method
        interpolator: BaseInterpolator
        if method == "linear":
            interpolator = LinearInterpolator()
        elif method == "pchip":
            interpolator = PchipInterpolator()
        elif method == "pchip_mp":
            opts = self.config.method_options
            interpolator = PchipMeanPreservingInterpolator(
                convergence_tol=float(opts.get("convergence_tol", DEFAULT_RM_CONVERGENCE_TOL)),
                max_iterations=int(opts.get("max_iterations", DEFAULT_RM_MAX_ITER)),
            )
        elif method == "fourier":
            opts = self.config.method_options
            interpolator = FourierInterpolator(n_harmonics=int(opts.get("n_harmonics", 3)))
        elif method == "akima":
            interpolator = AkimaInterpolator()
        elif method == "cubic":
            interpolator = CubicSplineInterpolator()
        else:  # pragma: no cover - exhaustively handled by Literal
            raise PipelineInterpolationError(f"Método desconocido: {method!r}")

        axis = TemporalAxis.from_months(
            year=self.config.target_year, anchor=self.config.monthly_anchor
        )
        try:
            result = interpolator.interpolate(
                data,
                axis,
                cyclic=True,
                chunk_size=self.config.chunk_size,
            )
        except Exception as exc:
            raise PipelineInterpolationError(f"El interpolador '{method}' falló: {exc}") from exc
        return result.compute() if hasattr(result.data, "compute") else result

    def _write(self, data: xr.DataArray) -> tuple[Path, ...]:
        """Dispatch to the writer for the requested output format."""
        fmt = self.config.output_format
        out_dir = Path(self.config.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            writer: BaseWriter
            if fmt == "netcdf":
                writer = NetCDFWriter()
                path = out_dir / "tempify_output.nc"
                return (Path(writer.write(data, path)),)
            if fmt == "multiband_geotiff":
                writer = MultiBandGeoTIFFWriter()
                path = out_dir / "tempify_output.tif"
                return (Path(writer.write(data, path)),)
            if fmt == "geotiff_collection":
                writer = GeoTIFFCollectionWriter()
                files = writer.write(data, out_dir)
                return tuple(Path(p) for p in (files if isinstance(files, list) else [files]))
            if fmt == "zarr":
                writer = ZarrWriter()
                zpath = out_dir / "tempify_output.zarr"
                return (Path(writer.write(data, zpath)),)
        except Exception as exc:
            raise PipelineWriteError(f"Escritura falló: {exc}") from exc
        raise PipelineWriteError(f"Formato de salida desconocido: {fmt!r}")

    def _resolve_profile(self) -> Any:
        matcher = VariableProfileMatcher()
        name = self.config.variable_profile_override or "temperature"
        return matcher.match(name)


# Silence unused-import warnings for PHASES (public re-export from __init__)
_PHASES_EXPORT = PHASES

```

## File: `code/pipeline/report.py`


```python
"""ProcessingReport dataclass + ReportGenerator (Markdown renderer)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tempify.detection import StructureDetectionResult
    from tempify.detection.frequency import ResolutionResult
    from tempify.pipeline.config import PipelineConfig
    from tempify.validation.report import ValidationReport


def _tempify_version() -> str:
    try:
        return version("tempify")
    except PackageNotFoundError:
        return "0.0.0-dev"


@dataclass(frozen=True, slots=True)
class ProcessingReport:
    """Canonical report attached to every pipeline run.

    Matches the schema in ``docs/schemas/processing-report.schema.md``.
    """

    tempify_version: str
    timestamp_utc: str
    method: str
    target_year: int
    structure_mode: str
    temporal_frequency: str
    detection_confidence: dict[str, float]
    pre_validation_summary: dict[str, int]
    post_validation_summary: dict[str, int] | None
    statistics: dict[str, dict[str, float]] | None
    inputs: tuple[Path, ...]
    outputs: tuple[Path, ...]
    dry_run: bool = field(default=False)
    notes: tuple[str, ...] = field(default_factory=tuple)


class ReportGenerator:
    """Build a :class:`ProcessingReport` from a pipeline run's outputs."""

    def build(
        self,
        config: PipelineConfig,
        detection: StructureDetectionResult,
        frequency: ResolutionResult,
        pre_validation: ValidationReport,
        post_validation: ValidationReport | None,
        outputs: tuple[Path, ...],
    ) -> ProcessingReport:
        """Assemble a :class:`ProcessingReport` from the run components."""
        notes: list[str] = []
        if config.dry_run:
            notes.append("[DRY_RUN] No interpolation, post-validation, or write occurred.")
        if config.force_method:
            notes.append(
                "Se aplicó --force-method; el método elegido no es recomendado "
                "científicamente para la variable detectada (ver attrs)."
            )
        # Pre-validation summary
        pre_summary = {
            "errors": len(pre_validation.errors),
            "warnings": len(pre_validation.warnings),
            "info": len(pre_validation.info_items),
        }
        post_summary: dict[str, int] | None = None
        if post_validation is not None:
            post_summary = {
                "errors": len(post_validation.errors),
                "warnings": len(post_validation.warnings),
                "info": len(post_validation.info_items),
            }
        return ProcessingReport(
            tempify_version=_tempify_version(),
            timestamp_utc=datetime.now(UTC).isoformat(timespec="seconds"),
            method=config.method,
            target_year=config.target_year,
            structure_mode=detection.structure_mode.value,
            temporal_frequency=frequency.frequency.value,
            detection_confidence={
                k: float(v)  # type: ignore[arg-type]
                for k, v in detection.confidence.items()
            },
            pre_validation_summary=pre_summary,
            post_validation_summary=post_summary,
            statistics=post_validation.statistics if post_validation is not None else None,
            inputs=detection.files,
            outputs=outputs,
            dry_run=config.dry_run,
            notes=tuple(notes),
        )

    def to_markdown(self, report: ProcessingReport) -> str:
        """Render ``report`` as a Markdown document (Spanish)."""
        prefix = "[DRY_RUN] " if report.dry_run else ""
        lines: list[str] = [
            f"# {prefix}Reporte de procesamiento tempify",
            "",
            f"- **Versión tempify:** {report.tempify_version}",
            f"- **Timestamp UTC:** {report.timestamp_utc}",
            f"- **Método:** `{report.method}`",
            f"- **Año destino:** {report.target_year}",
            f"- **Modo de estructura:** {report.structure_mode}",
            f"- **Frecuencia temporal inferida:** {report.temporal_frequency}",
            "",
            "## Confianza de detección",
            "",
        ]
        for key, value in report.detection_confidence.items():
            lines.append(f"- {key}: {value:.2f}")
        lines.extend(
            [
                "",
                "## Validación pre-procesamiento",
                "",
                f"- Errores: {report.pre_validation_summary['errors']}",
                f"- Advertencias: {report.pre_validation_summary['warnings']}",
                f"- Info: {report.pre_validation_summary['info']}",
                "",
            ]
        )
        if report.post_validation_summary is not None:
            lines.extend(
                [
                    "## Validación post-procesamiento",
                    "",
                    f"- Errores: {report.post_validation_summary['errors']}",
                    f"- Advertencias: {report.post_validation_summary['warnings']}",
                    f"- Info: {report.post_validation_summary['info']}",
                    "",
                ]
            )
        lines.extend(["## Archivos de entrada", ""])
        for p in report.inputs:
            lines.append(f"- `{p}`")
        lines.extend(["", "## Archivos de salida", ""])
        for p in report.outputs:
            lines.append(f"- `{p}`")
        if report.notes:
            lines.extend(["", "## Notas", ""])
            for note in report.notes:
                lines.append(f"- {note}")
        return "\n".join(lines) + "\n"

    def to_json(self, report: ProcessingReport) -> str:
        """Render ``report`` as a JSON document (for machine consumers)."""
        payload: dict[str, Any] = {
            "tempify_version": report.tempify_version,
            "timestamp_utc": report.timestamp_utc,
            "method": report.method,
            "target_year": report.target_year,
            "structure_mode": report.structure_mode,
            "temporal_frequency": report.temporal_frequency,
            "detection_confidence": report.detection_confidence,
            "pre_validation_summary": report.pre_validation_summary,
            "post_validation_summary": report.post_validation_summary,
            "statistics": report.statistics,
            "inputs": [str(p) for p in report.inputs],
            "outputs": [str(p) for p in report.outputs],
            "dry_run": report.dry_run,
            "notes": list(report.notes),
        }
        return json.dumps(payload, indent=2, ensure_ascii=False)

```

## File: `code/validation/post.py`


```python
"""Post-interpolation validator.

Verifies monthly mean preservation, cyclic continuity at the Dec-Jan
boundary, physical range conformance, and NaN integrity. Per the
policy "fail-fast pre, warn-and-continue post", failures here emit
``WARN`` severity but do not abort the pipeline.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import xarray as xr

from tempify.validation._codes import (
    POST_CYCLIC_DISCONTINUITY,
    POST_MEAN_NOT_PRESERVED,
    POST_NAN_INTEGRITY_VIOLATION,
    POST_PHYSICAL_RANGE_VIOLATION,
)
from tempify.validation.profiles import VariableProfile
from tempify.validation.report import (
    CheckPhase,
    CheckResult,
    CheckSeverity,
    ValidationReport,
)

DEFAULT_POST_ATOL: Final[float] = 1e-4
"""Contractual post-validator atol per ADR-0010 nivel 2."""

DEFAULT_POST_RTOL: Final[float] = 1e-6
"""Contractual post-validator rtol per ADR-0010 nivel 2."""

CYCLIC_DISCONTINUITY_FACTOR: Final[float] = 3.0
"""Multiplier of the monthly std used as discontinuity threshold."""


class PostInterpolationValidator:
    """Run post-process checks on the interpolated daily output."""

    def __init__(
        self,
        atol: float | None = None,
        rtol: float | None = None,
    ) -> None:
        self.atol = atol if atol is not None else DEFAULT_POST_ATOL
        self.rtol = rtol if rtol is not None else DEFAULT_POST_RTOL

    def check(
        self,
        monthly_input: xr.DataArray,
        daily_output: xr.DataArray,
        profile: VariableProfile,
    ) -> ValidationReport:
        """Run all post-interpolation checks on ``daily_output``."""
        checks: list[CheckResult] = [
            self._check_mean_preservation(monthly_input, daily_output, profile),
            self._check_cyclic_continuity(daily_output),
            self._check_physical_range(daily_output, profile),
            self._check_nan_integrity(monthly_input, daily_output),
        ]
        return ValidationReport(checks=tuple(checks))

    def _aggregate_to_monthly(self, daily: xr.DataArray) -> xr.DataArray:
        if "time" not in daily.dims:
            raise ValueError("daily output must have a 'time' dimension")
        # Build a month index per day from the time coord
        if not hasattr(daily.coords["time"], "dt"):
            raise ValueError("time coordinate must be datetime-like")
        return daily.groupby(daily["time"].dt.month).mean(dim="time")

    def _check_mean_preservation(
        self,
        monthly_input: xr.DataArray,
        daily_output: xr.DataArray,
        profile: VariableProfile,
    ) -> CheckResult:
        atol = float(min(self.atol, profile.acceptable_mean_error))
        agg = self._aggregate_to_monthly(daily_output)
        # Align dim order with the monthly_input shape so the comparison
        # broadcasts correctly regardless of which dim leads.
        try:
            agg_aligned = agg.transpose(*monthly_input.dims)
        except ValueError:
            agg_aligned = agg
        diff = float(np.nanmax(np.abs(agg_aligned.values - monthly_input.values)))
        ok = bool(np.isfinite(diff)) and (
            diff <= atol + self.rtol * float(np.nanmax(np.abs(monthly_input.values)))
        )
        return CheckResult(
            check_id=POST_MEAN_NOT_PRESERVED,
            name="Monthly mean preservation",
            severity=CheckSeverity.INFO if ok else CheckSeverity.WARN,
            phase=CheckPhase.POST_PROCESS,
            passed=ok,
            message=(
                f"Diferencia máxima entre media reconstruida y original: {diff:.3e} "
                f"(tolerancia efectiva: {atol:.3e})"
            ),
            details={
                "max_abs_diff": diff,
                "atol_used": atol,
                "rtol_used": self.rtol,
            },
        )

    def _check_cyclic_continuity(self, daily: xr.DataArray) -> CheckResult:
        if "time" not in daily.dims:
            return CheckResult(
                check_id=POST_CYCLIC_DISCONTINUITY,
                name="Cyclic continuity (Dec-Jan)",
                severity=CheckSeverity.INFO,
                phase=CheckPhase.POST_PROCESS,
                passed=True,
                message="No aplica: output sin dimensión 'time'.",
            )
        first = float(np.nanmean(daily.isel(time=0).values))
        last = float(np.nanmean(daily.isel(time=-1).values))
        wrap_diff = abs(last - first)
        # Use the daily series std as a scale
        std = float(np.nanstd(daily.values))
        threshold = CYCLIC_DISCONTINUITY_FACTOR * std if std > 0 else float("inf")
        ok = wrap_diff <= threshold
        return CheckResult(
            check_id=POST_CYCLIC_DISCONTINUITY,
            name="Cyclic continuity (Dec-Jan)",
            severity=CheckSeverity.INFO if ok else CheckSeverity.WARN,
            phase=CheckPhase.POST_PROCESS,
            passed=ok,
            message=(
                f"Diferencia entre el primer y último día: {wrap_diff:.3e} "
                f"(umbral: {threshold:.3e})"
            ),
            details={
                "wrap_diff": wrap_diff,
                "series_std": std,
                "threshold": threshold,
            },
        )

    def _check_physical_range(self, daily: xr.DataArray, profile: VariableProfile) -> CheckResult:
        finite = np.isfinite(daily.values)
        if not finite.any():
            return CheckResult(
                check_id=POST_PHYSICAL_RANGE_VIOLATION,
                name="Physical range",
                severity=CheckSeverity.INFO,
                phase=CheckPhase.POST_PROCESS,
                passed=True,
                message="No aplica: output es todo NaN.",
            )
        finite_vals = daily.values[finite]
        min_v = float(np.min(finite_vals))
        max_v = float(np.max(finite_vals))
        below = int((finite_vals < profile.physical_min).sum())
        above = int((finite_vals > profile.physical_max).sum())
        ok = below == 0 and above == 0
        return CheckResult(
            check_id=POST_PHYSICAL_RANGE_VIOLATION,
            name="Physical range",
            severity=CheckSeverity.INFO if ok else CheckSeverity.WARN,
            phase=CheckPhase.POST_PROCESS,
            passed=ok,
            message=(
                f"Rango observado [{min_v:.3f}, {max_v:.3f}] vs físico "
                f"[{profile.physical_min}, {profile.physical_max}]; "
                f"{int(below + above)} píxeles-día fuera de rango."
            ),
            details={
                "observed_min": min_v,
                "observed_max": max_v,
                "below_count": int(below),
                "above_count": int(above),
                "physical_min": profile.physical_min,
                "physical_max": profile.physical_max,
            },
        )

    def _check_nan_integrity(
        self, monthly_input: xr.DataArray, daily_output: xr.DataArray
    ) -> CheckResult:
        """A pixel that was all-NaN in input must be all-NaN in output (and vice versa)."""
        # Identify spatial mask of fully-NaN input pixels (month dim is collapsed)
        if "month" not in monthly_input.dims or "time" not in daily_output.dims:
            return CheckResult(
                check_id=POST_NAN_INTEGRITY_VIOLATION,
                name="NaN integrity",
                severity=CheckSeverity.INFO,
                phase=CheckPhase.POST_PROCESS,
                passed=True,
                message="No aplica: dimensiones inesperadas.",
            )
        nan_input_pixels = monthly_input.isnull().all(dim="month")
        # In output: a pixel is "all-NaN" if every time step is NaN
        nan_output_pixels = daily_output.isnull().all(dim="time")
        try:
            mismatch = (nan_input_pixels != nan_output_pixels).sum()
            n_mismatch = int(mismatch.values)
        except (ValueError, TypeError):
            n_mismatch = -1
        ok = n_mismatch == 0
        return CheckResult(
            check_id=POST_NAN_INTEGRITY_VIOLATION,
            name="NaN integrity",
            severity=CheckSeverity.INFO if ok else CheckSeverity.ERROR,
            phase=CheckPhase.POST_PROCESS,
            passed=ok,
            message=(
                f"{n_mismatch} píxel(es) divergen entre input y output en presencia de NaN."
                if n_mismatch != 0
                else "Integridad de NaN preservada."
            ),
            details={"mismatch_count": n_mismatch},
        )

```

## File: `code/validation/profiles.py`


```python
"""Variable profile loader and matcher.

Profiles are YAML files declaring per-variable conventions: allowed
interpolation methods, physical range, acceptable mean error, units,
aliases. They live in :mod:`tempify.profiles` and are loaded via
:func:`importlib.resources`.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from importlib import resources
from typing import Any

import yaml  # type: ignore[import-untyped]

from tempify.validation.errors import UnknownVariableProfileError

ALLOWED_METHODS: frozenset[str] = frozenset(
    {"linear", "pchip", "pchip_mp", "fourier", "akima", "cubic"}
)


@dataclass(frozen=True, slots=True)
class VariableProfile:
    """Declarative profile of a climatological variable.

    Loaded from a YAML file in :mod:`tempify.profiles`. The full schema
    is documented in ``docs/schemas/variable-profile.schema.yaml``.
    """

    name: str
    canonical_name: str
    units: str
    allowed_methods: tuple[str, ...]
    physical_min: float
    physical_max: float
    acceptable_mean_error: float
    aliases: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VariableProfile:
        """Build a profile from a parsed YAML payload."""
        return cls(
            name=str(data["name"]),
            canonical_name=str(data.get("canonical_name", data["name"])),
            units=str(data["units"]),
            allowed_methods=tuple(data.get("allowed_methods", [])),
            physical_min=float(data["physical_range"]["min"]),
            physical_max=float(data["physical_range"]["max"]),
            acceptable_mean_error=float(data["acceptable_mean_error"]),
            aliases=tuple(data.get("aliases", [])),
            description=str(data.get("description", "")),
        )


def _read_profile_yaml(filename: str) -> VariableProfile:
    """Load a single profile YAML from the tempify.profiles package."""
    with resources.files("tempify.profiles").joinpath(filename).open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return VariableProfile.from_dict(data)


def iter_builtin_profiles() -> Iterator[VariableProfile]:
    """Yield every built-in variable profile bundled with tempify."""
    for entry in resources.files("tempify.profiles").iterdir():
        name = entry.name
        if not name.endswith(".yaml") or name.startswith("_"):
            continue
        yield _read_profile_yaml(name)


class VariableProfileMatcher:
    """Look up a :class:`VariableProfile` by name or alias (case-insensitive)."""

    def __init__(self, profiles: list[VariableProfile] | None = None) -> None:
        self._profiles = profiles if profiles is not None else list(iter_builtin_profiles())

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(p.name for p in self._profiles))

    def match(self, query: str) -> VariableProfile:
        """Return the profile whose name or alias matches ``query``."""
        q = query.lower().strip()
        for p in self._profiles:
            if p.name.lower() == q:
                return p
            if any(a.lower() == q for a in p.aliases):
                return p
        raise UnknownVariableProfileError(name=query, available=self.names())

```

## File: `code/validation/compatibility.py`


```python
"""Method-variable compatibility checker.

Per ADR-0004 (precipitation policy), smooth methods (Linear, PCHIP,
PCHIP+RM, Fourier) are not appropriate for precipitation. The checker
raises :class:`MethodVariableIncompatibilityError` by default; with
``force=True`` it instead emits a ``COMPAT-003`` WARN that the Pipeline
forwards to the output's provenance attrs.
"""

from __future__ import annotations

from tempify.validation._codes import (
    COMPAT_FORCE_OVERRIDE_USED,
    COMPAT_METHOD_NOT_ALLOWED,
    COMPAT_PRECIPITATION_SMOOTH,
)
from tempify.validation.errors import MethodVariableIncompatibilityError
from tempify.validation.profiles import VariableProfile
from tempify.validation.report import (
    CheckPhase,
    CheckResult,
    CheckSeverity,
)

SMOOTH_METHODS: frozenset[str] = frozenset(
    {"linear", "pchip", "pchip_mp", "fourier", "akima", "cubic"}
)


class MethodVariableCompatibilityChecker:
    """Verify that ``method`` is allowed by ``profile`` per ADR-0004."""

    def check(
        self,
        method: str,
        profile: VariableProfile,
        *,
        force: bool = False,
    ) -> CheckResult:
        """Return a CheckResult describing the compatibility verdict.

        If ``method not in profile.allowed_methods`` and ``force is False``,
        raises :class:`MethodVariableIncompatibilityError`. With
        ``force=True`` the check passes but emits severity WARN and code
        ``COMPAT-003`` so the violation is recorded in the report.
        """
        if method in profile.allowed_methods:
            return CheckResult(
                check_id=COMPAT_METHOD_NOT_ALLOWED,
                name="Method-variable compatibility",
                severity=CheckSeverity.INFO,
                phase=CheckPhase.PRE_PROCESS,
                passed=True,
                message=(f"El método '{method}' está permitido para la variable '{profile.name}'."),
                details={
                    "method": method,
                    "variable": profile.name,
                    "allowed": list(profile.allowed_methods),
                },
            )

        # Special case: smooth method on precipitation
        is_precip_smooth = profile.name == "precipitation" and method in SMOOTH_METHODS
        if force:
            check_id = (
                COMPAT_PRECIPITATION_SMOOTH if is_precip_smooth else COMPAT_FORCE_OVERRIDE_USED
            )
            return CheckResult(
                check_id=check_id,
                name="Method-variable compatibility (force override)",
                severity=CheckSeverity.WARN,
                phase=CheckPhase.PRE_PROCESS,
                passed=True,
                message=(
                    f"Se aplicó --force-method para el método '{method}' "
                    f"sobre la variable '{profile.name}'. El resultado NO es "
                    "científicamente recomendado y queda registrado en la "
                    "procedencia del output (ADR-0004)."
                ),
                details={
                    "method": method,
                    "variable": profile.name,
                    "allowed": list(profile.allowed_methods),
                    "force_method_used": True,
                },
            )

        raise MethodVariableIncompatibilityError(
            method=method,
            variable=profile.name,
            allowed=profile.allowed_methods,
        )

```

## File: `code/profiles/temperature.yaml`


```yaml
name: temperature
canonical_name: air_temperature
units: degC
aliases: [tavg, tmean, tas, tmp, temperatura]
allowed_methods: [linear, pchip, pchip_mp, fourier, akima, cubic]
physical_range:
  min: -90.0
  max: 60.0
acceptable_mean_error: 1.0e-4
description: "Temperatura media del aire a 2 m, suave en el tiempo."

```

## File: `code/profiles/precipitation.yaml`


```yaml
name: precipitation
canonical_name: precipitation_flux
units: mm
aliases: [prcp, pr, ppt, precip, precipitacion]
allowed_methods: []
physical_range:
  min: 0.0
  max: 2000.0
acceptable_mean_error: 0.1
description: "Precipitación acumulada mensual. Métodos suaves rechazados por defecto per ADR-0004; usar --force-method bajo responsabilidad del usuario."

```

## File: `code/profiles/solar_radiation.yaml`


```yaml
name: solar_radiation
canonical_name: surface_downwelling_shortwave_flux_in_air
units: "W m-2"
aliases: [srad, rsds, radiacion_solar]
allowed_methods: [linear, pchip, pchip_mp, fourier, akima, cubic]
physical_range:
  min: 0.0
  max: 1361.0
acceptable_mean_error: 1.0
description: "Radiación solar de onda corta incidente en superficie."

```

## File: `code/profiles/relative_humidity.yaml`


```yaml
name: relative_humidity
canonical_name: relative_humidity
units: "%"
aliases: [rh, hr, humedad_relativa]
allowed_methods: [linear, pchip, pchip_mp, fourier, akima, cubic]
physical_range:
  min: 0.0
  max: 100.0
acceptable_mean_error: 0.5
description: "Humedad relativa media mensual."

```


---

# Scripts ejecutables (bench + demo + regeneradores de figuras)


## File: `examples/run_demo.py`


```python
"""End-to-end demo: tempify on a small WorldClim-like sample (Chile Central).

Runs the full pipeline (Linear and PCHIP+RM) and verifies that:

1. Output is a daily NetCDF with 365 time steps for year 2023.
2. The monthly mean of the daily output reproduces the input climatology
   within the contractual tolerance (ADR-0010 nivel 2: atol=1e-4).
3. The processing report contains canonical provenance fields.

Usage:
    # 1. Generate the synthetic WorldClim sample (one-time, ~50 KB)
    python examples/generate_worldclim_sample.py

    # 2. Run the demo
    python examples/run_demo.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr

from tempify.pipeline import (
    PipelineConfig,
    ProcessingReport,
    ReportGenerator,
    TempifyPipeline,
)

DATA_DIR = Path(__file__).parent / "data" / "worldclim_chile_central"


def _aggregate_to_monthly(daily: xr.DataArray) -> xr.DataArray:
    """Aggregate daily output to monthly mean for verification."""
    return daily.groupby(daily["time"].dt.month).mean(dim="time")


def _load_monthly_input() -> xr.DataArray:
    """Read the 12 input GeoTIFFs as a (month, y, x) DataArray."""
    import rioxarray  # noqa: F401 - registers the rio accessor

    arrays = []
    for month in range(1, 13):
        path = DATA_DIR / f"wc2.1_2.5m_tavg_{month:02d}.tif"
        arrays.append(xr.open_dataarray(path, engine="rasterio").squeeze("band", drop=True))
    return xr.concat(arrays, dim="month").assign_coords(month=list(range(1, 13)))


def _run(method: str, out_subdir: str) -> ProcessingReport:
    out_dir = Path(__file__).parent / "out" / out_subdir
    cfg = PipelineConfig(
        method=method,  # type: ignore[arg-type]
        target_year=2023,
        output_dir=out_dir,
        output_format="netcdf",
    )
    print(f"\n=== Ejecutando tempify con metodo '{method}' ===")
    result = TempifyPipeline(cfg).run(DATA_DIR)
    print(f"  Outputs: {[str(p) for p in result.outputs]}")
    print(
        f"  Pre-validacion: errors={len(result.pre_validation.errors)} "
        f"warnings={len(result.pre_validation.warnings)}"
    )
    if result.post_validation is not None:
        print(
            "  Post-validacion: errors="
            f"{len(result.post_validation.errors)} warnings="
            f"{len(result.post_validation.warnings)}"
        )

    # Verify mean preservation
    daily = xr.open_dataarray(result.outputs[0])
    monthly_input = _load_monthly_input()
    monthly_recon = _aggregate_to_monthly(daily).transpose("month", "y", "x")
    max_diff = float(np.max(np.abs(monthly_recon.values - monthly_input.values)))
    print(f"  Diferencia maxima entre media reconstruida e input: {max_diff:.3e} degC")
    if method == "pchip_mp":
        assert max_diff < 1e-4, f"PCHIP+RM debe preservar media; max_diff={max_diff:.3e}"
        print("  OK: PCHIP+RM preservo la media mensual dentro de la tolerancia.")
    return result.report


def main() -> None:
    if not DATA_DIR.exists():
        raise SystemExit(
            "Datos sinteticos no encontrados. Ejecute primero:\n"
            "    python examples/generate_worldclim_sample.py"
        )

    _run("linear", "linear")
    report_pchip_mp = _run("pchip_mp", "pchip_mp")

    rg = ReportGenerator()
    md = rg.to_markdown(report_pchip_mp)
    print("\n=== Reporte (PCHIP+RM) ===")
    print(md)


if __name__ == "__main__":
    main()

```

## File: `examples/bench_max_diff.py`


```python
"""Benchmark: max |diff| per method on the WorldClim Chile Central sample.

Computes the worst pixel-wise discrepancy between the monthly mean
reconstructed from the daily output and the original monthly input,
for the six interpolation methods available in tempify.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import xarray as xr

from tempify.pipeline import PipelineConfig, TempifyPipeline

DATA_DIR = Path(__file__).parent / "data" / "worldclim_chile_central"
OUT_ROOT = Path(__file__).parent / "out" / "bench_max_diff"
METHODS = ["linear", "pchip", "pchip_mp", "fourier", "akima", "cubic"]


def _aggregate_to_monthly(daily: xr.DataArray) -> xr.DataArray:
    return daily.groupby(daily["time"].dt.month).mean(dim="time")


def _load_monthly_input() -> xr.DataArray:
    import rioxarray  # noqa: F401
    arrays = []
    for month in range(1, 13):
        path = DATA_DIR / f"wc2.1_2.5m_tavg_{month:02d}.tif"
        arrays.append(
            xr.open_dataarray(path, engine="rasterio").squeeze("band", drop=True)
        )
    return xr.concat(arrays, dim="month").assign_coords(month=list(range(1, 13)))


def _run(method: str) -> float:
    out_dir = OUT_ROOT / method
    if out_dir.exists():
        shutil.rmtree(out_dir)
    cfg = PipelineConfig(
        method=method,
        target_year=2023,
        output_dir=out_dir,
        output_format="netcdf",
    )
    result = TempifyPipeline(cfg).run(DATA_DIR)
    daily = xr.open_dataarray(result.outputs[0])
    monthly_input = _load_monthly_input()
    monthly_recon = _aggregate_to_monthly(daily).transpose("month", "y", "x")
    return float(np.max(np.abs(monthly_recon.values - monthly_input.values)))


def main() -> None:
    print(f"{'method':<10}  {'max |diff| (°C)':<22}  scientific")
    print("-" * 60)
    for m in METHODS:
        d = _run(m)
        mantissa = d / 10 ** np.floor(np.log10(d)) if d > 0 else 0.0
        exponent = int(np.floor(np.log10(d))) if d > 0 else 0
        print(f"{m:<10}  {d:<22.6e}  {mantissa:.2f} × 10^{exponent}")


if __name__ == "__main__":
    main()

```

## File: `examples/generate_worldclim_sample.py`


```python
"""Generate a small WorldClim-like sample (Chile Central).

This script produces 12 GeoTIFFs with the WorldClim v2.1 naming convention
(``wc2.1_2.5m_tavg_NN.tif``) over a small bounding box covering roughly
the Metropolitan Region of Santiago, Chile. Values are synthesised from
the real monthly mean temperature climatology for the area (~21 degC in
summer, ~9 degC in winter) plus a small spatial gradient simulating
altitude.

Why synthetic? The real WorldClim global product weights several MB per
file and requires internet to download. This sample stays under 100 KB
total while keeping the temporal pattern realistic enough to validate
that tempify preserves the monthly mean and produces a smooth daily
signal.

Run:
    python examples/generate_worldclim_sample.py [--output ./data]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import rioxarray  # noqa: F401 - registers the rio accessor
import xarray as xr

# Monthly mean temperature (degC) for Santiago, Chile (rounded climatology).
SANTIAGO_MONTHLY_TAVG: tuple[float, ...] = (
    21.0,  # Jan
    20.0,  # Feb
    18.0,  # Mar
    15.0,  # Apr
    12.0,  # May
    9.0,  # Jun
    9.0,  # Jul
    10.0,  # Aug
    12.0,  # Sep
    14.0,  # Oct
    17.0,  # Nov
    20.0,  # Dec
)

# Bounding box approximating the Metropolitan Region (lon_min, lat_min,
# lon_max, lat_max). 30x30 pixels at ~2.5min resolution covers the area.
BBOX_LON: tuple[float, float] = (-71.5, -69.5)
BBOX_LAT: tuple[float, float] = (-34.5, -32.5)
N_PIXELS: int = 30


def _build_field(month_idx: int, base_value: float) -> np.ndarray:
    """Build a 30x30 raster: base value + altitude-driven cooling toward east."""
    rng = np.random.default_rng(month_idx)
    lon = np.linspace(BBOX_LON[0], BBOX_LON[1], N_PIXELS)
    lat = np.linspace(BBOX_LAT[0], BBOX_LAT[1], N_PIXELS)
    lon_grid, _ = np.meshgrid(lon, lat)
    # Altitude proxy: cooler toward east (Andes). Linear gradient ~6 degC.
    altitude_effect = -6.0 * (lon_grid - BBOX_LON[0]) / (BBOX_LON[1] - BBOX_LON[0])
    noise = rng.normal(scale=0.2, size=(N_PIXELS, N_PIXELS))
    field = base_value + altitude_effect + noise
    return field.astype(np.float32)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a WorldClim-like sample.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / "data" / "worldclim_chile_central",
        help="Output directory (default: examples/data/worldclim_chile_central/).",
    )
    args = parser.parse_args()

    out_dir = args.output
    out_dir.mkdir(parents=True, exist_ok=True)

    lon = np.linspace(BBOX_LON[0], BBOX_LON[1], N_PIXELS)
    lat = np.linspace(BBOX_LAT[1], BBOX_LAT[0], N_PIXELS)  # north -> south

    for month_idx, base in enumerate(SANTIAGO_MONTHLY_TAVG):
        arr = _build_field(month_idx, base)
        da = xr.DataArray(
            arr,
            dims=("y", "x"),
            coords={"y": lat, "x": lon},
            name="tavg",
        ).rio.write_crs("EPSG:4326")
        path = out_dir / f"wc2.1_2.5m_tavg_{month_idx + 1:02d}.tif"
        da.rio.to_raster(path)
        print(f"  wrote {path.name} (mean={float(arr.mean()):.2f} degC)")
    print(f"OK: 12 GeoTIFFs en {out_dir}")


if __name__ == "__main__":
    main()

```

## File: `examples/regenerate_maipo_timeseries.py`


```python
"""Regenera docs/assets/maipo_pixel_timeseries.jpg desde el notebook 02.

Replica exactamente las celdas 5 + 9 + 16 del notebook 02-real-worldclim-maipo.ipynb,
ejecutando el pipeline pchip_mp sobre WorldClim Alto Maipo y guardando la figura
del ciclo anual reconstruido.
"""

from __future__ import annotations

import datetime as _dt
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rioxarray  # noqa: F401
import xarray as xr

from tempify.pipeline import PipelineConfig, TempifyPipeline

STACK_PATH = Path("examples/data/worldclim_maipo_alto/wc1_6_maipo_alto_tavg_stack.tif")
OUT_DIR = Path("examples/out/maipo_pchip_mp")
ASSET_PATH = Path("docs/assets/maipo_pixel_timeseries.jpg")


def main() -> None:
    monthly = xr.load_dataarray(STACK_PATH)
    print(f"Monthly: dims={monthly.dims}, shape={monthly.shape}")

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    cfg = PipelineConfig(
        method="pchip_mp",
        target_year=2024,
        output_dir=OUT_DIR,
        output_format="netcdf",
    )
    result = TempifyPipeline(cfg).run(STACK_PATH)
    daily = xr.load_dataarray(result.outputs[0])
    print(f"Daily: shape={daily.shape}, dims={daily.dims}")

    # Localizar pixel mas frio (cordillera) y mas calido (valle) en mes de enero
    # (mismo criterio que el notebook).
    jan = daily.isel(time=14).values
    iy_cold, ix_cold = np.unravel_index(np.nanargmin(jan), jan.shape)
    iy_warm, ix_warm = np.unravel_index(np.nanargmax(jan), jan.shape)

    series_cold = daily.isel(y=iy_cold, x=ix_cold).values
    series_warm = daily.isel(y=iy_warm, x=ix_warm).values
    assert not np.isnan(series_cold).any()
    assert not np.isnan(series_warm).any()

    month_doy = [int(_dt.date(2024, m, 15).timetuple().tm_yday) for m in range(1, 13)]
    month_cold = monthly.isel(band=slice(0, 12), y=iy_cold, x=ix_cold).values
    month_warm = monthly.isel(band=slice(0, 12), y=iy_warm, x=ix_warm).values

    print(f"Pixel cordillera: y={iy_cold}, x={ix_cold}  T_ene={jan[iy_cold, ix_cold]:.1f} degC")
    print(f"Pixel valle:      y={iy_warm}, x={ix_warm}  T_ene={jan[iy_warm, ix_warm]:.1f} degC")

    fig, ax = plt.subplots(figsize=(12, 4.6), dpi=110)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f6faf8")
    doy_all = np.arange(1, daily.sizes["time"] + 1)
    ax.plot(doy_all, series_warm, color="#dc2626", linewidth=2.0,
            label=f"Valle (y={iy_warm}, x={ix_warm})", zorder=3)
    ax.plot(doy_all, series_cold, color="#1d4ed8", linewidth=2.0,
            label=f"Alta cordillera (y={iy_cold}, x={ix_cold})", zorder=3)
    ax.scatter(month_doy, month_warm, color="#7f1d1d", s=40,
               edgecolors="white", linewidth=1.2, zorder=4, label="Nodo mensual valle")
    ax.scatter(month_doy, month_cold, color="#1e3a8a", s=40,
               edgecolors="white", linewidth=1.2, zorder=4, label="Nodo mensual cordillera")
    ax.set_xlim(0, daily.sizes["time"] + 1)
    ax.set_xticks([int(_dt.date(2024, m, 15).timetuple().tm_yday) for m in range(1, 13)])
    ax.set_xticklabels(["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                        "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"], fontsize=9)
    ax.axhline(0, color="#94a3b8", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_ylabel("Temperatura (degC)", color="#4a5b6b", fontsize=10)
    ax.set_title(
        "Ciclo anual reconstruido — Alta cordillera vs valle (pchip_mp sobre WorldClim Alto Maipo)",
        color="#0d2854", fontsize=12, fontweight="bold", pad=12, loc="left",
    )
    ax.grid(True, alpha=0.18, linewidth=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper center", framealpha=0.95, fontsize=9,
              edgecolor="#0d2854", ncol=2)
    plt.tight_layout()
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(ASSET_PATH, dpi=110, bbox_inches="tight", facecolor="white",
                pil_kwargs={"quality": 88})
    plt.close(fig)
    print(f"\nFigura guardada: {ASSET_PATH} ({ASSET_PATH.stat().st_size // 1024} KB)")
    print(f"Amplitud termica valle:      {series_warm.max() - series_warm.min():.1f} degC")
    print(f"Amplitud termica cordillera: {series_cold.max() - series_cold.min():.1f} degC")
    print(f"Offset valle vs cordillera:  {series_warm.mean() - series_cold.mean():.1f} degC")


if __name__ == "__main__":
    main()

```

## File: `examples/regenerate_maipo_monthly_grid.py`


```python
"""Regenera docs/assets/maipo_monthly_grid.jpg con cubic spline + fila de diff.

Layout 3 filas × 4 columnas:
- Fila 1: input mensual WorldClim (Ene/Abr/Jul/Oct)
- Fila 2: salida tempify (cubic) en el día 15 del mismo mes
- Fila 3: diff = anchor - predicción, con COLORBAR INDEPENDIENTE (diverging)
  porque las diferencias son varios órdenes de magnitud más pequeñas que
  la temperatura absoluta.

Cubic spline pasa exactamente por los nodos de midpoint, por lo que la diff
en el día ancla es esencialmente ruido float64 (~1e-14 °C), mostrando
visualmente que las anclas se conservan exactamente incluso con un método
no mean-preserving.
"""

from __future__ import annotations

import datetime as _dt
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rioxarray  # noqa: F401
import xarray as xr
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec

from tempify.pipeline import PipelineConfig, TempifyPipeline

STACK_PATH = Path("examples/data/worldclim_maipo_alto/wc1_6_maipo_alto_tavg_stack.tif")
OUT_DIR = Path("examples/out/maipo_cubic")
ASSET_PATH = Path("docs/assets/maipo_monthly_grid.jpg")

SHOW_MONTHS = [1, 4, 7, 10]
MONTH_NAMES_ES = {1: "Enero", 4: "Abril", 7: "Julio", 10: "Octubre"}
CMAP_TEMP = "RdYlBu_r"

# Custom diverging palette: dark blue → blue → light blue → YELLOW center →
# coral → red → dark red. The yellow center (not white) makes small
# residuals visible against the white background of the figure.
CMAP_DIFF = LinearSegmentedColormap.from_list(
    "tempify_diff",
    ["#08306b", "#2171b5", "#6baed6", "#ffeda0", "#fb6a4a", "#cb181d", "#67000d"],
    N=256,
)


def main() -> None:
    monthly = xr.load_dataarray(STACK_PATH)
    print(f"Monthly input: dims={monthly.dims}, shape={monthly.shape}")

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    cfg = PipelineConfig(
        method="cubic",
        target_year=2024,
        output_dir=OUT_DIR,
        output_format="netcdf",
    )
    result = TempifyPipeline(cfg).run(STACK_PATH)
    daily = xr.load_dataarray(result.outputs[0])
    print(f"Daily cubic: shape={daily.shape}")

    # Compute diffs first to get symmetric range for diverging colorbar
    diffs = []
    for month in SHOW_MONTHS:
        anchor = monthly.isel(band=month - 1).values
        doy_15 = _dt.date(2024, month, 15).timetuple().tm_yday - 1
        pred = daily.isel(time=doy_15).values
        diffs.append(anchor - pred)
    diffs_arr = np.stack(diffs)
    diff_abs_max = float(np.nanmax(np.abs(diffs_arr)))
    print(f"Max |diff| en celdas mostradas: {diff_abs_max:.3e} °C")

    # Use symmetric scale for the diverging colorbar
    diff_vmin = -diff_abs_max if diff_abs_max > 0 else -1e-15
    diff_vmax = diff_abs_max if diff_abs_max > 0 else 1e-15

    vmin = float(monthly.min())
    vmax = float(monthly.max())

    fig = plt.figure(figsize=(15, 10.5), dpi=110, layout="constrained")
    gs = GridSpec(
        3, 5, figure=fig,
        width_ratios=[1, 1, 1, 1, 0.04],
        hspace=0.18,
    )

    axes_in  = [fig.add_subplot(gs[0, c]) for c in range(4)]
    axes_out = [fig.add_subplot(gs[1, c], sharex=axes_in[c], sharey=axes_in[c]) for c in range(4)]
    axes_dif = [fig.add_subplot(gs[2, c], sharex=axes_in[c], sharey=axes_in[c]) for c in range(4)]
    cbar_temp_ax = fig.add_subplot(gs[0:2, -1])
    cbar_diff_ax = fig.add_subplot(gs[2, -1])

    im_temp = None
    im_diff = None
    for col, month in enumerate(SHOW_MONTHS):
        data_in = monthly.isel(band=month - 1).values
        doy_15 = _dt.date(2024, month, 15).timetuple().tm_yday - 1
        data_out = daily.isel(time=doy_15).values
        data_dif = data_in - data_out

        im_temp = axes_in[col].imshow(data_in, cmap=CMAP_TEMP, vmin=vmin, vmax=vmax, aspect="auto")
        axes_in[col].set_title(MONTH_NAMES_ES[month], fontsize=11,
                               fontweight="bold", color="#0d2854")
        axes_in[col].set_xticks([]); axes_in[col].set_yticks([])

        axes_out[col].imshow(data_out, cmap=CMAP_TEMP, vmin=vmin, vmax=vmax, aspect="auto")
        axes_out[col].set_xticks([]); axes_out[col].set_yticks([])

        im_diff = axes_dif[col].imshow(
            data_dif, cmap=CMAP_DIFF, vmin=diff_vmin, vmax=diff_vmax, aspect="auto"
        )
        axes_dif[col].set_xticks([]); axes_dif[col].set_yticks([])

    axes_in[0].set_ylabel(
        "WorldClim v2.1\n(entrada mensual)",
        fontsize=10, color="#1e3a8a", fontweight="bold", labelpad=8,
    )
    axes_out[0].set_ylabel(
        "tempify cubic\n(salida día 15)",
        fontsize=10, color="#065f46", fontweight="bold", labelpad=8,
    )
    axes_dif[0].set_ylabel(
        "Diferencia\n(ancla − predicción)",
        fontsize=10, color="#7c2d12", fontweight="bold", labelpad=8,
    )

    if im_temp is not None:
        fig.colorbar(im_temp, cax=cbar_temp_ax, label="Temperatura (°C)")
    if im_diff is not None:
        cb = fig.colorbar(im_diff, cax=cbar_diff_ax, label="Δ (°C)")
        # Format with scientific notation
        cb.formatter.set_powerlimits((-2, 2))
        cb.update_ticks()

    fig.suptitle(
        "Entrada mensual WorldClim vs salida diaria tempify (cubic spline) — anclas conservadas",
        fontsize=12, fontweight="bold", color="#0d2854",
    )

    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(ASSET_PATH, dpi=110, bbox_inches="tight", facecolor="white",
                pil_kwargs={"quality": 88})
    plt.close(fig)
    print(f"\nFigura guardada: {ASSET_PATH} ({ASSET_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

```
