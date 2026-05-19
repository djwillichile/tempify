# Requirements — documentation

**Estado:** Draft
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-19
**Última actualización:** 2026-05-19

## 1. Propósito

Publicar un sitio de documentación auto-generado en `tempify.readthedocs.io` que consolide la referencia API, los tutoriales ejecutables (notebooks), las decisiones arquitectónicas (ADRs), los schemas de datos y la metodología científica del proyecto. La URL ya está anunciada en `pyproject.toml` pero hoy no resuelve, lo que constituye una promesa incumplida hacia usuarios y citadores académicos.

## 2. Alcance

### In-scope

- Configuración Sphinx (`docs/conf.py`, `docs/index.md`, `docs/_static/`, `docs/Makefile`, `.readthedocs.yaml`).
- Referencia API auto-generada con `sphinx.ext.autodoc` + `sphinx.ext.napoleon` (estilo NumPy, ya canónico en el código).
- Integración de los 2 notebooks de `docs/tutorials/` vía `myst-nb` con ejecución cacheada.
- Renderizado de `docs/adr/*.md`, `docs/methodology/*.md` y `docs/schemas/*.md` vía `myst-parser`, navegables como secciones de primer nivel.
- Citas científicas con `sphinxcontrib-bibtex` apuntando a `REFERENCES.bib` (raíz del repo).
- Doctests ejecutables en CI: `pytest --doctest-modules src/tempify` + `sphinx-build -b doctest`.
- Linter de docstrings: `ruff` rules `D` con `convention = "numpy"`, integrado en `pyproject.toml` y CI.
- Workflow `.github/workflows/docs.yml`: build sin warnings en cada PR, deploy a Read the Docs en push a `main` vía webhook.
- `CONTRIBUTING.md` con sección "Documentation": cómo construir localmente, escribir docstrings, agregar tutoriales.
- Auditoría de cobertura de docstrings en API pública (reporte en `impl-log.md`, no migración masiva si ya cumplen NumPy).

### Out-of-scope

- Traducción i18n del sitio (`sphinx-intl`). Diferido.
- Reemplazo del `index.html` estático actual en `docs/` hasta primer deploy exitoso en RTD.
- Diagramas Mermaid/PlantUML interactivos. Diferido a fase 2 si emerge necesidad.
- Documentación de internals privados (`_kernels.py`, módulos prefijados con `_`).
- Versionado multi-rama con `sphinx-multiversion`. Solo `latest` y `stable` (defaults de RTD).
- Migración del CLI/GUI a inglés (permanecen en español per sus specs respectivas).

## 3. Actores y casos de uso

### Actor 1: Usuario nuevo evaluando la librería

> Como investigador climático que descubre tempify en PyPI, quiero leer una guía de inicio rápido y ver ejemplos ejecutados con datos reales para decidir en 10 minutos si la librería resuelve mi caso.

**Caso de uso típico:** Llega desde el README a `tempify.readthedocs.io/en/latest/`, navega a "Tutorials", abre `01-getting-started` renderizado con outputs y figuras, decide instalar.

### Actor 2: Usuario que necesita la firma exacta de una función

> Como usuario intermedio que ya instaló la librería, quiero encontrar la documentación de `tempify.interpolation.pchip_rm.PCHIPRMInterpolator` con sus parámetros, tipos, ejemplos y enlaces a los ADRs que justifican su comportamiento.

**Caso de uso típico:** Busca "PCHIP" en el sitio, llega a la página de referencia API, ve la firma con type hints, lee el ejemplo, sigue el enlace cruzado a ADR-0010 (conservación de media).

### Actor 3: Contribuidor externo

> Como contribuidor que quiere proponer un PR, quiero que `CONTRIBUTING.md` me indique exactamente cómo construir las docs y cómo escribir docstrings que pasen el linter.

**Caso de uso típico:** Lee `CONTRIBUTING.md`, ejecuta `sphinx-build -W -b html docs docs/_build/html` localmente, verifica que su nueva función pase `ruff check --select D`, abre PR.

### Actor 4: Citador académico

> Como autor de un paper que cita tempify, quiero ver una referencia bibliográfica estable, la metodología documentada y el DOI Zenodo.

**Caso de uso típico:** Visita el sitio, encuentra "Methodology" > precipitación, ve citas BibTeX renderizadas, copia la referencia oficial.

## 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL build a Sphinx-based HTML documentation site from sources in `docs/` using the `[docs]` optional dependencies declared in `pyproject.toml`.

### REQ-002 (Ubiquitous)

THE SYSTEM SHALL auto-generate API reference pages for every public symbol of the `tempify` package using `sphinx.ext.autodoc` + `sphinx.ext.napoleon` with `napoleon_numpy_docstring = True`.

### REQ-003 (Event-driven)

WHEN building docs, THE SYSTEM SHALL render `docs/tutorials/*.ipynb` notebooks via `myst-nb` with execution caching enabled (`nb_execution_mode = "cache"`).

### REQ-004 (Ubiquitous)

THE SYSTEM SHALL include the contents of `docs/adr/`, `docs/methodology/` and `docs/schemas/` as first-level navigable sections in the site's table of contents, rendered via `myst-parser`.

### REQ-005 (Optional)

WHERE a docstring or Markdown page uses `{cite}` or `{footcite}` roles, THE SYSTEM SHALL resolve them against `REFERENCES.bib` (repository root) via `sphinxcontrib-bibtex`.

### REQ-006 (Event-driven)

WHEN CI runs on a pull request, THE SYSTEM SHALL execute `pytest --doctest-modules src/tempify` and `sphinx-build -b doctest docs docs/_build/doctest`, failing the PR if any doctest fails.

### REQ-007 (Event-driven)

WHEN CI runs on a pull request, THE SYSTEM SHALL execute `ruff check src/tempify --select D` with `convention = "numpy"` configured in `pyproject.toml`, failing the PR if any docstring lint rule is violated.

### REQ-008 (Event-driven)

WHEN a pull request is opened or updated, THE SYSTEM SHALL run `sphinx-build -W -b html docs docs/_build/html` in `.github/workflows/docs.yml` and publish the resulting HTML as a CI artifact, failing the PR if any Sphinx warning occurs.

### REQ-009 (Event-driven)

WHEN a commit is pushed to `main`, THE SYSTEM SHALL trigger a Read the Docs build via webhook such that `https://tempify.readthedocs.io/en/latest/` reflects the new content within 5 minutes.

### REQ-010 (Ubiquitous)

THE SYSTEM SHALL provide a `CONTRIBUTING.md` file at the repository root with a "Documentation" section explaining: (a) local build command, (b) docstring convention (NumPy) with a canonical example, (c) how to add a new tutorial, (d) how to add an ADR.

### REQ-011 (Ubiquitous, autodoc isolation)

THE SYSTEM SHALL configure `autodoc_mock_imports = ["PySide6"]` in `docs/conf.py` so the API build does not require a graphical environment, and SHALL exclude `tempify.gui` from API reference generation if its import surface is not stable in CI.

### REQ-012 (State-driven)

WHILE building docs, THE SYSTEM SHALL fail the build if any cross-reference (`:class:`, `:func:`, `:mod:`, `:ref:`) cannot be resolved (`nitpicky = True`), with an explicit allow-list for third-party references in `nitpick_ignore`.

### REQ-013 (Ubiquitous, language policy)

THE SYSTEM SHALL render all documentation pages in English. The README and CLI/GUI user-facing strings remain in Spanish per their own specs.

### REQ-014 (Ubiquitous, attribution policy)

THE SYSTEM SHALL NOT include in any committed artifact (commits, code comments, docstrings, generated HTML, workflow files, CONTRIBUTING.md, CHANGELOG.md) any reference to AI assistants, code generators, or external authoring tools. Author and contributor attribution shall list only the project owner and accepted human contributors.

### REQ-015 (Optional)

WHERE a docstring example uses non-deterministic input (current time, random without seed, network), THE SYSTEM SHALL mark the doctest block with `# doctest: +SKIP` or refactor to use fixed seeds, preserving bit-exact reproducibility per CLAUDE.md guardrail #6.

## 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Reliability | Build determinista | `sphinx-build -W` pasa en 3 corridas consecutivas sin diffs significativos en HTML generado (excluyendo timestamps) |
| NFR-002 | Performance | Build completo < 5 min en CI estándar (ubuntu-latest, 2 cores) | Job `docs.yml` reporta duración; alerta si supera 5 min |
| NFR-003 | Maintainability | Cero ADRs nuevos requeridos por esta spec | Verificado en review de `design.md` |
| NFR-004 | Coverage | 100% de símbolos públicos del paquete `tempify` aparecen en la referencia API | Script de auditoría compara `dir(tempify)` filtrado contra páginas generadas |
| NFR-005 | Accessibility | HTML generado pasa validación WCAG AA básica (contraste, alt-text en figuras) | Linter `pa11y` en CI sobre 3 páginas representativas (opcional fase 2) |
| NFR-006 | Reproducibility | Notebooks renderizados son bit-exact entre builds | Hash SHA-256 de outputs de celdas estable entre 2 corridas con cache invalidado |

## 6. Criterios de aceptación

Trazabilidad REQ → test/verificación (cada REQ tiene al menos un check):

- [ ] REQ-001 → `sphinx-build -W -b html docs docs/_build/html` exit 0
- [ ] REQ-002 → Test `test_api_reference_includes_public_symbols` enumera símbolos públicos y verifica presencia en HTML generado
- [ ] REQ-003 → `docs/_build/html/tutorials/01-getting-started.html` contiene outputs renderizados
- [ ] REQ-004 → `docs/_build/html/adr/0001-xarray-as-core-data-model.html` existe y es accesible desde toctree
- [ ] REQ-005 → Test `test_bibtex_citation_resolves` valida al menos una cita en `methodology/precipitation.md`
- [ ] REQ-006 → Job `doctests` en `docs.yml` corre y falla la PR si rompe
- [ ] REQ-007 → Job `ruff-D` en `docs.yml` corre y falla la PR si rompe
- [ ] REQ-008 → Job `sphinx-build` en `docs.yml` con flag `-W` corre en cada PR
- [ ] REQ-009 → `.readthedocs.yaml` válido; primer push a `main` resuelve URL pública
- [ ] REQ-010 → `CONTRIBUTING.md` existe con sección "Documentation" y los 4 sub-puntos requeridos
- [ ] REQ-011 → `docs/conf.py` declara `autodoc_mock_imports = ["PySide6"]`
- [ ] REQ-012 → `docs/conf.py` declara `nitpicky = True` y `nitpick_ignore` con justificación inline
- [ ] REQ-013 → Test `test_html_lang_attribute_is_en` parsea `<html lang="en">` en páginas generadas
- [ ] REQ-014 → Script `tools/check-attribution.sh` grep -ri sobre `claude\|copilot\|gpt\|chatgpt\|anthropic\|openai` en `.github/`, `docs/`, `CONTRIBUTING.md`, `CHANGELOG.md` y `git log` retorna cero matches
- [ ] REQ-015 → `pytest --doctest-modules` sin SKIPs no documentados (cada SKIP justificado en comentario)
- [ ] NFR-001 → 3 corridas de `sphinx-build` con diff vacío (modulo timestamps)
- [ ] NFR-002 → CI reporta `<300s` en job de docs
- [ ] NFR-004 → Reporte de auditoría de cobertura adjunto a `impl-log.md`
- [ ] CHANGELOG actualizado con sección `[Unreleased]` describiendo el nuevo sitio

## 7. Dependencias y supuestos

### Specs relacionadas

- Depende de: ninguna funcional (la documentación es transversal).
- Afecta a: [`cli`](../cli/requirements.md), [`gui`](../gui/requirements.md), [`core-interpolation`](../core-interpolation/requirements.md), [`pipeline`](../pipeline/requirements.md), [`io-handlers`](../io-handlers/requirements.md), [`validation`](../validation/requirements.md) — todas ven sus docstrings publicadas y sometidas a `ruff D`.
- Coordina con: [`security`](../security/requirements.md) (la sección "Security" en CONTRIBUTING.md debe enlazar `SECURITY.md`).

### ADRs referenciados

- Ninguno nuevo. Esta spec se apoya en ADRs existentes (0001-0018) para enlazado.
- Si en `design.md` se decide mkdocs en lugar de Sphinx, se abrirá ADR-0019 (no esperado).

### Supuestos

- El usuario configurará el webhook RTD ↔ GitHub manualmente la primera vez (acción fuera del repo).
- `REFERENCES.bib` existirá en la raíz del repo o será creado como parte de T06 (vacío inicialmente, poblado conforme metodología cite fuentes).
- Los notebooks en `docs/tutorials/` no requieren credenciales ni datos externos pesados (los datos WorldClim usados en `02-real-worldclim-maipo.ipynb` están commiteados o son sintéticos via `tempify.datasets`).
- El usuario es el único autor visible en el repositorio; todos los commits resultantes se firman con `Guillermo Fuentes-Jaque <guillermo@icta.cl>`.

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| `autodoc` no logra importar `tempify.gui` por Qt en CI sin display | Alta | Medio | `autodoc_mock_imports = ["PySide6"]` (REQ-011) + exclusión condicional del módulo |
| Notebooks con datos pesados ralentizan el build CI más allá de NFR-002 | Media | Medio | Cachear ejecución (`nb_execution_mode = "cache"`); o commitear outputs y marcar `nb_execution_mode = "off"` para tutoriales pesados |
| Typer auto-genera ayuda CLI que duplica `autodoc` | Media | Bajo | Excluir `tempify.cli.app` del autodoc o usar `sphinx-click` específico |
| Doctests no determinísticos rompen reproducibilidad bit-exact (guardrail #6) | Media | Alto | REQ-015 + revisión manual de cada bloque `>>>` durante T08 |
| Webhook RTD no se dispara y la URL anunciada sigue sin entregar | Media | Alto | Verificación manual post-T09 con push de prueba; documentar el setup en `CONTRIBUTING.md` |
| `nitpicky = True` bloquea el build por referencias a tipos externos (xarray.DataArray) | Alta | Bajo | `nitpick_ignore` con allow-list explícita; cargar `intersphinx_mapping` para xarray/numpy/scipy |
| Atribuciones AI filtran al repo vía mensajes de commit o trailers automáticos del harness | Media | Alto | REQ-014 + script `tools/check-attribution.sh` en pre-commit y CI |
| Inconsistencia entre la promesa de la URL RTD (anunciada desde v0.1.x) y la entrega real genera ruido reputacional | Alta | Medio | T09 prioritaria; entrada en CHANGELOG `[Unreleased]` que comunique progreso |

## 8. Referencias

- Sphinx: https://www.sphinx-doc.org/
- Napoleon (NumPy/Google docstrings): https://sphinxcontrib-napoleon.readthedocs.io/
- MyST-NB (notebooks): https://myst-nb.readthedocs.io/
- MyST Parser (Markdown): https://myst-parser.readthedocs.io/
- sphinxcontrib-bibtex: https://sphinxcontrib-bibtex.readthedocs.io/
- Read the Docs configuration: https://docs.readthedocs.com/platform/stable/config-file/v2.html
- Ruff D rules: https://docs.astral.sh/ruff/rules/#pydocstyle-d
- EARS notation: https://alistairmavin.com/ears/
- [steering/architecture.md](../../steering/architecture.md)
- [steering/conventions.md](../../steering/conventions.md)
