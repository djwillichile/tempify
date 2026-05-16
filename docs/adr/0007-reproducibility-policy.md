# ADR-0007: Política de reproducibilidad (dos modos)

**Estado:** Accepted
**Fecha:** 2026-05-16
**Deciders:** Guillermo Fuentes-Jaque
**Contexto técnico:** NFR-003 de `core-interpolation`, REQ-010 y NFR-002 de `pipeline`, guardrail nº 6 de `CLAUDE.md`.

## Contexto

El proyecto tempify declara como invariante "reproducibilidad bit-exact: mismos inputs y mismos parámetros producen mismo output, verificable con MD5". Este compromiso entra en tensión con tres realidades del cómputo numérico paralelo y heterogéneo:

1. **Orden de reducción en Dask.** Operaciones de reducción flotante (`sum`, `mean`, agregaciones intermedias del grafo) no son asociativas en IEEE 754. Con el scheduler `threaded` o `distributed`, el orden de combinación de chunks depende del tamaño de chunk, del número de workers y del orden de finalización de tareas. Dos ejecuciones de la misma operación pueden diferir en el último bit (típicamente ULP ≤ 1).

2. **Backend BLAS/LAPACK.** La interpolación Fourier por mínimos cuadrados (`scipy.linalg.lstsq`) y la FFT (`scipy.fft`) delegan en BLAS. Las wheels oficiales de NumPy/SciPy usan OpenBLAS; entornos conda-forge pueden enlazar MKL. Implementaciones distintas (orden de bloqueo, AVX-512 vs AVX2, denormals) producen resultados que difieren en bits poco significativos.

3. **Plataforma.** Windows con MSVC + libm de UCRT y Linux con glibc + libm de GCC no garantizan idéntico redondeo en funciones trascendentes (`exp`, `sin`, `cos`). El proyecto soporta ambas plataformas (ver `steering/tech.md`).

Una política "bit-exact universal" exigiría fijar plataforma, BLAS, scheduler single-thread y desactivar todo paralelismo. Eso destruye el objetivo de rendimiento de NFR-001 (Chile a 2.5 arc-min en menos de 60 s). Una política "solo `allclose`" elimina la capacidad de detectar regresiones numéricas finas en CI, donde una diferencia bit-a-bit revela un cambio de implementación no intencional. Hace falta una política con dos niveles.

## Decisión

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

## Alternativas consideradas

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

## Consecuencias

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

## Notas de implementación

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

## Referencias

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
