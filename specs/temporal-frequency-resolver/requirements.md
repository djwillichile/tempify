# Requirements — temporal-frequency-resolver

**Estado:** Draft
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-15
**Última actualización:** 2026-05-15

## 1. Propósito

Inferir la frecuencia temporal de los datos de entrada siguiendo una jerarquía de fuentes de información: metadatos CF-conventions, parsing de nomenclatura, heurística por conteo, y como último recurso, solicitud interactiva al usuario.

## 2. Alcance

### In-scope

- Lectura de metadatos CF-conventions (`time.units`, `time.calendar`).
- Parsing de nomenclaturas conocidas: WorldClim, CHELSA, CHIRPS, ERA5.
- Heurística por conteo de archivos (12 → mensual, 365/366 → diario, 52 → semanal).
- Fallback interactivo (callback al CLI o parámetro en API).

### Out-of-scope

- Reconocimiento de la variable (responsabilidad de `VariableProfileMatcher`).
- Detección de estructura (responsabilidad de `structure-detection`).

## 3. Actores y casos de uso

### Actor: Investigador que tiene archivos descargados de fuentes mixtas sin convenciones uniformes.

**Caso de uso típico:** Investigador apunta a una carpeta WorldClim; el sistema reconoce el patrón `wc2.1_*_tavg_MM.tif` y deduce frecuencia mensual sin preguntar.

## 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL attempt to resolve temporal frequency in the following order: (1) CF-conventions, (2) filename parsing, (3) count-based heuristic, (4) interactive prompt.

### REQ-002 (Event-driven)

WHEN CF-conventions metadata is present and valid, THE SYSTEM SHALL accept it as ground truth without further inference.

### REQ-003 (Event-driven)

WHEN filename parsing succeeds with a confidence above 0.9, THE SYSTEM SHALL accept the parsed frequency.

### REQ-004 (State-driven)

WHILE no automatic detection is possible, THE SYSTEM SHALL request explicit user input via callback (CLI) or raise `FrequencyResolutionError` (API mode).

### REQ-005 (Optional)

WHERE the user provides an explicit `frequency` argument, THE SYSTEM SHALL skip detection and use the provided value.

### REQ-006 (Ubiquitous)

THE SYSTEM SHALL support an extensible filename parser registry, allowing users to register custom patterns.

## 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Reliability | Todas las decisiones deben ser trazables en el reporte de procesamiento | Inspección manual del reporte generado |
| NFR-002 | Usability | Mensajes de error en español, con código referenciable | Test `test_error_messages_spanish` |

## 6. Criterios de aceptación

- [ ] Todos los REQ cubiertos por tests específicos
- [ ] Cobertura del módulo >= 85%
- [ ] Documentación API completa (docstrings NumPy)
- [ ] CHANGELOG actualizado

## 7. Dependencias y supuestos

### Specs relacionadas

- Bloqueada por: [core-interpolation](../core-interpolation/requirements.md)
- Bloquea: [cli](../cli/requirements.md) (transitivamente)

### Supuestos

- Los inputs son archivos legibles por GDAL via rioxarray.

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Edge cases en formatos no estándar | Media | Bajo | Fixtures extensivas + manejo robusto de excepciones |

## 8. Referencias

- CF Conventions: https://cfconventions.org/
- EARS notation: https://alistairmavin.com/ears/
