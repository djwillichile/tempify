# Design — core-interpolation

**Estado:** Draft
**Requirements doc:** [requirements.md](requirements.md) (Approved, REQ-001..014, NFR-001..005)
**Última actualización:** 2026-05-15

## 1. Visión técnica

La feature `core-interpolation` materializa la Capa 4 (Interpolation) del proyecto (per `steering/architecture.md`). Es **interpolación temporal pura, sin I/O ni conocimiento de georreferencia**: recibe un `xr.DataArray` con coord `month ∈ [1,12]` y devuelve un `xr.DataArray` con coord `time` diaria (365 o 366 valores). La paralelización es ortogonal: todos los métodos vectorizan vía `xr.apply_ufunc(..., dask='parallelized')` sobre el kernel 1D del píxel (per ADR-0001, ADR-0002).

Se exponen cuatro métodos detrás de un único contrato `BaseInterpolator.interpolate(...)`: Lineal (referencia), PCHIP (Fritsch-Carlson, suave + monótono local), PCHIP+Rymes-Myers (PCHIP con corrección iterativa mean-preserving) y Fourier (multi-armónico, 1..5). La política de precipitación (ADR-0004) NO se aplica aquí: estos algoritmos son agnósticos a la variable. El rechazo vive en Capa 3 (`MethodVariableCompatibilityChecker`). La política de reproducibilidad (ADR-0007) tampoco se aplica aquí: el módulo es estatic-puro respecto al scheduler de Dask; el `reproducibility_context` lo aplica Capa 5.

## 2. Arquitectura propuesta

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

## 3. Contratos públicos (APIs)

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

## 4. Modelos de datos

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
# ADR-0010 Level 2 (validation tolerance) lives in PostInterpolationValidator
```

## 5. Algoritmos clave

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

# 1. Initial guess via PCHIP cyclic
y = pchip_cyclic(m, target_doys)

# 2. Iterative Rymes-Myers correction
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

# 3. NaN handling per REQ-008
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

# 1. Compute DFT of monthly series (length 12)
M = np.fft.rfft(m)        # length 7 (real input)

# 2. Truncate beyond K-th harmonic
M_trunc = zeros_like(M)
M_trunc[:K+1] = M[:K+1]

# 3. Build continuous reconstruction at target DOYs
phi[t] = 2 * pi * (DOY(t) - DOY_anchor) / N        # phase 0..2pi over year
y[t] = M_trunc[0].real / 12
       + sum_{k=1..K} (2/12) * (M_trunc[k].real * cos(k*phi[t])
                                - M_trunc[k].imag * sin(k*phi[t]))
```

Validación: `FOURIER_MIN_HARMONICS <= n_harmonics <= FOURIER_MAX_HARMONICS` (1..5). Harmonic 6 (Nyquist para 12 muestras) representa el modo doblado no observable y queda explícitamente prohibido. Construcción inválida → `ValueError` en `__init__`.

**Boundary:** la propia construcción es periódica; `cyclic=False` no aplica ningún tratamiento especial (REQ-005c).
**Complejidad:** `O(N)` por píxel (FFT de 12 elementos es `O(1)`).
**Trade-offs:** suavidad infinita C∞; no preserva monotonicidad; no preserva la media mensual exacta (sesgo pequeño dependiente de truncamiento); ideal para variables con ciclo anual dominante (temperatura, radiación).

## 6. Decisiones de diseño

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

## 7. Estrategia de testing

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

## 8. Plan de migración

N/A. Esta spec es la primera implementación de Capa 4. No hay código previo que migrar.

## 9. Métricas de calidad

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

## 10. Trazabilidad requirements → design → tests

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

## 11. Referencias

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
