# Design — temporal-frequency-resolver

**Estado:** Draft
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-15

## 1. Visión técnica

El `TemporalFrequencyResolver` es un sub-componente puro (sin I/O) de la Capa 2 Detection que infiere la frecuencia temporal de un conjunto de archivos enumerados aplicando una jerarquía estricta de cuatro tiers de evidencia: metadatos CF-conventions ya extraídos por la Capa 1, parsing de nomenclatura mediante un catálogo extensible de regex parsers, heurística por conteo, y resolución asistida por callback inyectable. Su salida es un `ResolutionResult` inmutable que el `StructureDetector` consume para poblar `DetectionResult.temporal_frequency` y la clave canónica `confidence.temporal_frequency_tier` definida en ADR-0008.

El diseño persigue tres invariantes: (1) determinismo bit-exact sobre el mismo input (alineado con ADR-0007); (2) extensibilidad pública del catálogo de parsers sin tocar el core, vía entry points y registro programático; (3) ausencia total de side effects de I/O, dado que la metadata CF llega ya parseada y los nombres se inspeccionan como strings.

## 2. Arquitectura propuesta

### Diagrama de componentes

```
tempify.detection.frequency
├── resolver.py           TemporalFrequencyResolver, ResolutionResult, ResolutionTier
├── registry.py           FrequencyParserRegistry, entry-point discovery
├── parsers
│   ├── base.py           BaseFilenameParser (ABC)
│   ├── worldclim.py      WorldClimParser
│   ├── chelsa.py         ChelsaParser
│   ├── chirps.py         ChirpsParser
│   └── era5.py           Era5Parser
├── cf_tier.py            CF-conventions parsing helper (cftime)
├── heuristic.py          Count-based heuristic
└── errors.py             FrequencyResolutionError, UnsupportedCalendarError,
                          ParserRegistrationError

         StructureDetector (caller)
                 │
                 ▼
  ┌─────────────────────────────┐
  │ TemporalFrequencyResolver   │
  │  .resolve(files, cf_meta)   │
  └─────────────────────────────┘
            │   pipeline higher-wins (REQ-008)
            ▼
  Tier 1: cf_tier.parse_cf(metadata)            ── confidence ∈ {0.95, 1.0}
  Tier 2: registry.iter_parsers() → match       ── confidence ≤ 0.9
  Tier 3: heuristic.from_count(files)           ── confidence = 0.7
  Tier 4: callback(candidates) (si registrado)  ── confidence = 0.4
            │
            ▼
        ResolutionResult
```

### Componentes nuevos

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| `TemporalFrequencyResolver` | `src/tempify/detection/frequency/resolver.py` | Orquesta la jerarquía de tiers y construye el `ResolutionResult`. |
| `ResolutionResult` | `src/tempify/detection/frequency/resolver.py` | Dataclass inmutable de salida (REQ-007). |
| `ResolutionTier` | `src/tempify/detection/frequency/resolver.py` | `StrEnum` con los cinco tiers contractuales. |
| `BaseFilenameParser` | `src/tempify/detection/frequency/parsers/base.py` | ABC del catálogo de parsers, con `parse()` y `confidence` declarativos. |
| `FrequencyParserRegistry` | `src/tempify/detection/frequency/registry.py` | Registro singleton-por-instancia con dual mechanism (entry points + programmatic). |
| `WorldClimParser`, `ChelsaParser`, `ChirpsParser`, `Era5Parser` | `src/tempify/detection/frequency/parsers/*.py` | Parsers built-in (REQ-010). |
| `_parse_cf_metadata` | `src/tempify/detection/frequency/cf_tier.py` | Helper puro que interpreta `time.units` y `time.calendar` con `cftime`. |
| `_resolve_from_count` | `src/tempify/detection/frequency/heuristic.py` | Heurística por conteo, incluido el desempate 12 → MONTHLY vs CLIMATOLOGICAL. |
| `FrequencyResolutionError`, `UnsupportedCalendarError`, `ParserRegistrationError` | `src/tempify/detection/frequency/errors.py` | Jerarquía de excepciones tipadas. |

### Componentes modificados

| Componente | Ubicación | Cambio |
|---|---|---|
| `StructureDetector` | `src/tempify/detection/structure.py` | Inyectará una instancia de `TemporalFrequencyResolver` en su constructor; será modificado en su propia spec, no aquí. |
| `steering/architecture.md` § Reglas duras | `steering/architecture.md` | Nota pendiente: rename `UnknownFrequencyError` → `FrequencyResolutionError` (se tramitará en revisión siguiente del steering). |

## 3. Contratos públicos (APIs)

### `TemporalFrequencyResolver`

```python
class TemporalFrequencyResolver:
    """Resuelve la frecuencia temporal de un conjunto de archivos por tiers."""

    def __init__(
        self,
        registry: FrequencyParserRegistry,
        callback: Callable[[list[ResolutionResult]], TemporalFrequency] | None = None,
    ) -> None: ...

    def resolve(
        self,
        files: list[Path],
        cf_metadata: dict[str, Any] | None = None,
        *,
        override: TemporalFrequency | None = None,
    ) -> ResolutionResult: ...
```

**Pre-condiciones:**
- `files` es no-vacío y ya viene ordenado canónicamente (NFC) por la Capa 1.
- `cf_metadata`, si se pasa, contiene al menos `time.units` y opcionalmente `time.calendar`.
- `registry` está construido con los parsers built-in pre-registrados.

**Post-condiciones:**
- Devuelve un `ResolutionResult` con `frequency`, `tier_used`, `confidence ∈ [0.0, 1.0]`, y `source_evidence` (<200 chars, sin newlines).
- En conflicto entre tiers, prevalece el tier superior por REQ-008, y `source_evidence` contiene el token `WARN: <higher>={X} > <lower>={Y}`.

**Excepciones lanzadas:**
- `FrequencyResolutionError`: ningún tier converge y no hay callback.
- `UnsupportedCalendarError`: el calendar CF es no-estándar (`360_day`, `noleap`, `julian`, `all_leap`).

### `BaseFilenameParser`

```python
@dataclass(frozen=True, slots=True)
class ParseResult:
    """Resultado de parsing por filename, ahora con info de fecha extraída."""
    frequency: TemporalFrequency
    confidence: float  # [0, 1]
    time_point: datetime | None        # punto único si filename codifica fecha exacta
    time_range: tuple[datetime, datetime] | None  # rango si codifica periodo
    month_of_year: int | None          # 1..12 si solo hay mes-de-año sin año
    year: int | None
    band_index: int | None             # para multi-band GeoTIFF cuando aplica


class BaseFilenameParser(ABC):
    """Parser de nomenclatura para una fuente de datos conocida."""

    name: ClassVar[str]            # Identificador único en el registry
    confidence: ClassVar[float]    # Confianza declarativa (≤ 0.9 por REQ-003)

    @abstractmethod
    def parse(self, filename: str) -> ParseResult | None:
        """Intenta extraer frecuencia + fecha codificada. None si no matchea."""
```

**Pre-condiciones:** `filename` es `Path.name` (no ruta completa), ya normalizado a NFC.
**Post-condiciones:** Si retorna `ParseResult`, su `frequency` es la nominal del catálogo y su `confidence ≤ 0.9` (REQ-003). El resolver consume el `ParseResult` para construir el `ResolutionResult` agregado y el `time_axis`.

### `FrequencyParserRegistry`

```python
class FrequencyParserRegistry:
    """Registro de parsers built-in y externos."""

    def __init__(self, *, load_entry_points: bool = True) -> None: ...
    def register(self, parser_cls: type[BaseFilenameParser]) -> None: ...
    def iter_parsers(self) -> Iterator[BaseFilenameParser]: ...
    @classmethod
    def with_builtins(cls) -> "FrequencyParserRegistry": ...
```

**Pre-condiciones:** `parser_cls` hereda de `BaseFilenameParser` y declara `name` único.
**Post-condiciones:** `iter_parsers()` recorre primero built-ins, luego entry points, luego registrados programáticamente.
**Excepciones lanzadas:** `ParserRegistrationError` si colisiona `name`.

### Jerarquía de excepciones

```python
class FrequencyResolutionError(RuntimeError):
    """Levantada cuando la jerarquía no converge o detecta conflicto irresoluble."""
    partial_evidence: dict[ResolutionTier, ResolutionResult | None]

class UnsupportedCalendarError(FrequencyResolutionError):
    """Calendar CF no soportado en v1.0 (360_day, noleap, julian, all_leap)."""

class ParserRegistrationError(ValueError):
    """Colisión de `name` en el registry."""
```

## 4. Modelos de datos

### `ResolutionTier`

```python
from enum import StrEnum

class ResolutionTier(StrEnum):
    CF_METADATA = "cf_units"
    FILENAME_PATTERN = "nomenclature"
    COUNT_HEURISTIC = "count_heuristic"
    INTERACTIVE_CALLBACK = "interactive_callback"
    USER_OVERRIDE = "user_override"
```

**Nota de reconciliación 4 vs 5 tiers.** REQ-001 declara cuatro tiers de inferencia. `USER_OVERRIDE` (REQ-005) no es un tier de inferencia sino un short-circuit: el resolver lo procesa antes de entrar al pipeline de tiers y nunca aparece en `partial_evidence`. ADR-0008 codifica solo los cuatro tiers de inferencia en `confidence.temporal_frequency_tier ∈ {1.0, 0.9, 0.7, 0.4}`; el override no añade un quinto valor numérico, simplemente reusa `1.0` por construcción (`source_evidence = "user override"`).

### `ResolutionResult`

```python
@dataclass(frozen=True)
class ResolutionResult:
    frequency: TemporalFrequency
    tier_used: ResolutionTier
    confidence: float           # [0.0, 1.0]
    source_evidence: str        # <200 chars, sin newlines
    time_axis: list[datetime] | None = None  # eje temporal ensamblado (REQ-011/REQ-013)
    monthly_anchor_applied: Literal["midpoint", "start", "end", "custom"] | None = None  # REQ-012
    calendar_agnostic: bool = False  # True si el axis se construyó sin años explícitos

    def __post_init__(self) -> None:
        # Validaciones: rango, longitud, ausencia de '\n', tier_used ∈ enum,
        # time_axis estrictamente creciente cuando no es None.
        ...
```

El resolver ensambla `time_axis` ordenando los `time_point` retornados por los parsers, o calculando los midpoints (per ADR-0015) cuando solo hay `month_of_year`. Si no hay año explícito en ningún filename, se marca `calendar_agnostic=True` y se emite un warning.

El mapeo a la clave canónica del schema es directo:
- `ResolutionResult.frequency` → `DetectionResult.temporal_frequency`.
- `tier_used` → `DetectionResult.confidence["temporal_frequency_tier"]` vía tabla del ADR-0008 (`CF_METADATA=1.0`, `FILENAME_PATTERN=0.9`, `COUNT_HEURISTIC=0.7`, `INTERACTIVE_CALLBACK=0.4`, `USER_OVERRIDE=1.0`).
- `confidence` → `DetectionResult.confidence["temporal_frequency"]`.
- `source_evidence` → `DetectionResult.evidence["temporal_frequency"]`.

## 5. Algoritmos clave

### Algoritmo 1: orquestación de tiers

Pseudo-código de `TemporalFrequencyResolver.resolve`:

```
if override is not None:
    return ResolutionResult(override, USER_OVERRIDE, 1.0, "user override")

partial: dict[ResolutionTier, ResolutionResult | None] = {}

# Tier 1: CF
cf_result = _parse_cf_metadata(cf_metadata) if cf_metadata else None
partial[CF_METADATA] = cf_result

# Tier 2: Nomenclature
name_result = _try_parsers(files, registry)
partial[FILENAME_PATTERN] = name_result

# Tier 3: Count heuristic
count_result = _resolve_from_count(files)
partial[COUNT_HEURISTIC] = count_result

# Conflict resolution: higher-wins (REQ-008)
winner = first_non_null([cf_result, name_result, count_result])
if winner is not None:
    return _annotate_conflicts(winner, partial)

# Tier 4: Callback
if callback is not None:
    candidates = [r for r in partial.values() if r is not None]
    chosen_freq = callback(candidates)
    return ResolutionResult(chosen_freq, INTERACTIVE_CALLBACK, 0.4,
                            f"callback chose {chosen_freq.value}")

# All tiers failed and no callback
raise FrequencyResolutionError(partial_evidence=partial)
```

**Complejidad:** O(N · P) donde N=|files| y P=|parsers|. Para N≤366 y P~5, NFR-001 (<100 ms) holgado.

### Algoritmo 2: CF-conventions parsing (`_parse_cf_metadata`)

1. Extraer `units = cf_metadata["time"]["units"]` (e.g. `"days since 1970-01-01"`).
2. Extraer `calendar = cf_metadata["time"].get("calendar", "standard")`.
3. Si `calendar` ∉ `{"standard", "gregorian", "proleptic_gregorian"}`, lanzar `UnsupportedCalendarError`.
4. Si `cf_metadata["time"]` incluye valores numéricos, decodificar con `cftime.num2date(values, units, calendar)` y calcular el delta dominante:
   - `Δ ≈ 1 día` → `DAILY`.
   - `Δ ≈ 28-31 días` → `MONTHLY`.
   - `Δ ≈ 7 días` → `WEEKLY`.
   - `Δ ≈ 1 hora` → `HOURLY`.
   - `Δ ≈ 365-366 días` → `YEARLY`.
5. Confidence: `1.0` si match exacto (delta uniforme dentro de tolerancia), `0.95` si parcial (e.g. falta `calendar`, asumido `standard`).
6. `source_evidence`: cadena del tipo `"CF time:units='days since 1970-01-01', Δ_mediana=1.0d"`.

### Algoritmo 3: Filename parsing (`_try_parsers`)

Para cada parser en `registry.iter_parsers()` (orden: built-ins → entry points → programmatic):

1. Aplicar `parser.parse(Path(f).name)` sobre los primeros K nombres (default K=min(8, len(files))) y exigir consenso ≥ 75%.
2. Si hay consenso, retornar el `ResolutionResult` del parser ganador con `confidence = parser.confidence` (≤ 0.9 por REQ-003).
3. Si dos parsers matchean con distintas frecuencias, prevalece el primero del orden de iteración y `source_evidence` anota la colisión (`WARN: nomenclature parsers in conflict: WorldClim=MONTHLY, ChirpsLike=DAILY`).

### Algoritmo 4: Count heuristic (`_resolve_from_count`)

```
N = len(files)
match N:
    case 12:  return MONTHLY si exista \d{4} en ≥1 filename, else CLIMATOLOGICAL
    case 24:  return HOURLY (24 valores intradiarios)
    case 52:  return WEEKLY
    case 365 | 366: return DAILY
    case n if n ≥ 2 and all filenames contain distinct \d{4}: return YEARLY
    case _: return None  # heurística no concluye
```

`confidence = 0.7` fijo (ADR-0008). `source_evidence = f"count_heuristic N={N}, year_token={'present'|'absent'}"`.

### Algoritmo 5: Conflict annotation (`_annotate_conflicts`)

Recibe el ganador y el dict de evidencia parcial. Si dos o más tiers no-null discrepan en `frequency`, retorna un nuevo `ResolutionResult` con el ganador intacto pero `source_evidence` prefijado por `WARN: <winner_tier>={X} > <other_tier>={Y}`. Esta es la implementación literal de REQ-008.

### Algoritmo 6: construcción de `time_axis` (REQ-011, REQ-012, REQ-013)

Pseudo-código de `_build_time_axis(parse_results, anchor, band_descriptions)`:

```
1. Si band_descriptions están disponibles y parsean ISO 8601 → usar como axis (REQ-013, fuente preferente).
2. Para cada archivo del stack, invocar parsers en orden y obtener un ParseResult.
3. Si el ParseResult retorna time_point → usarlo directamente.
4. Si retorna month_of_year + year → construir datetime con el anchor configurado:
     - midpoint (default, ADR-0015): día ≈ 15 (o ceil(mid_of_month)).
     - start: día 1.
     - end: último día calendárico del mes.
     - custom: callable provisto por PipelineConfig.monthly_anchor_fn.
5. Si retorna month_of_year sin year → construir con midpoint del mes en un
   "año-plantilla" arbitrario (1970), marcar el axis como calendar_agnostic=True
   y emitir warning `CALENDAR_AGNOSTIC: month-only encoding (no year present)`.
6. Si retorna time_range (e.g. mensual con día implícito) → reducir al anchor.
7. Ordenar el axis cronológicamente y deduplicar.
8. Validar continuidad: los deltas observados deben coincidir con la frecuencia
   inferida (tolerancia ±10% para frecuencias sub-diarias y mensuales).
```

**Precedencia de fuentes (REQ-013):** band descriptions ISO > filename parsing > inferencia pura por frecuencia. Esta precedencia es independiente de la jerarquía de tiers de frecuencia: aquí se trata del *eje concreto*, no de la frecuencia nominal.

### Algoritmo 7: `MultiBandGeoTIFFBandDescriptionParser`

Parser auxiliar especializado en modo A (multi-band GeoTIFF). Lee las descripciones de banda expuestas como `GDAL_BAND_DESCRIPTIONS` (ya extraídas por la Capa 1) e intenta parsear cada descripción como ISO 8601 (`YYYY-MM-DD`, `YYYY-MM-DDTHH:MM:SS`, etc.). Si todas las bandas parsean, retorna un `time_axis` directo y un `ParseResult` con `band_index` poblado por entrada. Si solo un subconjunto parsea, retorna `None` (no fallback parcial: degrada hacia filename parsing).

## 6. Parser catalog built-in

Tabla de los cuatro parsers obligatorios (REQ-010). Las regex aquí son ilustrativas; la implementación final puede ser más permisiva siempre que pase la property test de NFR-002 (≥10 variantes por catálogo).

| Parser | `name` | Regex (ilustrativa) | Frecuencia | Confidence |
|---|---|---|---|---|
| `WorldClimParser` | `worldclim` | `^wc2\.1_(?:30s\|2\.5m\|5m\|10m)_[a-z]+_(?:(?P<year>\d{4})_)?(?P<month>\d{2})\.tif$` | `MONTHLY` | 0.9 |
| `ChelsaParser` | `chelsa` | `^CHELSA_[a-z]+_(?P<year>\d{4})_(?P<month>\d{2})_V\.\d\.\d\.tif$` | `MONTHLY` | 0.9 |
| `ChirpsParser` | `chirps` | `^chirps-v2\.0\.(?P<year>\d{4})\.(?P<month>\d{2})(?:\.(?P<day>\d{2}))?\.tif$` | `DAILY` (con `day`) / `MONTHLY` (sin `day`) | 0.9 |
| `Era5Parser` | `era5` | `^era5_(?P<var>[a-z0-9_]+)_(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})_(?P<hour>\d{2})\.(nc\|tif)$` | `HOURLY` (con `hour`) / `DAILY` (sin `hour`) | 0.9 / 0.85 |

`Era5Parser` usa cinco grupos nombrados (`var`, `year`, `month`, `day`, `hour`) y desambigua por la presencia del grupo `hour` en el match: si `hour` está capturado, la frecuencia es `HOURLY` con confidence `0.9`; si los nombres del set no incluyen la parte `_hh` (grupo `hour` ausente), el parser devuelve `frequency=DAILY` con confidence `0.85`. La regla "presencia/ausencia del grupo" sustituye la heurística previa basada en hora fija `_00.`, que era ambigua frente a regex con grupo posicional.

## 7. Decisiones de diseño

### Decisión 1: rename `UnknownFrequencyError` → `FrequencyResolutionError`

**Opciones consideradas:**
1. Mantener `UnknownFrequencyError` (alineado con `architecture.md`).
2. Renombrar a `FrequencyResolutionError`.

**Decisión:** Opción 2.
**Razón:** El error cubre dos escenarios (jerarquía sin candidatos y tiers en conflicto irresoluble), no solo "desconocido". El nombre `FrequencyResolutionError` describe mejor el dominio y permite subclasear (`UnsupportedCalendarError`) sin acrobacias semánticas. La spec de requirements ya marca la actualización pendiente al steering.

### Decisión 2: dual mechanism para el registry (entry points + programmatic)

**Opciones consideradas:**
1. Solo entry points (Python estándar, declarativo).
2. Solo registro programático (más simple, peor para terceros).
3. Ambos, con orden de precedencia documentado.

**Decisión:** Opción 3.
**Razón:** Entry points dan extensión estable para paquetes terceros (e.g. `tempify-modis`) sin patches; el registro programático cubre testing y uso ad-hoc en notebooks. Orden de iteración: built-ins → entry points → programmatic, garantiza que el comportamiento sea predecible.
**Trade-offs:** Carga de entry points implica una primera invocación más lenta (~1-5 ms). Mitigado con cache en el constructor del registry.

### Decisión 3: `ResolutionTier` con 5 valores aunque REQ-001 hable de 4 tiers

**Opciones consideradas:**
1. Enum con 4 valores (omitir `USER_OVERRIDE`).
2. Enum con 5 valores, documentando que el quinto es short-circuit no-tier.

**Decisión:** Opción 2.
**Razón:** REQ-005 obliga a marcar el override en `tier_used`. Tener un valor enumerado es más limpio que un magic string. ADR-0008 sigue contemplando solo cuatro encodings numéricos en `confidence.temporal_frequency_tier`; el override reusa el slot `1.0` por construcción (equivale en confianza a CF exacto).

### Decisión 4: callback como dependencia inyectada, no I/O integrado

**Opciones consideradas:**
1. Resolver levanta directamente `input()` cuando no converge.
2. Resolver recibe un callback opcional y no toca stdin.

**Decisión:** Opción 2.
**Razón:** Pureza arquitectónica: la Capa 2 no hace I/O (regla dura del `architecture.md`). La Capa 6 (CLI) inyecta el callback con su propio prompt Typer; la API permite inyección programática para tests y batch.

## 8. Estrategia de testing

### Tests unitarios por tier

- `test_tier_cf_wins` — CF metadata presente → `tier_used == CF_METADATA`, confidence ∈ {0.95, 1.0}.
- `test_tier_cf_unsupported_calendar` — calendar `360_day` levanta `UnsupportedCalendarError`.
- `test_tier_worldclim_pattern_match` — set canónico `wc2.1_30s_tavg_01.tif`...`12.tif` → `MONTHLY`, 0.9.
- `test_tier_chelsa_pattern_match` — análogo para CHELSA.
- `test_tier_chirps_pattern_match` — set CHIRPS diario → `DAILY`, 0.9.
- `test_tier_era5_pattern_match` — set ERA5 con sufijo `_hh` (grupo `hour` capturado) → `HOURLY` con confidence `0.9`; set ERA5 sin sufijo `_hh` (grupo `hour` ausente) → `DAILY` con confidence `0.85`.
- `test_tier_heuristic_count_12_means_monthly` — 12 archivos con token `\d{4}` → `MONTHLY`; sin token → `CLIMATOLOGICAL`.
- `test_tier_heuristic_count_365_means_daily` — 365 archivos sin nombres reconocibles.
- `test_callback_invoked_when_ambiguous` — todos los tiers retornan None excepto callback, que se llama con `partial_evidence`.

### Tests de orquestación

- `test_user_override_skips_detection` — override CLI atajado en línea 1 del algoritmo.
- `test_conflicting_tiers_higher_wins` — CF=MONTHLY, parser=DAILY → gana MONTHLY, `source_evidence` contiene `WARN`.
- `test_raises_when_no_callback_and_unknown` — todos los tiers fallan + callback=None → `FrequencyResolutionError`.
- `test_resolution_result_shape` — valida campos, rango, ausencia de newlines, longitud <200.
- `test_partial_evidence_in_exception` — la excepción expone `partial_evidence` con keys `CF_METADATA`, `FILENAME_PATTERN`, `COUNT_HEURISTIC`.

### Tests property-based (hypothesis)

- `test_catalog_property_coverage` parametrizado: ≥10 variantes de filename por cada catálogo built-in (WorldClim, CHELSA, CHIRPS, ERA5), todas reconocidas (cubre NFR-002).
- `test_count_heuristic_idempotent` — orden de `files` no afecta el resultado (verifica invariante de NFC).

### Tests de registry y extensibilidad

- `test_builtin_parsers_preregistered` — `FrequencyParserRegistry.with_builtins()` expone los cuatro.
- `test_registry_accepts_external_parser` — registro programático de un parser dummy, `iter_parsers` lo incluye al final.
- `test_registry_entry_point_discovery` — fixture instala un parser dummy vía entry point `tempify.frequency_parsers` y verifica descubrimiento (usar `pytest-tmppath` + `pkg_resources` stub).
- `test_registry_collision_raises` — registrar dos parsers con mismo `name` → `ParserRegistrationError`.

### Tests no-TTY

- `test_no_tty_raises_frequency_resolution_error` — entorno simulado sin callback inyectado y tiers no convergen → `FrequencyResolutionError`.

### Tests de extracción de eje temporal (REQ-011, REQ-012, REQ-013)

- `test_worldclim_extracts_month_only_axis_with_midpoint` — set canónico de 12 filenames WorldClim sin año → `time_axis` con 12 datetimes anclados al midpoint (día ≈15), `calendar_agnostic=True`, warning emitido.
- `test_chelsa_extracts_year_month_axis` — set CHELSA con año explícito → `time_axis` con `year+month` y midpoint aplicado, `calendar_agnostic=False`.
- `test_chirps_extracts_daily_axis` — set CHIRPS con `YYYY.MM.DD` → `time_axis` con fechas exactas, sin anchor (`monthly_anchor_applied=None`).
- `test_era5_extracts_hourly_axis` — set ERA5 con grupo `hour` capturado → `time_axis` con resolución horaria.
- `test_multiband_geotiff_band_description_axis` — modo A con `GDAL_BAND_DESCRIPTIONS` ISO 8601 → axis tomado de las bandas, filename parsing ignorado (REQ-013).
- `test_monthly_anchor_override_start` — `PipelineConfig.monthly_anchor='start'` → todos los time points caen en día 1.
- `test_calendar_agnostic_warning_when_no_year` — month-only sin año → warning con token `CALENDAR_AGNOSTIC`.

### Fixtures necesarios

- `synthetic_cf_monthly.json` — dict con `time.units` y `time.calendar` para tier 1.
- `worldclim_names_set.json`, `chelsa_names_set.json`, `chirps_names_set.json`, `era5_names_set.json` — listas de 12+ nombres canónicos por catálogo.
- `dummy_external_parser.py` — parser fixture para los tests de extensibilidad.

### Benchmark (NFR-001)

- `bench/test_resolver_perf.py::test_366_files_under_100ms` — input sintético de 366 nombres, ejecución single-thread, asserta `< 100 ms`.

## 9. Plan de migración

No aplica: feature greenfield. Las modificaciones colaterales (`StructureDetector` consume el `ResolutionResult`, rename de `UnknownFrequencyError` en `architecture.md`) se realizan en sus respectivas specs.

## 10. Métricas de calidad

| Métrica | Umbral |
|---|---|
| Coverage del módulo `tempify.detection.frequency` | ≥ 85% (NFR-004) |
| Performance (366 nombres + metadata CF) | < 100 ms (NFR-001) |
| Memoria peak | < 50 MB (resolver puro, sin lectura de datos) |
| Variantes property-test por catálogo | ≥ 10 (NFR-002) |

## 11. Trazabilidad requirements → design

| Requirement | Componente que lo implementa |
|---|---|
| REQ-001 | `TemporalFrequencyResolver.resolve` § Algoritmo 1 |
| REQ-002 | `_parse_cf_metadata` § Algoritmo 2 |
| REQ-003 | `BaseFilenameParser.confidence` (cap 0.9), `_try_parsers` § Algoritmo 3 |
| REQ-004a | rama `if callback is not None` en Algoritmo 1 |
| REQ-004b | rama final `raise FrequencyResolutionError` en Algoritmo 1 |
| REQ-005 | short-circuit `override` en línea 1 del Algoritmo 1 |
| REQ-006 | `FrequencyParserRegistry.with_builtins` |
| REQ-007 | `ResolutionResult` dataclass + `__post_init__` |
| REQ-008 | `_annotate_conflicts` + ordenamiento higher-wins en Algoritmo 1 |
| REQ-009 | `FrequencyParserRegistry.register` + entry-point loader |
| REQ-010 | `WorldClimParser`, `ChelsaParser`, `ChirpsParser`, `Era5Parser` § 6 |
| REQ-011 | `ParseResult` (campos `time_point`, `month_of_year`, `year`) + `_build_time_axis` § Algoritmo 6 |
| REQ-012 | `PipelineConfig.monthly_anchor` aplicado en pasos 4-5 del Algoritmo 6 |
| REQ-013 | `MultiBandGeoTIFFBandDescriptionParser` § Algoritmo 7 + precedencia en paso 1 del Algoritmo 6 |
| NFR (consistencia) | Validación de continuidad en paso 8 del Algoritmo 6 + tests de extracción de eje |
| NFR-001 | benchmark `test_366_files_under_100ms` |
| NFR-002 | property test `test_catalog_property_coverage` |
| NFR-003 | `test_registry_accepts_external_parser`, `test_registry_entry_point_discovery` |
| NFR-004 | coverage configurado en CI |
