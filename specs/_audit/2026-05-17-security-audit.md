# Auditoría de Seguridad — tempify v0.1.2 (2026-05-17)

## Resumen ejecutivo

El repositorio está en muy buen estado de seguridad para una librería Python pura de procesamiento local. **No se detectaron secretos expuestos, credenciales, ni patrones de ejecución arbitraria de código en `src/`.** Los hallazgos son principalmente higiénicos: ausencia de gobernanza estándar (`SECURITY.md`, `CODE_OF_CONDUCT.md`, workflows CI), drift de versión en `pyproject.toml`, fuga menor del username del autor en outputs de notebook, y dependencias con pin de tipo `>=` sin upper bound (típico en libs Python).

## Hallazgos por severidad

- CRITICAL: **0**
- HIGH: **0**
- MED: **3** (H-001, H-002, H-003)
- LOW: **6** (H-004 a H-009)

## Detalle de hallazgos

### [MED] H-001 — Drift de versión: pyproject.toml dice 0.1.0, el tag es v0.1.2

- **Archivo:** `pyproject.toml:7`
- **Estado:** ✅ **CORREGIDO** en este branch (`code/worldclim-notebook-and-landing`). Ahora `pyproject.toml` y `__version__` ambos declaran `0.1.2`.
- **Riesgo:** Usuarios que hagan `pip show tempify` recibían metadata incorrecta. Reportes con MD5 registraban una versión inconsistente con Zenodo.
- **Recomendación aplicada:** bump `version = "0.1.2"` + verificación automática en CI propuesta como REQ-SEC-005.

### [MED] H-002 — Sin política de divulgación de vulnerabilidades (`SECURITY.md`)

- **Archivo:** raíz del repo (ausencia)
- **Estado:** ✅ **CORREGIDO** — `SECURITY.md` creado en este branch con canal de reporte, SLAs y versiones soportadas.

### [MED] H-003 — Sin CI/CD ni workflows de GitHub Actions

- **Archivo:** ausencia de `.github/workflows/`
- **Estado:** ⏳ **PENDIENTE para v0.1.3.** Se requiere workflow básico (`pytest + ruff + mypy + gitleaks`), Dependabot, CodeQL. Tracked en REQ-SEC-008.

### [LOW] H-004 — Username del desarrollador filtrado en notebook tutorial

- **Archivo:** `docs/tutorials/01-getting-started.ipynb` (2 occurrences en outputs cacheados)
- **Estado:** ✅ **CORREGIDO** — sanitizado en este branch (`C:\Users\Guillermo\AppData\...` → `C:\Users\runner\AppData\...`).

### [LOW] H-005 — `.coverage` (sqlite con paths absolutos) presente en working tree

- **Archivo:** `D:\proyectos IA\tempify\.coverage`
- **Estado:** ✅ **CORREGIDO** — borrado localmente; ya estaba en `.gitignore`.

### [LOW] H-006 — Dependencias con pin de límite inferior sin upper bound

- **Archivo:** `pyproject.toml:31-41`
- **Estado:** ⏳ **ACEPTADO COMO STATUS QUO.** Práctica estándar para libs Python. Mitigación documentada en REQ-SEC-004 (Dependabot weekly).

### [LOW] H-007 — Helpers internos `_*.py` en `docs/tutorials/`

- **Archivo:** `docs/tutorials/_build_notebook_02.py`, `_export_landing_pngs.py`
- **Estado:** ✅ **CORREGIDO** — borrados en este branch (nunca fueron committeados a main).

### [LOW] H-008 — Sin `CODE_OF_CONDUCT.md` ni `CONTRIBUTING.md`

- **Archivo:** raíz del repo (ausencia)
- **Estado:** ⏳ **PENDIENTE para v0.1.3.** Tracked en REQ-SEC-007.

### [LOW] H-009 — `pickle` / `eval` / `yaml.load` inseguro en `src/`

- **Estado:** ✅ **VERIFICACIÓN NEGATIVA.** Grep extensivo sobre `src/tempify/` no encontró ningún uso. El único `yaml.safe_load` en `validation/profiles.py:60` es correcto. Tracked en REQ-SEC-003.

## Áreas verificadas sin hallazgos

- **Secretos/credenciales:** sin matches para AWS keys, GitHub/PyPI tokens, JWT, claves privadas, passwords hardcodeados.
- **Archivos `.env`, `.pem`, `.key`:** ninguno.
- **Patrones unsafe:** `src/` limpio.
- **Historial git (100 commits):** sin commits sospechosos; un único autor (`guillermo.f1990@gmail.com` / `32119499+djwillichile@noreply.github.com`).
- **Binarios trackeados:** solo `wc1_6_maipo_alto_tavg_stack.tif` (220 KB, dataset declarado y legítimo).
- **`.gitignore`:** cubre `.venv/`, `__pycache__/`, `.coverage`, `.DS_Store`, IDE caches, `*.tif`/`*.nc` (con excepciones explícitas).
- **CLI path traversal:** `tempify/cli/app.py` recibe `pathlib.Path` vía Typer; sin concatenación insegura ni `os.system`.

## Recomendaciones generales (mejoras, no hallazgos)

- **`pre-commit` con `gitleaks` + `nbstripout`:** complementa los hooks ya documentados en `CLAUDE.md`.
- **`pip-audit` en CI semanal:** una vez añadidos los workflows.
- **Branch protection en `main`:** formalizar el guardrail #8 ("no tocar main directamente") con regla de GitHub que exija PR + CI verde.
- **PEP 740 attestations:** cuando se publique a PyPI, firmar los artefactos con sigstore.

## Acciones cerradas en este branch (`code/worldclim-notebook-and-landing`)

| ID | Acción | Archivo |
|---|---|---|
| H-001 | Bump `pyproject.toml` version 0.1.0 → 0.1.2 | `pyproject.toml` |
| H-002 | Crear `SECURITY.md` | `SECURITY.md` |
| H-004 | Sanitizar username en notebook 01 | `docs/tutorials/01-getting-started.ipynb` |
| H-005 | Borrar `.coverage` local | (working tree only) |
| H-007 | Borrar helpers temporales | (working tree only) |

## Acciones pendientes para v0.1.3

- H-003: agregar workflows CI + Dependabot + CodeQL
- H-008: agregar `CODE_OF_CONDUCT.md` y `CONTRIBUTING.md`
- Suite de tests `tests/security/` para REQ-SEC-002, -005, -006

## Trazabilidad

Auditoría delegada a agente `general-purpose` el 2026-05-17. Spec asociada: `specs/security/requirements.md`. Política operacional: `SECURITY.md`.
