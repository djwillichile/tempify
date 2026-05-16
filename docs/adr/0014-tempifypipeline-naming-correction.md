# ADR-0014: Corrección de nomenclatura de `tempifyPipeline` a `TempifyPipeline`

**Status:** Accepted
**Date:** 2026-05-16
**Decision-makers:** Guillermo Fuentes-Jaque

## Contexto

`steering/architecture.md` (Capa 5, Orquestación) introduce la clase orquestadora con el nombre `tempifyPipeline` (minúscula inicial). Esta nomenclatura entra en conflicto directo con `steering/conventions.md`, que establece **PascalCase para todas las clases** siguiendo PEP 8.

La incoherencia se ha propagado a las specs activas que referencian la clase:

- `specs/pipeline/requirements.md`
- `specs/cli/requirements.md`
- `specs/gui/requirements.md`

Dado que `steering/conventions.md` es un contrato vinculante del proyecto y la convención PEP 8 es estándar inamovible en el ecosistema Python, la divergencia debe resolverse antes de que el nombre se materialice en código de implementación. Corregirlo más tarde implicaría refactor transversal y churn innecesario en el historial de Git.

## Decisión

Renombrar la clase orquestadora de **`tempifyPipeline`** a **`TempifyPipeline`** en todas las referencias del proyecto:

- `steering/architecture.md` (Capa 5 y diagramas de flujo)
- `specs/pipeline/requirements.md`
- `specs/cli/requirements.md`
- `specs/gui/requirements.md`
- Código futuro (módulo `tempify.pipeline`)

El paquete (`tempify`) y el módulo (`tempify.pipeline`) **permanecen en lowercase**, conforme a PEP 8 para nombres de paquetes y módulos. La corrección afecta exclusivamente al símbolo de clase.

## Alternativas consideradas

### 1. Mantener `tempifyPipeline` y documentar una excepción a la convención

Rechazado. Documentar excepciones erosiona la regla y normaliza la negociación caso a caso de convenciones. PEP 8 no contempla camelCase para clases; aceptar la excepción introduciría una inconsistencia visible para cualquier colaborador familiarizado con el ecosistema Python.

### 2. Renombrar a `Pipeline` (sin prefijo)

Rechazado. El nombre es ambiguo dentro de un paquete que orquesta múltiples elementos (detectores, validadores, interpoladores, escritores). Un símbolo genérico `Pipeline` no contextualiza el dominio y colisiona conceptualmente con pipelines de bibliotecas externas (sklearn, Dask, Prefect) cuando aparezca en tracebacks o en imports.

### 3. `TempifyPipeline` (elegido)

Respeta PascalCase, contextualiza el dominio (cualquier traceback o IDE muestra inmediatamente la procedencia), y es trivialmente buscable en el código y la documentación. El prefijo `Tempify` es redundante con el paquete cuando se importa con `from tempify.pipeline import TempifyPipeline`, pero la redundancia se justifica por desambiguación y discoverabilidad.

## Consecuencias

### Positivas

- Coherencia restaurada entre `steering/conventions.md` y `steering/architecture.md`.
- Alineación con PEP 8: ningún lector futuro tropezará con la convención.
- Refactor barato: la corrección ocurre antes de cualquier implementación.

### Negativas

- Enmienda transversal obligatoria a `steering/architecture.md`, `specs/pipeline/requirements.md`, `specs/cli/requirements.md`, `specs/gui/requirements.md`.
- Las specs deben re-aprobarse si el cambio implica diff no trivial en su superficie pública.

### Sin impacto

- El nombre del paquete (`tempify`) y del módulo (`tempify.pipeline`) **no cambian**: PEP 8 mantiene lowercase para paquetes/módulos.
- No hay código de implementación afectado (las specs siguen en estado Draft).

## Referencias

- PEP 8 — Naming Conventions: https://peps.python.org/pep-0008/#naming-conventions
- `steering/conventions.md` — Sección de naming.
- `steering/architecture.md` — Capa 5 (Orquestación).
