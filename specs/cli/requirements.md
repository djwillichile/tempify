# Requirements — cli

**Estado:** Draft
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-15
**Última actualización:** 2026-05-15

## 1. Propósito

Proveer una interfaz de línea de comandos ergonómica que invoque las funcionalidades del API sin duplicar lógica de negocio. Soportar prompts interactivos cuando la detección automática falla.

## 2. Alcance

### In-scope

- Comandos: `convert`, `inspect`, `validate`, `profiles`, `version`.
- Prompts interactivos en español para resolver ambigüedades.
- Output formateado con `rich` (tablas, progress bars, color).
- Mensajes de error con código de error referenciable.

### Out-of-scope

- Lógica de negocio (toda en el pipeline / domain layers).
- Interfaz gráfica (diferida a Fase 4).

## 3. Actores y casos de uso

### Actor: Usuario que no programa en Python pero necesita ejecutar conversiones puntuales.

**Caso de uso típico:** Usuario ejecuta `tempify convert ./worldclim_chile/ --method pchip_mp --output ./out.nc` y recibe progress bar + reporte final.

## 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL expose a `tempify` command with subcommands `convert`, `inspect`, `validate`, `profiles`, and `version`.

### REQ-002 (Event-driven)

WHEN `convert` is invoked, THE SYSTEM SHALL display a progress bar showing percentage of pixels processed.

### REQ-003 (State-driven)

WHILE running interactively, THE SYSTEM SHALL prompt the user for any ambiguity that cannot be resolved automatically (e.g., unknown temporal frequency).

### REQ-004 (Event-driven)

WHEN running non-interactively (no TTY), THE SYSTEM SHALL fail with `InteractiveRequiredError` rather than blocking on a prompt.

### REQ-005 (Optional)

WHERE the user passes `--report path.md`, THE SYSTEM SHALL write the processing report to that file in Markdown format.

### REQ-006 (Ubiquitous)

THE SYSTEM SHALL exit with code 0 on success, 1 on validation failure, 2 on user cancellation, 3 on internal error.

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
