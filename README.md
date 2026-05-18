# tempify

> **Densificación temporal para stacks ráster geoespaciales.**
> *Generate more data between your existing data.*

[![Tests](https://img.shields.io/badge/tests-241%20passing-brightgreen)](https://github.com/djwillichile/tempify/actions)
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)](https://github.com/djwillichile/tempify)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20265222.svg)](https://doi.org/10.5281/zenodo.20265222)


## ¿Qué es?

`tempify` es una librería Python + CLI que realiza **densificación temporal** sobre stacks ráster geoespaciales. Toma una serie de rásters muestreada a baja frecuencia (por ejemplo, 12 valores mensuales) y genera una serie densa (365 o 366 valores diarios) preservando propiedades estadísticas críticas como la conservación de la media mensual.

Análogo conceptual: igual que la **interpolación de fotogramas** genera frames intermedios para un video más fluido, `tempify` genera valores temporales intermedios para un stack ráster más denso.

## ¿Para qué sirve?

Numerosos productos geoespaciales se distribuyen a frecuencia mensual o climatológica (WorldClim, CHELSA, TerraClimate, CRU-TS), pero múltiples aplicaciones requieren resolución diaria:

- Cálculo de grados-día (GDD)
- Modelos de evapotranspiración (Hargreaves-Samani, Penman-Monteith)
- Índices bioclimáticos derivados
- Modelos hidrológicos distribuidos
- Modelos de distribución de especies (SDM) con cubiertas climáticas diarias
- Modelación regional de calidad del aire

`tempify` automatiza esa conversión con métodos validados experimentalmente y trazabilidad metodológica completa.

## ¿Qué no es?

- No es un GIS general (no reproyecta, no recorta).
- No hace downscaling espacial (la resolución espacial no cambia).
- No es un weather generator estocástico (no inventa variabilidad sinóptica).
- No interpola precipitación con métodos suaves (rechazado por diseño).

## Tutoriales

| Notebook | Descripción | Colab |
|----------|-------------|-------|
| [`01-getting-started.ipynb`](docs/tutorials/01-getting-started.ipynb) | Introducción a la API: datos sintéticos WorldClim-like, cuatro métodos de interpolación, conservación de media mensual, reporte de procedencia, visualización 3D. | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/djwillichile/tempify/blob/main/docs/tutorials/01-getting-started.ipynb) |
| [`02-real-worldclim-maipo.ipynb`](docs/tutorials/02-real-worldclim-maipo.ipynb) | Caso real con datos WorldClim v2.1 descargados para la cuenca del Maipo (Chile). Densificación mensual → diaria, análisis espacial y validación de conservación. | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/djwillichile/tempify/blob/main/docs/tutorials/02-real-worldclim-maipo.ipynb) |

## Instalación

```bash
# Desde el repo (recomendado para v0.1.0)
git clone https://github.com/djwillichile/tempify.git
cd tempify
pip install -e ".[dev]"

# pip / conda-forge: planificado para v0.1.x cuando el paquete suba a PyPI
```

Requiere Python 3.11, 3.12 o 3.13.

## Ejemplo mínimo

```bash
# CLI
tempify convert ./worldclim_chile/ \
    --method pchip_mp \
    --year 2023 \
    --output ./out/ \
    --report ./out/report.md
```

```python
# API Python
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

## Métodos disponibles

| Método | Descripción | Recomendado para |
|---|---|---|
| `linear` | Interpolación lineal entre nodos | Prototipos rápidos |
| `pchip` | Piecewise Cubic Hermite (shape-preserving) | Uso general |
| `pchip_mp` | PCHIP + Rymes-Myers mean-preserving | **Producto final, máxima fidelidad** |
| `fourier` | Ajuste armónico (1-5 armónicos) | Representación paramétrica del ciclo |
| `akima` | Akima 1970 (C¹, menos overshoot que cubic) | Variables con cambios bruscos |
| `cubic` | Spline natural C² | Señales muy suaves (puede overshoot) |

## Estado del proyecto

**v0.1.0 — primer release funcional** (2026-05-16). Capas 1-6 implementadas (I/O, Detection, Validation, Interpolation, Pipeline, CLI), 241 tests passing, 91% coverage, 17 ADRs documentados.

**Diferido a v0.2.0:** GUI PySide6, instalador Windows .exe, integración de redes neuronales pre-entrenadas bajo patrón híbrido (ver [ADR-0017](docs/adr/0017-neural-interpolator-extensibility.md)).

Este repositorio sigue **Spec-Driven Development** y **Harness Engineering**. Toda implementación está precedida por una spec aprobada en `specs/`. Ver `CLAUDE.md` para el régimen de trabajo.

## Ejemplo rápido (WorldClim Chile Central)

Demo end-to-end sobre 12 GeoTIFFs sintéticos que reproducen la
climatología real de temperatura media mensual de la Región
Metropolitana de Santiago (≈21 °C verano, 9 °C invierno) con la
convención de nombres de WorldClim v2.1.

```bash
# 1. Generar los archivos sinteticos (~50 KB, no requiere internet)
python examples/generate_worldclim_sample.py

# 2. Convertir mensual a diario via CLI
tempify convert examples/data/worldclim_chile_central \
    --method pchip_mp \
    --year 2023 \
    --output examples/out/cli \
    --report examples/out/cli/report.md

# 3. (opcional) Ejecutar el demo Python que verifica numericamente
python examples/run_demo.py
```

Verifica end-to-end que: detección automática (mode B + climatological
WorldClim), pipeline completo de 7 fases, NetCDF diario CF-compliant
de salida, conservación de media mensual <1e-4 °C, y reporte de
procedencia con MD5 de inputs. Ver `examples/README.md`.

## Estructura del repositorio

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

## Documentación

- Tutoriales: `docs/tutorials/`
- Notas metodológicas: `docs/methodology/`
- Architecture Decision Records: `docs/adr/`

## Contribuir

Este proyecto sigue Spec-Driven Development estricto. Para contribuir:

1. Lee `CLAUDE.md` y `steering/harness.md` para entender el régimen de trabajo.
2. Abre un issue describiendo la feature antes de iniciar trabajo.
3. Las contribuciones se discuten primero a nivel de spec, después en código.

## Licencia

MIT License. Ver `LICENSE`.

## Citar este software

Para metadatos completos (autores, afiliación, ORCID) ver [CITATION.cff](CITATION.cff). Todas las entradas BibTeX están en [`REFERENCES.bib`](REFERENCES.bib).

> Fuentes-Jaque, G. S. (2026). *tempify: Temporal densification for geospatial raster stacks* (v0.1.5) \[Software\]. ICTA Ltda.; Universidad San Sebastián; Universidad de Chile. https://doi.org/10.5281/zenodo.20265222

## Referencias bibliográficas de los métodos

Las publicaciones originales detrás de cada método de interpolación que `tempify` implementa. Si usás un método específico en una publicación científica, citá también el paper correspondiente (no solo el paquete). Todas las revistas están indexadas en Web of Science / JCR. Entradas BibTeX en [`REFERENCES.bib`](REFERENCES.bib).

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

> **Sobre datasets de referencia.** Si usás datos WorldClim para validar tu pipeline, citá también:
>
> Fick, S. E., & Hijmans, R. J. (2017). WorldClim 2: New 1-km spatial resolution climate surfaces for global land areas. *International Journal of Climatology*, *37*(12), 4302–4315. https://doi.org/10.1002/joc.5086
>
> El stack `examples/data/worldclim_maipo_alto/` que distribuimos es un recorte derivado de ese producto.

## Contacto

**ICTA Ltda.** · Santiago, Chile · Mantenedor: Guillermo Fuentes-Jaque

- Email institucional: [contacto@icta.cl](mailto:contacto@icta.cl)
- Sitio web: [icta.cl](https://icta.cl)
- WhatsApp: [+56 9 9292 4314](https://wa.me/56992924314)
- Email del mantenedor: [guillermo@icta.cl](mailto:guillermo@icta.cl)
- Issues técnicos: usa el [issue tracker de GitHub](https://github.com/djwillichile/tempify/issues) en lugar de los canales anteriores.
