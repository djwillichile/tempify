# Requirements — security

**Estado:** Approved
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-17
**Última actualización:** 2026-05-17

## 1. Propósito

Establecer los requisitos de seguridad transversales del paquete `tempify` y los procesos asociados (auditoría, divulgación responsable, gobernanza del repositorio público). Las cláusulas son cross-cutting: aplican a todas las capas (`detection`, `io`, `interpolation`, `validation`, `pipeline`, `cli`) y a la presencia del proyecto en GitHub, PyPI y Zenodo.

## 2. Alcance

### In-scope

- Política de divulgación de vulnerabilidades (canal privado, SLAs).
- Higiene del repositorio público: ausencia de credenciales, PII no-pública, archivos generados; archivos de gobernanza estándar (`SECURITY.md`, `LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`).
- Higiene de dependencias: declaración explícita en `pyproject.toml`, alertas automáticas (Dependabot, `pip-audit`), preferencia por carga segura (e.g. `yaml.safe_load`).
- Patrones unsafe prohibidos en `src/`: `eval`, `exec`, `os.system`, `subprocess(shell=True)`, `pickle.load` sobre input no confiable, `yaml.load` sin `SafeLoader`.
- Reproducibilidad criptográfica: artefactos publicados (wheel + sdist + tag) firmados o atestiguados cuando la cadena lo soporte (PEP 740 / sigstore).
- Integridad del DOI: la versión declarada en `pyproject.toml`, `__version__`, `CITATION.cff` y la etiqueta del release de GitHub deben coincidir antes de publicar a Zenodo.
- Limpieza de outputs de notebooks: usernames de SO, paths absolutos del desarrollador y tokens accidentales son removidos antes de mergear a `main`.
- CI/CD básico: pipeline automatizado que verifica `pytest`, `ruff`, `mypy --strict` y un scan de secretos en cada PR antes de mergear a `main`.

### Out-of-scope

- Threat modeling completo a nivel de input adversarial sobre dependencias upstream (rasterio, GDAL): se delega a sus equipos.
- Pentest contra una eventual GUI o servicio web (responsabilidad de las specs `gui` y `packaging` cuando existan tales superficies).
- Cifrado at-rest de los datos del usuario (es una librería de procesamiento; el usuario decide cómo persiste sus rásters).
- Autenticación/autorización: `tempify` no maneja identidades.

## 3. Actores y casos de uso

### Actor 1: Investigador externo que detecta una vulnerabilidad

> Como investigador de seguridad, quiero un canal privado y documentado para reportar un hallazgo en `tempify` sin exponerlo públicamente antes de su corrección.

**Caso de uso típico:** abre un Private Vulnerability Report en GitHub o escribe a `contacto@icta.cl`; recibe acuse en ≤ 5 días hábiles; el fix sale en una release patch con crédito (a menos que pida anonimato).

### Actor 2: Mantenedor

> Como mantenedor, quiero que el repositorio público no exponga credenciales ni paths internos, y que cualquier regresión de seguridad sea detectada en CI antes de mergearse.

**Caso de uso típico:** abre un PR; CI corre `pytest`, lint, typecheck y `gitleaks`/`detect-secrets`; si hay un patrón sospechoso (e.g. token, `eval(`), CI falla y el PR se bloquea.

### Actor 3: Usuario que cita el software en un paper

> Como investigador que cita `tempify` (DOI 10.5281/zenodo.20251750), quiero estar seguro de que la versión instalada coincide bit-exactamente con la archivada en Zenodo.

**Caso de uso típico:** corre `python -c "import tempify; print(tempify.__version__)"`; el valor coincide con `version` en `pyproject.toml`, con el tag en GitHub y con la versión declarada en Zenodo. La cita es reproducible.

## 4. Requisitos funcionales (formato EARS)

### REQ-SEC-001 (Ubiquitous, divulgación responsable)

THE SYSTEM SHALL provide a documented vulnerability disclosure channel at `SECURITY.md`, including at minimum: contact email, GitHub Private Vulnerability Reporting URL, supported versions table, response SLAs.

### REQ-SEC-002 (Unwanted, secretos en repo)

IF a commit pushed to any branch introduces a credential pattern (`AKIA[0-9A-Z]{16}`, `ghp_[A-Za-z0-9]{36}`, `pypi-A[A-Za-z0-9_-]{40,}`, `-----BEGIN PRIVATE KEY-----`, `password\s*=\s*['"]`, `api_key\s*=\s*['"]`), THEN THE SYSTEM SHALL block the push via a pre-commit hook AND the CI pipeline SHALL fail the resulting PR.

### REQ-SEC-003 (Ubiquitous, patrones unsafe)

THE SYSTEM SHALL forbid the following Python constructs in `src/tempify/`: `eval(`, `exec(`, `os.system(`, `subprocess.*shell=True`, `pickle.load*` over untrusted input, `yaml.load(` without `SafeLoader`. The CI pipeline SHALL run a linter rule (Ruff S-rules) that flags these.

### REQ-SEC-004 (Ubiquitous, dependency hygiene)

THE SYSTEM SHALL declare all runtime dependencies in `pyproject.toml` with a lower-bound pin (`>=`). The repository SHALL have Dependabot enabled with weekly checks. New CVEs detected SHALL be triaged within 10 business days.

### REQ-SEC-005 (Event-driven, version consistency)

WHEN a new release is tagged in GitHub, THE SYSTEM SHALL verify that `pyproject.toml::project.version`, `src/tempify/__init__.py::__version__`, `CITATION.cff::version` and the tag string itself are byte-identical strings. Drift between any of them SHALL block the release workflow.

### REQ-SEC-006 (Event-driven, notebook hygiene)

WHEN a pre-executed notebook (`.ipynb`) is committed, THE SYSTEM SHALL ensure its outputs do not contain: OS usernames different from `runner` / generic placeholders, absolute paths under `C:\Users\<real>` or `/home/<real>`, tokens (any pattern matching REQ-SEC-002). A pre-commit step using `nbstripout` or equivalent sanitisation is REQUIRED.

### REQ-SEC-007 (Ubiquitous, governance files)

THE SYSTEM SHALL maintain the following governance files at the repo root: `LICENSE` (MIT), `SECURITY.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1 or equivalent), `CONTRIBUTING.md` pointing to `CLAUDE.md` for the SDD harness.

### REQ-SEC-008 (Ubiquitous, CI gating)

THE SYSTEM SHALL run a CI workflow on every PR that executes, at minimum: `pytest` (all unit tests pass, coverage ≥ 85% per module), `ruff check`, `mypy --strict`, secret scanning (`gitleaks` or `detect-secrets`). Merges to `main` SHALL require this workflow green.

### REQ-SEC-009 (Optional, supply chain)

WHERE the release pipeline publishes a wheel + sdist (e.g. to PyPI), THE SYSTEM SHOULD attach a PEP 740 attestation generated by `pypi-attestations` or sigstore so that downstream users can verify provenance cryptographically.

### REQ-SEC-010 (Unwanted, PII leakage)

IF a commit introduces PII not intentionally public (private addresses, phone numbers beyond ICTA contact, internal emails not `contacto@icta.cl`/`guillermo@icta.cl`/`guillermo.f1990@gmail.com`), THEN the pre-commit hook SHALL flag the file and require explicit override.

## 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-SEC-001 | Reliability | El disclosure channel `SECURITY.md` existe y es válido | Auditoría manual al cierre de cada release; `gh repo view --json hasSecurityPolicy` retorna `true`. |
| NFR-SEC-002 | Maintainability | El historial git no contiene secretos en commits previos | `gitleaks detect --log-opts=--all` retorna 0 hits, ejecutado al menos una vez por release. |
| NFR-SEC-003 | Reproducibilidad | `__version__` ≡ `pyproject.version` ≡ tag al momento del release | Test automático en CI: `pytest tests/release/test_version_consistency.py`. |
| NFR-SEC-004 | Performance del scan | Los hooks de pre-commit no deben superar 5 s sobre el árbol completo | Benchmark `time .claude/hooks/pre-commit.sh` con working tree limpio. |
| NFR-SEC-005 | Auditability | Existe un reporte de auditoría reciente en `specs/_audit/` ≤ 90 días | Verificar fecha del archivo más reciente bajo `specs/_audit/`. |

## 6. Criterios de aceptación

- [x] `SECURITY.md` existe y declara canal de reporte privado + SLAs.
- [x] Pyproject + `__version__` + `CITATION.cff` declaran `0.1.2` (alineado con DOI 10.5281/zenodo.20251750).
- [x] `src/` libre de patrones unsafe (verificado por auditoría 2026-05-17, ver `specs/_audit/2026-05-17-security-audit.md`).
- [ ] CI workflow básico (`pytest`, `ruff`, `mypy`, `gitleaks`) está pusheado a `.github/workflows/`. **Pendiente para v0.1.3.**
- [ ] Dependabot habilitado en repo settings. **Pendiente.**
- [ ] `CODE_OF_CONDUCT.md` + `CONTRIBUTING.md` en raíz. **Pendiente.**

## 7. Dependencias y supuestos

- **Dependencia hacia `_audit/`:** los reportes periódicos de auditoría son insumo para validar NFR-SEC-002 y NFR-SEC-005.
- **Supuesto:** mientras no exista una superficie de red (servicio HTTP, daemon), el threat model se limita a inputs locales del usuario y supply chain. Esto cambiará cuando se publique la GUI (spec `gui`) o un servidor.

## 8. Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Token/credencial accidentalmente committeado | Baja | Alto | REQ-SEC-002: pre-commit hook + CI gate |
| Drift de versión rompe cita Zenodo | Media | Medio | REQ-SEC-005: test automático en CI |
| Dependency con CVE no detectado | Media | Alto | REQ-SEC-004: Dependabot + `pip-audit` |
| PR malicioso desde fork con secrets exfiltration | Baja | Alto | REQ-SEC-008: workflows con `permissions: read-only` por defecto |
| Notebook commiteado con username/path local | Alta | Bajo | REQ-SEC-006: `nbstripout` pre-commit |

## 9. Referencias

- OWASP Software Component Verification Standard.
- GitHub Docs: Security advisories y Private Vulnerability Reporting.
- PEP 740 — Index support for digital attestations.
- Ruff rule set `S` (bandit-derived security rules).
- `specs/_audit/2026-05-17-security-audit.md` (reporte inicial).

## 10. Trazabilidad REQ → tests / verificación

- [x] REQ-SEC-001 → presencia de `SECURITY.md` + revisión manual.
- [ ] REQ-SEC-002 → `tests/security/test_no_secrets_pattern.py` (pendiente).
- [x] REQ-SEC-003 → ruff config con S-rules; verificado por auditoría.
- [ ] REQ-SEC-004 → presencia de `.github/dependabot.yml` (pendiente).
- [ ] REQ-SEC-005 → `tests/release/test_version_consistency.py` (pendiente, ver siguiente release).
- [ ] REQ-SEC-006 → `.pre-commit-config.yaml` con `nbstripout` (pendiente).
- [x] REQ-SEC-007 → `SECURITY.md` listo; `CODE_OF_CONDUCT.md` y `CONTRIBUTING.md` pendientes para v0.1.3.
- [ ] REQ-SEC-008 → `.github/workflows/ci.yml` (pendiente, ver tracking issue).
- [ ] REQ-SEC-009 → opcional, evaluado cuando se publique a PyPI.
- [ ] REQ-SEC-010 → pre-commit con regex de PII (pendiente).
