# Processing Report Schema

## Propósito

El **processing report** es el artefacto de trazabilidad principal que emite `tempify convert --report <path.md>`. Su función es triple:

1. **Trazabilidad.** Documentar exactamente qué entradas se consumieron, qué decisiones automáticas tomó el motor (detección, validación, selección de método) y qué salidas se produjeron.
2. **Reproducibilidad.** Capturar todos los parámetros, hashes (MD5 de inputs/outputs) y metadatos de entorno necesarios para que un tercero pueda repetir la corrida y obtener resultados bit-exact (modo `strict`) o estadísticamente equivalentes (modo `parallel`). Ver ADR-0007.
3. **Comunicación con el usuario.** Servir como documento legible por humanos (Markdown renderizable en el visor GUI, en GitHub o en cualquier editor) que explique en lenguaje técnico qué pasó durante la conversión, qué warnings se emitieron y qué confianza tuvo el sistema en sus inferencias.

El reporte es **autocontenido**: incluye un bloque YAML de procedencia embebido que basta para reconstruir la invocación CLI equivalente sin acceso a logs externos.

## Estructura del archivo

El reporte es un Markdown con secciones fijas, en este orden:

1. **Encabezado** — versión del paquete, timestamp ISO-8601 UTC, modo de reproducibilidad, plataforma.
2. **Inputs** — tabla con: path, MD5, tamaño, formato, dimensiones, CRS.
3. **Detección** — modo (A/B/C), frecuencia temporal, perfil de variable, confidence dict completo.
4. **Validación pre-procesamiento** — resultado del `GeospatialCoherenceValidator` y `MethodVariableCompatibilityChecker`. Cada check con estado (PASS/WARN/FAIL) y mensaje.
5. **Parámetros de interpolación** — método, opciones específicas (n_harmonics, convergence_tol, etc.), chunk_size, scheduler.
6. **Estadísticas pre y post** — tabla con min/max/mean/std/nan% por banda mensual de entrada y por banda diaria agregada de salida.
7. **Validación post-procesamiento** — resultado del `PostInterpolationValidator` (conservación de media, continuidad cíclica, rango físico).
8. **Outputs** — path, MD5, tamaño, formato.
9. **Procedencia** — bloque YAML embebido en el Markdown con todos los campos necesarios para reproducir.

Cada sección debe estar precedida por un encabezado Markdown de nivel 2 (`## <Nombre>`). Subsecciones opcionales usan nivel 3 (`### <Nombre>`). El visor GUI (spec `gui`) renderiza estas secciones como pestañas o paneles colapsables.

## Schema YAML del bloque de procedencia

El bloque de procedencia (sección 9) sigue este shape:

```yaml
tempify_version: "0.1.0"
timestamp_utc: "2026-05-16T14:32:11Z"
platform: "Windows-10.0.22631-x86_64"
python_version: "3.11.8"
reproducibility_mode: "parallel"  # o "strict"
dask_scheduler: "threaded"  # o "synchronous"
config:
  method: "pchip_mp"
  method_options:
    convergence_tol: 1.0e-6
    max_iterations: 50
  chunk_size: 512
  variable_profile: "temperature"
  force_method_used: false
inputs:
  - path: "..."
    md5: "..."
    bytes: 12345
outputs:
  - path: "..."
    md5: "..."
    bytes: 67890
detection_confidence:
  structure_mode: 1.0
  temporal_frequency: 0.95
  temporal_frequency_tier: 1.0
  variable_profile: 0.9
  homogeneity: 1.0
  overall: 0.97
warnings: []
errors: []
```

Notas sobre los campos:

- `reproducibility_mode`: `"strict"` fuerza `dask_scheduler: "synchronous"` y desactiva paralelismo no determinista; `"parallel"` permite `threaded` o `processes` (ver ADR-0007).
- `detection_confidence`: claves alineadas con el contrato del `DetectionResult` (ADR-0008). El campo `temporal_frequency_tier` refleja qué tier de inferencia se usó (1.0 = CF metadata, 0.7 = nomenclatura, 0.4 = heurística, 0.0 = prompt usuario).
- `force_method_used`: `true` si el usuario sobreescribió la recomendación del `MethodVariableCompatibilityChecker` mediante `--force-method`.
- `warnings` y `errors`: arrays de strings; vacíos si no hubo eventos.
- Los hashes MD5 se computan sobre el contenido binario íntegro del archivo. Para colecciones de monocapas (modo B/C), `inputs` contiene una entrada por archivo.

## Ejemplo completo

```markdown
# Processing Report — tempify

## Encabezado
- **Package:** tempify 0.1.0
- **Timestamp (UTC):** 2026-05-16T14:32:11Z
- **Reproducibility mode:** parallel
- **Platform:** Windows-10.0.22631-x86_64 / Python 3.11.8

## Inputs
| Path | MD5 | Size | Format | Dims | CRS |
|------|-----|------|--------|------|-----|
| wc2.1_10m_tavg.tif | 4f3a...c1 | 18.4 MB | GeoTIFF | (12, 1080, 2160) | EPSG:4326 |

## Detección
- **Structure mode:** A (single multi-band stack)
- **Temporal frequency:** monthly (tier: CF metadata)
- **Variable profile:** temperature
- **Confidence (overall):** 0.97

## Validación pre-procesamiento
| Check | Estado | Mensaje |
|-------|--------|---------|
| CRS consistency | PASS | Single CRS detected: EPSG:4326 |
| Grid alignment | PASS | All bands share grid |
| Method/variable compatibility | PASS | pchip_mp compatible with temperature |

## Parámetros de interpolación
- **Method:** pchip_mp
- **Options:** convergence_tol=1e-6, max_iterations=50
- **Chunk size:** 512
- **Scheduler:** threaded

## Estadísticas pre/post
| Banda | min | max | mean | std | nan% |
|-------|-----|-----|------|-----|------|
| Jan (in) | -42.1 | 38.2 | 12.4 | 18.6 | 2.1 |
| Jan (out, daily agg) | -42.0 | 38.3 | 12.4 | 18.7 | 2.1 |

## Validación post-procesamiento
| Check | Estado | Mensaje |
|-------|--------|---------|
| Monthly mean conservation | PASS | max abs error 3.2e-7 |
| Cyclic continuity | PASS | day 365 ≈ day 1 within tol |
| Physical range | PASS | values within [-90, 60] degC |

## Outputs
| Path | MD5 | Size | Format |
|------|-----|------|--------|
| tavg_daily.nc | 9b1e...77 | 412.0 MB | NetCDF4 |

## Procedencia
```yaml
tempify_version: "0.1.0"
timestamp_utc: "2026-05-16T14:32:11Z"
platform: "Windows-10.0.22631-x86_64"
python_version: "3.11.8"
reproducibility_mode: "parallel"
dask_scheduler: "threaded"
config:
  method: "pchip_mp"
  method_options:
    convergence_tol: 1.0e-6
    max_iterations: 50
  chunk_size: 512
  variable_profile: "temperature"
  force_method_used: false
inputs:
  - path: "wc2.1_10m_tavg.tif"
    md5: "4f3a...c1"
    bytes: 19293184
outputs:
  - path: "tavg_daily.nc"
    md5: "9b1e...77"
    bytes: 432013312
detection_confidence:
  structure_mode: 1.0
  temporal_frequency: 1.0
  temporal_frequency_tier: 1.0
  variable_profile: 0.9
  homogeneity: 1.0
  overall: 0.97
warnings: []
errors: []
```
```

## Estabilidad del schema

- El schema sigue **SemVer**. Cambios breaking (renombrar/eliminar campos, cambiar tipos, alterar el orden de las secciones top-level) requieren bump **MAJOR** del paquete `tempify`.
- Cambios aditivos (nuevos campos opcionales, nuevas subsecciones) son **MINOR**.
- Correcciones de redacción o ejemplos son **PATCH**.
- Consumidores (visor GUI, scripts de terceros, parsers automatizados) deben aceptar campos extra y silenciar los desconocidos. Equivalente JSON-Schema: `additionalProperties: true` en el YAML embebido.
- El visor GUI debe degradar gracefully ante secciones faltantes (reportes generados por versiones anteriores).

## Referencias

- ADR-0007 — Reproducibility policy (modos `strict` y `parallel`, hashes MD5).
- ADR-0008 — Confidence scoring and detection result contract.
- `specs/pipeline/requirements.md` REQ-007 — generación de reporte.
- `specs/cli/requirements.md` REQ-005 — flag `--report`.
- `specs/gui/requirements.md` — visor del reporte.
- CF Conventions — http://cfconventions.org/
- Semantic Versioning — https://semver.org/
