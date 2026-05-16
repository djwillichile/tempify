# tempify

> **Densificación temporal para stacks ráster geoespaciales.**
> *Generate more data between your existing data.*

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

## Instalación (planificada)

```bash
pip install tempify
# o
conda install -c conda-forge tempify
```

## Ejemplo mínimo (planificado)

```bash
# CLI
tempify convert ./worldclim_chile/ \
    --method pchip_mp \
    --output ./worldclim_chile_daily.nc
```

```python
# API Python
from tempify import densify_temporal
import xarray as xr

monthly = xr.open_dataset("worldclim_monthly.nc")["tavg"]
daily = densify_temporal(monthly, target_freq="daily", method="pchip_mp")
daily.to_netcdf("worldclim_daily.nc")
```

## Métodos disponibles

| Método | Descripción | Recomendado para |
|---|---|---|
| `linear` | Interpolación lineal entre nodos | Prototipos rápidos |
| `pchip` | Piecewise Cubic Hermite (shape-preserving) | Uso general |
| `pchip_mp` | PCHIP + Rymes-Myers mean-preserving | **Producto final, máxima fidelidad** |
| `fourier` | Ajuste armónico (1-5 armónicos) | Representación paramétrica del ciclo |

## Estado del proyecto

🚧 **En desarrollo activo.** Versión 0.1.0-dev.

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

Una vez publicado:

```
Fuentes-Jaque, G. (2026). tempify: Temporal densification for geospatial
raster stacks. [Software]. DOI: 10.5281/zenodo.XXXXXXX
```

## Contacto

**ICTA Ltda.** · Santiago, Chile · Mantenedor: Guillermo Fuentes-Jaque

- Email institucional: [contacto@icta.cl](mailto:contacto@icta.cl)
- Sitio web: [icta.cl](https://icta.cl)
- WhatsApp: [+56 9 9292 4314](https://wa.me/56992924314)
- Email del mantenedor: [guillermo@icta.cl](mailto:guillermo@icta.cl)
- Issues técnicos: usa el [issue tracker de GitHub](https://github.com/djwillichile/tempify/issues) en lugar de los canales anteriores.
