# tempify

> **Densificación temporal para stacks ráster geoespaciales.**
> *Generate more data between your existing data.*

[![Tests](https://img.shields.io/badge/tests-241%20passing-brightgreen)](https://github.com/djwillichile/tempify/actions)
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)](https://github.com/djwillichile/tempify)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20297689.svg)](https://zenodo.org/records/20297689)


## ¿Qué es?

`tempify` es una librería Python + CLI que realiza **densificación temporal** sobre stacks ráster geoespaciales. Toma una serie de rásters muestreada a baja frecuencia (por ejemplo, 12 valores mensuales) y genera una serie densa (365 o 366 valores diarios) preservando propiedades estadísticas críticas como la conservación de la media mensual.

Análogo conceptual: igual que la **interpolación de fotogramas** genera frames intermedios para un video más fluido, `tempify` genera valores temporales intermedios para un stack ráster más denso.

## ¿Para qué sirve?

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

## ¿Qué no es?

- No es un GIS general (no reproyecta, no recorta).
- No hace downscaling espacial (la resolución espacial no cambia).
- No es un weather generator estocástico (no inventa variabilidad sinóptica).
- No interpola precipitación con métodos suaves (rechazado por diseño).

## Tutoriales

| Notebook | Descripción |
|----------|-------------|
| [`01-getting-started.ipynb`](docs/tutorials/01-getting-started.ipynb) | Introducción a la API: datos sintéticos WorldClim-like, seis métodos de interpolación, conservación de media mensual, reporte de procedencia, visualización 3D. [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/djwillichile/tempify/blob/main/docs/tutorials/01-getting-started.ipynb) |
| [`02-real-worldclim-maipo.ipynb`](docs/tutorials/02-real-worldclim-maipo.ipynb) | Caso real con datos WorldClim v2.1 descargados para la cuenca del Maipo (Chile). Densificación mensual → diaria, análisis espacial y validación de conservación. [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/djwillichile/tempify/blob/main/docs/tutorials/02-real-worldclim-maipo.ipynb) |

## Instalación

```bash
# Desde el repo (recomendado para v0.1.x)
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

**v0.1.5** (2026-05-18) — Módulos auxiliares `datasets`, `utils`, `plotting`; seis métodos de interpolación (`akima` y `cubic` agregados en v0.1.4); notebooks simplificados. Ver [CHANGELOG](CHANGELOG.md).

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

> Fuentes-Jaque, G. S. (2026). *tempify: Temporal densification for geospatial raster stacks* (v0.1.6) \[Software\]. ICTA Ltda.; Universidad San Sebastián; Universidad de Chile. https://doi.org/10.5281/zenodo.20297689

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

> **Sobre datasets de referencia.** El stack `examples/data/worldclim_maipo_alto/` que distribuimos es un recorte derivado de WorldClim v2.1. Si lo usás en publicaciones, citá el producto original.

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

## Contacto

**ICTA Ltda.** · Santiago, Chile · Mantenedor: Guillermo Fuentes-Jaque

- Email institucional: [contacto@icta.cl](mailto:contacto@icta.cl)
- Sitio web: [icta.cl](https://icta.cl)
- WhatsApp: [+56 9 9292 4314](https://wa.me/56992924314)
- Email del mantenedor: [guillermo@icta.cl](mailto:guillermo@icta.cl)
- Issues técnicos: usa el [issue tracker de GitHub](https://github.com/djwillichile/tempify/issues) en lugar de los canales anteriores.
