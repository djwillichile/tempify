# Tech Stack

## Lenguaje base

- **Python 3.11+** (typing moderno con `|`, `Self`, structural matching)
- **Tipado obligatorio** en toda función pública (verificado con `mypy --strict`)

## Dependencias core (runtime)

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

## Dependencias dev

| Dependencia | Propósito |
|---|---|
| `pytest >= 8.0` | Test runner |
| `pytest-cov` | Coverage |
| `hypothesis` | Property-based testing |
| `mypy` | Type checking strict |
| `ruff` | Lint + format |
| `sphinx + sphinx-rtd-theme` | Docs |
| `jupyter` | Tutoriales |

## Restricciones

- No agregar dependencias pesadas sin **ADR** en `docs/adr/`.
- Evitar GDAL directo: rioxarray + rasterio ya la encapsulan.
- No usar `pandas` salvo donde sea estrictamente necesario. Preferir xarray.
- No usar `geopandas` en core. Operaciones vectoriales en módulos opcionales.

## Empaquetado

- `pyproject.toml` con PEP 621 (sin `setup.py`)
- Build backend: `hatchling`
- Distribución: PyPI + conda-forge
- Versionado: SemVer estricto

## `pyproject.toml` mínimo

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

## CI/CD

- GitHub Actions
- Matriz: Python 3.11/3.12/3.13 × Linux/macOS/Windows
- Jobs: lint → typecheck → test → build → docs

## Compatibilidad mínima

- Python: 3.11+
- OS: Ubuntu 22.04+, macOS 13+, Windows 10/11
- GDAL (via rasterio wheel): 3.6+
