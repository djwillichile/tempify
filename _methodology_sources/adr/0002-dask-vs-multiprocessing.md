# ADR-0002: Dask vs multiprocessing nativo

**Estado:** Accepted
**Fecha:** 2026-05-16
**Deciders:** Guillermo Fuentes-Jaque
**Contexto técnico:** Capa 4 (Interpolation) y restricciones NFR-001/NFR-004 de la spec `core-interpolation`.

## Contexto

La densificación temporal de tempify aplica una función 1D (interpolación mensual → diaria) píxel a píxel sobre stacks ráster `(time, y, x)` cuyo tamaño puede superar la RAM disponible. El caso de referencia (NFR-001) es Chile a 2.5 arc-min, stack `12 × 3000 × 500 = 18M píxeles temporales`, con presupuesto de <60 s en 8 cores y <1 GB de RAM por chunk (NFR-004).

El problema combina tres requisitos simultáneos:

1. **Vectorización píxel a píxel** de una operación compute-bound (PCHIP, mínimos cuadrados Fourier, iteración Rymes-Myers).
2. **Out-of-core** para stacks que no caben en RAM (Chile completo a 30 arc-sec supera los 8 GB).
3. **Integración con `xr.DataArray`** sin romper el contrato de la Capa 4, que ya impone `xr.apply_ufunc(..., dask="parallelized")` (ver `steering/architecture.md` § Capa 4).

El ADR-0001 ya fijó `xarray.DataArray` como abstracción central. Falta decidir el mecanismo concreto de paralelismo subyacente.

## Decisión

Usar **Dask** como mecanismo de paralelismo, exclusivamente vía `xr.apply_ufunc(..., dask="parallelized")`. No se introducirá `multiprocessing`, `concurrent.futures.ProcessPoolExecutor`, `joblib` ni paralelismo manual basado en threads.

## Alternativas consideradas

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

## Consecuencias

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

## Notas de implementación

- **Scheduler por defecto:** `threaded`. Apropiado para las operaciones compute-bound de la Capa 4, donde los kernels NumPy/SciPy liberan el GIL.
- **Tamaño de chunk por defecto:** `512` en las dimensiones espaciales (`x`, `y`); `time` no se chunkea (`-1`) porque la interpolación es un reduce a lo largo de esa dimensión. Configurable vía `PipelineConfig.chunk_size`.
- **Modo single-thread reproducible:** `scheduler='synchronous'` disponible explícitamente para tests bit-exact y para depuración (ver ADR-0007).
- **Contrato de Capa 4:** todos los interpoladores invocan `xr.apply_ufunc` con `dask="parallelized"`, `vectorize=False`, `output_dtypes=[source.dtype]` y `input_core_dims=[["month"]]`, `output_core_dims=[["time"]]`. Esto es invariante arquitectónico, no decisión por interpolador.
- **Sin imports de `multiprocessing`, `concurrent.futures` ni `joblib` en el código del paquete.** El linter prohíbe esos módulos en `src/tempify/` salvo excepción justificada por ADR posterior.

## Referencias

- Dask documentation: https://docs.dask.org/
- `xarray.apply_ufunc`: https://docs.xarray.dev/en/stable/generated/xarray.apply_ufunc.html
- Pangeo project: https://pangeo.io/
- ADR-0001: Use xarray.DataArray as central data abstraction
- `steering/architecture.md` § Capa 4 Interpolation
- `specs/core-interpolation/requirements.md` NFR-001, NFR-003, NFR-004
