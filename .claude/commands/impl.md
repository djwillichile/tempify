# /impl <task-id>

Implementa una task específica siguiendo el loop **Plan → Work → Review** del harness.

## Pre-condiciones

- Existe `specs/<active>/tasks.md` con estado **Approved**.
- La task referenciada existe en `tasks.md`.
- La task no está marcada como completada.
- Las tasks que la bloquean están completadas.

Si alguna pre-condición falla, **abortar** con explicación.

## Comportamiento — Fase Plan

1. **Cargar contexto:**
   - `CLAUDE.md`
   - `steering/harness.md` (reglas operativas)
   - `specs/<active>/requirements.md`, `design.md`, `tasks.md`
   - `specs/<active>/impl-log.md` (qué se hizo antes)
   - Estado actual del repo: `git status`, `git log --oneline -10`

2. **Generar plan detallado** y presentarlo al usuario:
   - Spec referenciada (con sección exacta)
   - Archivos a crear/modificar (rutas absolutas)
   - Contratos públicos afectados (firmas antes/después)
   - Tests a añadir (con descripciones)
   - Riesgos identificados
   - Criterio de done verificable

3. **Esperar aprobación explícita** del plan. **No pasar a Work sin aprobación.**

## Comportamiento — Fase Work

Solo tras aprobación del plan:

1. **TDD estricto:**
   - Test rojo
   - Implementación mínima → test verde
   - Refactor sin romper tests
   - Commit con Conventional Commits

2. **Reglas operativas:**
   - Un commit por task atómica.
   - No tocar archivos fuera del plan. Si surge necesidad, **pausar y replanificar**.
   - Documentar decisiones no triviales en el commit body o en ADR.
   - Ejecutar tests localmente antes de cada commit (pre-commit hook lo verifica).

## Comportamiento — Fase Review

Tras completar la implementación:

1. **Auto-revisión:**
   - [ ] `pytest` pasa
   - [ ] `ruff check` pasa
   - [ ] `mypy --strict` pasa
   - [ ] Coverage por archivo nuevo/modificado >= 85%
   - [ ] Toda función pública tiene docstring NumPy
   - [ ] Criterio de done del plan se cumple punto por punto

2. **Actualizar bitácora:**
   - Añadir entrada en `specs/<active>/impl-log.md` describiendo:
     - Plan ejecutado
     - Commits realizados (con hashes)
     - Decisiones tomadas
     - Observaciones / lecciones
   - Marcar la task como completada en `tasks.md`

3. **Actualizar CHANGELOG.md** con la línea correspondiente bajo `[Unreleased]`.

4. **Presentar al usuario un resumen** para review humana final:
   ```
   [task-id] completada.
   Archivos: N modificados, M creados
   Tests: K añadidos, todos pasan
   Coverage: X.Y% (delta: +Z.W%)
   Commits: <hash1> <hash2>
   
   Criterios de done:
   - [x] ...
   - [x] ...
   
   ¿Apruebas el resultado o necesitas ajustes?
   ```

## Guardrails durante /impl

El agente **debe**:

- Pausar y preguntar si la spec resulta ambigua durante implementación.
- Reportar fallos de tests honestamente, no modificar tests para hacerlos pasar.
- Marcar la task como bloqueada si lleva >3 iteraciones sin progreso.

El agente **no debe**:

- Expandir silenciosamente el alcance.
- Tocar archivos fuera del plan aprobado.
- Hacer push a `main`.
- Modificar `steering/` o `CLAUDE.md`.
- Hacer commits sin que pasen lint/typecheck/tests.

## Output esperado

Una secuencia ordenada de:

1. Plan presentado para aprobación.
2. (tras aprobar) Commits ejecutados con mensajes claros.
3. Auto-review checklist.
4. Resumen final para review humana.
