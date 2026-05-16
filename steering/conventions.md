# Conventions

## Estilo de código

### Formato

- **Formatter:** `ruff format` (sin black/isort separados)
- **Línea máxima:** 100 caracteres
- **Indentación:** 4 espacios

### Naming

```python
# Módulos: snake_case
tempify/temporal_frequency_resolver.py

# Clases: PascalCase
class PchipMeanPreservingInterpolator: ...

# Funciones y variables: snake_case
def interpolate_monthly_to_daily(monthly_stack, ...): ...

# Constantes: UPPER_SNAKE_CASE
DEFAULT_CHUNK_SIZE = 512

# Privados: prefijo _
def _compute_pchip_slopes(...): ...
```

### Type hints

Obligatorios en función pública. Verificados con `mypy --strict`.

```python
from pathlib import Path
import xarray as xr

def interpolate(
    source: xr.DataArray,
    target_freq: TemporalFrequency,
    method: str = "pchip_mp",
    *,
    chunk_size: int = 512,
) -> xr.DataArray: ...
```

### Docstrings

Estilo **NumPy**, obligatorio:

```python
def interpolate_pchip_mean_preserving(
    monthly: xr.DataArray,
    target_doys: np.ndarray,
    n_iter: int = 50,
) -> xr.DataArray:
    """Interpolate monthly data to daily preserving the monthly mean.

    Applies PCHIP interpolation followed by iterative Rymes-Myers
    correction to ensure daily values average per month to exactly
    match original monthly values.

    Parameters
    ----------
    monthly : xr.DataArray
        Monthly stack with dims (month, y, x). Month coord 1..12.
    target_doys : np.ndarray
        1D array of target days of year, length 365 or 366.
    n_iter : int, default 50
        Number of Rymes-Myers correction iterations.

    Returns
    -------
    xr.DataArray
        Daily stack with dims (time, y, x).

    References
    ----------
    Rymes, M. D., & Myers, D. R. (2001). Mean preserving algorithm
    for smoothly interpolating averaged data. Solar Energy, 71(4),
    225-231.
    """
```

## Testing

### Organización

```
tests/
├── unit/              # Tests aislados por módulo
├── integration/       # Flujos end-to-end
└── fixtures/          # Datos de test (pequeños)
```

### Reglas

1. **Cobertura mínima por módulo: 85%** (verificado en CI).
2. **TDD para features nuevas:** test primero, código mínimo, refactor.
3. **Property-based testing con hypothesis** para invariantes críticos:
   - Conservación de media mensual en PCHIP+RM
   - Continuidad cíclica en métodos cíclicos
   - Idempotencia donde aplique
4. **Fixtures pequeñas**. Volúmenes grandes generados sintéticamente.
5. **No tests dependientes de red.** Mocks o fixtures locales.

### Ejemplo con hypothesis

```python
from hypothesis import given, strategies as st
import numpy as np

@given(
    monthly=st.lists(
        st.floats(min_value=-50, max_value=50, allow_nan=False),
        min_size=12, max_size=12
    )
)
def test_rymes_myers_preserves_monthly_mean(monthly):
    """For any valid monthly series, daily reconstruction averages
    back to original monthly values within tolerance."""
    monthly_arr = np.array(monthly)
    daily = interpolate_pchip_mean_preserving(monthly_arr, ...)
    reconstructed = aggregate_to_monthly(daily)
    np.testing.assert_allclose(reconstructed, monthly_arr, atol=1e-6)
```

## Git workflow

### Branches

- `main` — siempre desplegable, protegida
- `feature/<spec-name>-<short-desc>` — una rama por spec
- `fix/<issue-id>-<short-desc>`
- `docs/<topic>`

### Commits

**Conventional Commits** estricto:

```
<type>(<scope>): <subject>

[body opcional]

[footer: refs spec, issue, ADR]
```

Tipos válidos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `build`, `ci`.

Ejemplos:

```
feat(interpolation): add Fourier interpolator with N harmonics

Implements FourierInterpolator class accepting 1-5 harmonics.
Mean-preserving option via post Rymes-Myers correction.

Refs: specs/core-interpolation/tasks.md#task-4
```

```
fix(io): correct CRS preservation in MultiFileCollectionReader

Previously the CRS attribute was being dropped on concat.

Closes #42
```

### Pull requests

- Toda PR debe linkar a la spec correspondiente.
- Checklist obligatorio:
  - [ ] Spec actualizada si cambia el contrato
  - [ ] Tests añadidos/actualizados
  - [ ] Coverage no disminuye
  - [ ] Docstrings completos
  - [ ] CHANGELOG actualizado
  - [ ] mypy strict pasa
  - [ ] ruff pasa

## Versioning y release

- **SemVer estricto:** MAJOR.MINOR.PATCH
- Pre-1.0: cambios breaking permitidos en MINOR
- 1.0+: cambios breaking solo en MAJOR
- Releases via tag `vX.Y.Z` dispara publicación

## Documentación

- **README.md:** instalación + ejemplo mínimo (1 página).
- **docs/tutorials/:** notebooks ejecutables, uno por caso de uso.
- **docs/methodology/:** notas técnicas por método, con referencias.
- **docs/adr/:** Architecture Decision Records (MADR).
- **API reference:** Sphinx autodoc desde docstrings.

## Idioma

- Código + comentarios técnicos: **inglés**.
- Tutoriales y user docs: **español primario**, inglés secundario.
- Mensajes CLI: español por defecto, inglés vía env var.

## Performance

- Benchmarks regulares en `tests/benchmark/` (no en CI por costo).
- Profiling con `py-spy` antes de optimizar.
- **Regla:** no optimizar sin medir.
