# Requirements — temporal-frequency-resolver

**Estado:** Approved
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-15
**Última actualización:** 2026-05-16

## 1. Propósito

Inferir la frecuencia temporal de los datos de entrada siguiendo una jerarquía de cuatro tiers de evidencia: metadatos CF-conventions, parsing de nomenclatura mediante un catálogo extensible de parsers, heurística por conteo, y como último recurso una resolución asistida por callback (CLI) o un error tipado (API). El sub-componente `TemporalFrequencyResolver` (Capa 2 Detection, ver `steering/architecture.md`) produce un `ResolutionResult` determinista consumido por `StructureDetector` para poblar `DetectionResult.temporal_frequency` y `DetectionResult.confidence.temporal_frequency_tier` según el contrato fijado en ADR-0008 y `docs/schemas/detection-result.schema.md`.

## 2. Alcance

### In-scope

- Lectura de metadatos CF-conventions (`time.units`, `time.calendar`) ya cargados por la Capa 1 (I/O).
- Parsing de nomenclaturas conocidas mediante catálogo de parsers built-in: WorldClim, CHELSA, CHIRPS, ERA5.
- Heurística por conteo de archivos (12 → mensual o climatológico, 365/366 → diario, 52 → semanal, 24 → horario, N años → anual).
- Resolución asistida por callback inyectado (CLI provee prompt interactivo; API permite inyectar callback explícito).
- Enum normativo `TemporalFrequency` con valores `MONTHLY`, `DAILY`, `WEEKLY`, `CLIMATOLOGICAL`, `HOURLY`, `YEARLY` (alineado con `docs/schemas/detection-result.schema.md`).
- Output explícito `ResolutionResult` dataclass con frecuencia, tier ganador, confianza y evidencia textual corta.
- Registry extensible (`FrequencyParserRegistry`) que permite añadir parsers de terceros vía entry points o registro programático.
- Política de desempate entre tiers en conflicto: `cf_units > nomenclature > count_heuristic > callback`.

### Out-of-scope

- Reconocimiento de la variable física (responsabilidad de `VariableProfileMatcher`).
- Detección de estructura A/B/C (responsabilidad de `structure-detection`).
- Parsing de calendarios CF no-estándar (`360_day`, `noleap`, `julian`, `all_leap`). En v1.0 se rechazan con `UnsupportedCalendarError`.
- Normalización de timezones u offsets en coordenadas `time` (se asume UTC o naive según CF).
- Detección de eje espacial o coordenadas de proyección.
- Inferencia probabilística por ML (las confianzas son heurísticas deterministas per ADR-0008).

## 3. Actores y casos de uso

### Actor: Investigador con archivos descargados de fuentes mixtas sin convenciones uniformes

**Caso de uso típico:** El investigador apunta a una carpeta WorldClim; el parser `WorldClimParser` reconoce el patrón `wc2.1_*_tavg_MM.tif`, gana el tier `nomenclature` con confianza 0.9 y el sistema deduce frecuencia mensual sin interrumpir el pipeline.

### Actor: Desarrollador que consume `TemporalFrequencyResolver` como librería (API mode)

**Caso de uso típico:** El desarrollador integra tempify en un script batch sin TTY; si la jerarquía no converge y no se ha inyectado un callback, el resolver lanza `FrequencyResolutionError` con la evidencia parcial recolectada, permitiendo manejo programático.

## 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL attempt to resolve the temporal frequency in tier order: (1) CF-conventions, (2) filename parsing via the parser catalog, (3) count-based heuristic, (4) interactive callback. The resolved frequency SHALL be one of the values of the enum `TemporalFrequency = {MONTHLY, DAILY, WEEKLY, CLIMATOLOGICAL, HOURLY, YEARLY}`.

### REQ-002 (Event-driven)

WHEN CF-conventions metadata (`time.units` and `time.calendar`) is present and parseable, THE SYSTEM SHALL accept it as ground truth, assign `tier_used = "cf_units"` and report `confidence ∈ {0.95, 1.0}` per ADR-0008.

### REQ-003 (Event-driven)

WHEN a filename parser from the catalog matches with a regex score above 0.9, THE SYSTEM SHALL accept the parsed frequency, assign `tier_used = "nomenclature"` and cap the reported confidence at 0.9 per ADR-0008.

### REQ-004a (State-driven, CLI)

WHILE the resolver runs with a TTY and a disambiguation callback is registered, THE SYSTEM SHALL invoke that callback with the candidate frequencies and their per-tier confidences, allowing the user to resolve interactively. The result SHALL be returned with `tier_used = "interactive_callback"` and `confidence = 0.4`.

### REQ-004b (Unwanted)

IF the four-tier hierarchy fails to converge AND no disambiguation callback is registered (typical API / batch mode), THEN THE SYSTEM SHALL raise `FrequencyResolutionError` containing the partial evidence collected from each tier.

> Nota de naming: `architecture.md` § Reglas duras menciona `UnknownFrequencyError`. Se renombra a `FrequencyResolutionError` por ser estrictamente más específico: cubre tanto el caso "ningún tier produce candidato" como el caso "tiers en conflicto irresoluble", no solo el desconocido. La actualización al steering se tramita en la próxima revisión de `architecture.md`.

### REQ-005 (Optional)

WHERE the user provides an explicit `frequency: TemporalFrequency` argument to the resolver, THE SYSTEM SHALL skip detection entirely, assign `tier_used = "user_override"` and report `confidence = 1.0` with `source_evidence = "user override"`.

### REQ-006 (Ubiquitous)

THE SYSTEM SHALL expose an extensible filename parser catalog via `FrequencyParserRegistry`, with the four built-in parsers always pre-registered (WorldClim, CHELSA, CHIRPS, ERA5) and a public mechanism to register additional parsers (see REQ-009).

### REQ-007 (Ubiquitous)

THE SYSTEM SHALL return a `ResolutionResult` dataclass with the following fields:

- `frequency: TemporalFrequency`
- `tier_used: ResolutionTier` (enum: `cf_units`, `nomenclature`, `count_heuristic`, `interactive_callback`, `user_override`)
- `confidence: float` in the closed interval `[0.0, 1.0]`
- `source_evidence: str` (short human-readable string, <200 chars, no newlines, suitable for `DetectionResult.evidence["temporal_frequency"]`)

### REQ-008 (Unwanted, conflict resolution)

IF two or more tiers produce disagreeing candidates (e.g. CF says `MONTHLY` while a filename parser says `DAILY`), THEN THE SYSTEM SHALL prefer the higher-tier result following the strict ordering `cf_units > nomenclature > count_heuristic > interactive_callback`, AND THE SYSTEM SHALL emit a `WARN` annotation in `source_evidence` listing both candidates and the tier that won.

### REQ-009 (Ubiquitous, extensibility)

THE SYSTEM SHALL support extension of the parser catalog through either of the following mechanisms:

- Discovery via Python entry points group `tempify.frequency_parsers` (declared in third-party packages per PEP 621).
- Programmatic registration via `FrequencyParserRegistry.register(parser: BaseFilenameParser)` at runtime.

Both mechanisms SHALL produce identical observable behavior; collisions of parser names SHALL raise `ParserRegistrationError` at registration time, not at resolution time.

### REQ-010 (Ubiquitous, built-in catalog)

THE SYSTEM SHALL ship with the following four built-in filename parsers, each implementing `BaseFilenameParser`:

| Parser | Catálogo | Regex de ejemplo (no normativo) | Frecuencia | Confidence default |
|---|---|---|---|---|
| `WorldClimParser` | WorldClim 2.1 | `^wc2\.1_(?:30s\|2\.5m\|5m\|10m)_[a-z]+_(\d{2})\.tif$` | `MONTHLY` | 0.9 |
| `ChelsaParser` | CHELSA v2.1 | `^CHELSA_[a-z]+_(\d{2})_\d{4}_V\.\d\.\d\.tif$` | `MONTHLY` | 0.9 |
| `ChirpsParser` | CHIRPS v2.0 | `^chirps-v2\.0\.(\d{4})\.(\d{2})\.(\d{2})\.tif$` | `DAILY` | 0.9 |
| `Era5Parser` | ERA5 / ERA5-Land | `^era5(?:-land)?_[a-z0-9_]+_(\d{4})(\d{2})(\d{2})\d{2}\.(?:nc\|tif)$` | `HOURLY` o `DAILY` (según campo) | 0.9 |

Las regex listadas son ilustrativas: la implementación de cada parser puede ser más permisiva o estricta, pero SHALL documentar su patrón en el docstring y SHALL ser cubierta por la property test de NFR-002.

## 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Performance | Resolver la frecuencia sobre un conjunto de 366 archivos en <100 ms en hardware de referencia (single-thread, sin lectura de datos, solo metadata y nombres) | Benchmark `bench/test_resolver_perf.py::test_366_files_under_100ms` |
| NFR-002 | Reliability | Cobertura del catálogo built-in: property test con ≥10 variantes de filename por cada catálogo (WorldClim, CHELSA, CHIRPS, ERA5) y reconocimiento correcto en todas | Test parametrizado `test_catalog_property_coverage` con `@pytest.mark.parametrize` sobre fixtures |
| NFR-003 | Maintainability | Registry extensible documentado y testeado mediante un parser dummy externo registrado vía entry point y vía registro programático | Tests `test_registry_accepts_external_parser` y `test_registry_entry_point_discovery` |
| NFR-004 | Coverage | Cobertura del módulo `tempify.detection.frequency` ≥ 85% medida con `coverage.py` | Reporte CI bloquea PR si la cobertura cae bajo el umbral |

## 6. Criterios de aceptación

Trazabilidad REQ → test (cada REQ tiene al menos un test nombrado en `tests/detection/test_frequency_resolver.py`):

- [ ] REQ-001 → `test_tier_cf_wins` (orden de tiers respetado)
- [ ] REQ-002 → `test_tier_cf_wins` y `test_resolution_result_shape`
- [ ] REQ-003 → `test_tier_worldclim_pattern_match`, `test_tier_chelsa_pattern_match`, `test_tier_chirps_pattern_match`, `test_tier_era5_pattern_match`
- [ ] REQ-004a → `test_callback_invoked_when_ambiguous`
- [ ] REQ-004b → `test_raises_when_no_callback_and_unknown`
- [ ] REQ-005 → `test_user_override_skips_detection`
- [ ] REQ-006 → `test_builtin_parsers_preregistered`
- [ ] REQ-007 → `test_resolution_result_shape`
- [ ] REQ-008 → `test_conflicting_tiers_higher_wins`
- [ ] REQ-009 → `test_registry_accepts_external_parser`, `test_registry_entry_point_discovery`, `test_registry_collision_raises`
- [ ] REQ-010 → `test_tier_heuristic_count_12_means_monthly` (también cubre N=12 climatológico vs mensual) y los cuatro `test_tier_*_pattern_match` listados arriba
- [ ] NFR-001 → benchmark `test_366_files_under_100ms`
- [ ] NFR-002 → `test_catalog_property_coverage`
- [ ] NFR-003 → `test_registry_accepts_external_parser`
- [ ] NFR-004 → cobertura medida en CI ≥ 85%
- [ ] Documentación API (docstrings NumPy) completa para `TemporalFrequencyResolver`, `ResolutionResult`, `FrequencyParserRegistry`, `BaseFilenameParser`, y la jerarquía de excepciones
- [ ] CHANGELOG actualizado

## 7. Dependencias y supuestos

### Specs relacionadas

- **Bloqueada por:** [io-handlers](../io-handlers/requirements.md) (necesita lectura previa de metadata CF por los readers de la Capa 1).
- **Bloquea:** [structure-detection](../structure-detection/requirements.md) (el `StructureDetector` consume el `ResolutionResult` para poblar el `DetectionResult`), [pipeline](../pipeline/requirements.md), [cli](../cli/requirements.md), [gui](../gui/requirements.md).

### Supuestos

- Los archivos de entrada han sido enumerados y ordenados canónicamente (NFC) por la Capa 1 antes de pasar al resolver.
- La metadata CF, cuando está presente, ya fue extraída por el `BaseReader.metadata()` y se entrega como dict al resolver.
- En modo CLI, el callback de disambiguación es inyectado por la capa CLI (TTY garantizado). En modo API, el caller decide explícitamente si inyectar callback o aceptar `FrequencyResolutionError`.
- Los calendarios CF no-estándar quedan fuera del alcance v1.0 (ver §2 Out-of-scope).

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Conflicto entre tiers (CF dice `MONTHLY`, filename dice `DAILY`) | Media | Alto | REQ-008 fija política higher-wins documentada; `source_evidence` emite `WARN` con ambos candidatos |
| Regex de parsers built-in frágiles ante variantes de nomenclatura | Media | Medio | NFR-002 obliga a property test con ≥10 variantes por catálogo; parsers documentan patrón en docstring |
| N=12 ambiguo (mensual con año vs climatológico sin año) | Alta | Medio | Si CF metadata está disponible, prevalece su veredicto; en su ausencia, default a `CLIMATOLOGICAL` cuando ningún filename del set contiene un token de año (regex `\d{4}`) |
| Modo no-TTY (CI, batch) sin callback inyectado | Alta | Alto | REQ-004b: raise `FrequencyResolutionError` explícito; CLI provee callback automáticamente, API obliga a inyección consciente |
| Calendarios CF no-estándar (`360_day`, `noleap`, `julian`) | Baja | Medio | Out-of-scope v1.0; raise `UnsupportedCalendarError` con mensaje accionable |
| Colisión de nombres de parsers de terceros con built-ins | Baja | Bajo | `FrequencyParserRegistry.register` raises `ParserRegistrationError` en tiempo de registro, no en resolución |

## 8. Referencias

- ADR-0008: Confidence scoring and DetectionResult contract — `docs/adr/0008-confidence-scoring-and-detection-result-contract.md`.
- Schema canónico: `docs/schemas/detection-result.schema.md` (enum `TemporalFrequency`, claves `temporal_frequency` y `temporal_frequency_tier`).
- Steering: `steering/architecture.md` § Capa 2 Detection, sub-componente `TemporalFrequencyResolver`.
- CF Conventions: https://cfconventions.org/
- EARS notation: https://alistairmavin.com/ears/
- PEP 621 (entry points en `pyproject.toml`): https://peps.python.org/pep-0621/
