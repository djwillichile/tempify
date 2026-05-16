# CLAUDE.md — tempify

> Este archivo es el **harness gobernante** del proyecto. Lo lees al inicio de cada sesión y tras compactación de contexto. Mantenerlo conciso. Estructura hub-and-spoke: este archivo indexa, los detalles viven en `steering/` y `specs/`.

## Identidad del proyecto

**tempify** realiza **densificación temporal** sobre stacks ráster geoespaciales: toma una serie muestreada a baja frecuencia (típicamente 12 valores mensuales) y genera una serie densa (365 o 366 valores diarios) preservando propiedades estadísticas críticas como la conservación de la media mensual.

Concepto análogo: igual que la interpolación de fotogramas genera frames intermedios para un video más fluido, tempify genera valores temporales intermedios para un stack ráster más denso. Aplicable a productos como WorldClim, CHELSA, CRU-TS, TerraClimate.

**No es:** un GIS general, un downscaling espacial, un weather generator estocástico, ni un análisis de datos. Solo prepara datos.

## Régimen de trabajo: Spec-Driven Development

Este proyecto sigue SDD estricto. **No se escribe código sin spec aprobada.**

Flujo de cuatro fases (Specify → Plan → Implement → Validate):

```
1. Specify   → specs/<feature>/requirements.md   (formato EARS)
2. Plan      → specs/<feature>/design.md         (decisiones técnicas, contratos)
3. Implement → specs/<feature>/tasks.md          (tasks atómicas verificables)
4. Validate  → tests + specs/<feature>/impl-log.md
```

Cada fase tiene un **gate de aprobación humana** antes de avanzar a la siguiente. No saltarse fases.

Plantillas en `specs/_template/`. Specs activas indexadas más abajo.

## Loop de ejecución (Harness Engineering)

Para toda task de implementación, seguir el ciclo **Plan → Work → Review**:

1. **Plan.** Antes de tocar código, leer la spec relevante, declarar archivos a modificar, riesgos, y criterio de "done". Si el plan tiene > 5 archivos o > 200 líneas estimadas, descomponer en sub-tasks.
2. **Work.** Implementar siguiendo TDD: test primero, código mínimo, refactor. Commits frecuentes (uno por task atómica).
3. **Review.** Auto-revisar contra criterios de aceptación de la spec. Ejecutar lint + typecheck + tests. Solo entonces solicitar revisión humana.

Este loop se repite por cada task. **No combinar tasks.**

## Specs activas

| Spec | Estado | Descripción |
|------|--------|-------------|
| [core-interpolation](specs/core-interpolation/requirements.md) | Draft | 4 métodos de interpolación temporal (Lineal, PCHIP, PCHIP+RM, Fourier) |
| [structure-detection](specs/structure-detection/requirements.md) | Draft | Detección stack único vs colección de monocapas |
| [temporal-frequency-resolver](specs/temporal-frequency-resolver/requirements.md) | Draft | Inferencia de frecuencia (CF → nomenclatura → heurística → prompt) |
| [io-handlers](specs/io-handlers/requirements.md) | Draft | Lectores y escritores (GeoTIFF, NetCDF, Zarr) |
| [validation](specs/validation/requirements.md) | Draft | Coherencia geoespacial + post-interpolación |
| [cli](specs/cli/requirements.md) | Draft | Interfaz de línea de comandos |

## Steering: contexto persistente (leer antes de cualquier task)

- [Product](steering/product.md) — Audiencia, casos de uso, no-objetivos
- [Tech stack](steering/tech.md) — Python 3.11+, xarray, Dask, rioxarray
- [Architecture](steering/architecture.md) — 5 capas, contratos entre capas
- [Conventions](steering/conventions.md) — Code style, naming, testing, commits
- [Harness rules](steering/harness.md) — Guardrails operativos del agente

## Guardrails duros (no negociables)

Estos son los guardrails que el harness enforza. Violar uno aborta la task.

1. **No commits sin tests.** Cobertura mínima por módulo: 85%.
2. **No dependencias nuevas sin ADR.** Discutir antes en `docs/adr/`.
3. **Toda función pública con docstring NumPy + type hints.**
4. **No bypassear SDD.** Cambios requieren actualizar la spec primero.
5. **Precipitación nunca se interpola con métodos suaves.** El perfil de variable lo rechaza. Ver [methodology/precipitation.md](docs/methodology/precipitation.md).
6. **Reproducibilidad bit-exact.** Mismos inputs + parámetros = mismo output.
7. **No mutar archivos en `steering/` sin discusión.** Son contratos del proyecto.
8. **No tocar `main` directamente.** Toda PR vía feature branch.

## Memoria entre sesiones

- `specs/<feature>/impl-log.md` — bitácora cronológica de la implementación.
- `docs/adr/NNNN-*.md` — decisiones arquitectónicas registradas.
- `.claude/state/session-notes.md` — notas operativas de la sesión actual.

**Al iniciar sesión:**
1. Leer este archivo (`CLAUDE.md`)
2. Leer la spec activa (si hay una en curso)
3. Leer su `impl-log.md`
4. Revisar `git log --oneline -20` para entender estado del repo

## Hooks (`.claude/hooks/`)

Scripts que el harness ejecuta automáticamente en eventos:

- `pre-commit.sh` — lint + typecheck + tests rápidos
- `pre-task.sh` — verifica que la spec esté aprobada antes de implementar
- `post-task.sh` — actualiza `impl-log.md` y CHANGELOG

## Slash commands custom (`.claude/commands/`)

- `/spec-init <name>` — inicializa una nueva spec desde plantilla
- `/spec-requirements` — genera `requirements.md` (formato EARS)
- `/spec-design` — genera `design.md` tras aprobar requirements
- `/spec-tasks` — descompone en tasks atómicas
- `/impl <task-id>` — implementa una task con loop Plan-Work-Review
- `/review` — auto-revisión contra spec antes de pedir review humano

## Comunicación con el usuario

- **Idioma:** español (técnico, riguroso, sin generalidades vacías).
- **Código y comentarios técnicos:** inglés.
- **Cuestionar supuestos cuando corresponda.** Pushback constructivo es valorado.
- **No usar em dashes.** Usar comas y paréntesis para énfasis.
- **Estructura preferida en reportes técnicos:** requisitos → análisis comparativo → justificación técnico-económica.

## Referencias externas

- Spec-Driven Development (GitHub spec-kit): https://github.com/github/spec-kit
- Harness Engineering (OpenAI Skills): https://github.com/openai/skill-harness-engineering
- EARS notation: https://alistairmavin.com/ears/
- CF-conventions: https://cfconventions.org/
- Hipótesis del harness: contratos explícitos entre humano y agente reducen drift arquitectónico.
