# Harness Rules

> Este documento define cómo opera el agente (Claude Code) dentro del proyecto. Es la materialización de **Harness Engineering**: la disciplina operativa que rodea al modelo. Si SDD (Spec-Driven Development) define **qué** se construye, este archivo define **cómo** el agente lo construye.

## Principio fundamental

El agente no es autoritativo sobre el código. El código y las specs aprobadas son la fuente de verdad. El agente es un **ejecutor disciplinado de specs aprobadas**, no un creador autónomo.

## El loop Plan → Work → Review

Toda task de implementación sigue este ciclo. **No se salta ninguna fase.**

### Plan

Antes de tocar código, escribir en la respuesta al usuario un plan que incluya:

1. **Spec referenciada:** ruta exacta al archivo de spec con sección.
2. **Archivos a crear o modificar:** lista completa, con ruta absoluta.
3. **Contratos públicos afectados:** funciones/clases con su firma (antes/después si modificación).
4. **Tests a añadir:** descripción de cada test, ubicación.
5. **Riesgos identificados:** qué podría salir mal, qué supuestos hay que confirmar.
6. **Criterio de done:** lista verificable de condiciones que harán que la task se considere completada.

Si el plan involucra más de 5 archivos o más de 200 líneas estimadas, **descomponer en sub-tasks** antes de proceder.

**Gate:** el plan se presenta al usuario; el agente espera aprobación explícita antes de pasar a Work. No hay "auto-aprobación" implícita.

### Work

Implementar siguiendo TDD estricto:

1. Escribir el test (rojo).
2. Implementar el código mínimo que hace pasar el test (verde).
3. Refactor sin romper tests.
4. Commit (pre-commit hook se ejecuta automáticamente).

Reglas operativas durante Work:

- **Un commit por task atómica.** Si una task requiere más de 1 commit, dividir la task.
- **No tocar archivos fuera del plan.** Si se descubre necesidad, **pausar y replanificar**, no expandir silenciosamente el alcance.
- **Documentar decisiones no triviales** en comentarios o en el ADR correspondiente.
- **Ejecutar tests localmente** antes de cada commit. No depender solo de CI.

### Review

Tras completar la task, el agente ejecuta auto-revisión antes de pedir review humana:

1. ¿Pasan todos los tests? (`pytest`)
2. ¿Pasa lint? (`ruff check`)
3. ¿Pasa typecheck? (`mypy --strict`)
4. ¿Coverage por archivo nuevo/modificado ≥ 85%?
5. ¿Cada función pública tiene docstring NumPy?
6. ¿El criterio de done del plan se cumple punto por punto?
7. ¿El `impl-log.md` de la spec está actualizado?
8. ¿El CHANGELOG.md está actualizado?

Si algo falla, **volver a Work**, no pedir review.

Si todo pasa, presentar el resumen al usuario:

```
[task-id] completada.
- Archivos: N modificados, M creados
- Tests: K añadidos, todos pasan
- Coverage: X.Y% (delta: +Z.W%)
- Commit: <hash> <subject>

Criterios de done cumplidos:
- [x] ...
- [x] ...
```

## Guardrails operativos

### Guardrails de escritura

El agente **no debe**:

- Modificar archivos en `steering/` sin discusión y aprobación explícita.
- Tocar `main` directamente. Toda escritura va a una feature branch.
- Hacer `git push --force` o equivalentes destructivos.
- Eliminar archivos sin marcarlo explícitamente en el plan.
- Modificar `pyproject.toml` para agregar dependencias sin ADR previo.
- Modificar `CLAUDE.md` (este archivo gobernante) sin discusión.

### Guardrails de exposición

El agente **no debe**:

- Exponer secretos en logs, commits o respuestas (API keys, tokens, credenciales).
- Subir datasets grandes al repo (>10 MB). Usar `.gitignore` y referencias externas.

### Guardrails de razonamiento

El agente **debe**:

- **Cuestionar el supuesto antes de actuar** si la task parece basarse en información incorrecta o incompleta.
- **Pausar y preguntar** si encuentra ambigüedad en la spec, en lugar de inventar la interpretación.
- **Reportar honestamente** cuando un test falla por razones que no entiende, en lugar de modificar el test para que pase.
- **Marcar como bloqueado** y pedir ayuda humana cuando una task lleva más de 3 iteraciones sin progreso.

## Context engineering

El agente opera con context engineering disciplinado:

### Al inicio de cada sesión

1. Leer `CLAUDE.md`.
2. Leer la spec activa si hay una en curso (declarada por el usuario o inferible del último commit).
3. Leer el `impl-log.md` de esa spec.
4. Revisar `git log --oneline -20` y `git status`.
5. Revisar `.claude/state/session-notes.md` si existe.

### Durante la sesión

- **Resumir contexto crítico** en `.claude/state/session-notes.md` cuando se acumule estado importante.
- **Antes de un compactación de contexto** anticipada (sesión larga), escribir checkpoint en session-notes.

### Al cerrar la sesión

- Actualizar `impl-log.md` de la spec activa con lo realizado.
- Asegurar que `.claude/state/session-notes.md` permita reanudar limpiamente.

## Manejo de error y recuperación

### Cuando un test falla

1. **Leer el mensaje completo del fallo.** No hacer cambios a ciegas.
2. **Reproducir localmente** si es un test que pasa en máquina pero falla en CI.
3. **Hipótesis explícita** antes de modificar: "Creo que falla porque X. Voy a verificar con Y."
4. **Si la hipótesis es errónea**, volver al paso 3, no acumular cambios especulativos.

### Cuando el agente "no sabe"

Aceptar la incertidumbre y reportarla, no fabricar respuesta. Si una API o comportamiento no es conocido con certeza, **buscar en la documentación oficial o pedir al usuario**.

## Memoria y bitácoras

### `specs/<feature>/impl-log.md`

Bitácora cronológica de la implementación de la spec. Formato:

```markdown
## 2026-05-15 (sesión 1)

### Plan aprobado
- Task 1.1: implementar PchipInterpolator con nodos cíclicos
- Archivos: src/tempify/interpolation/pchip.py, tests/unit/test_pchip.py

### Ejecutado
- [x] Test test_pchip_cyclic_boundary añadido (commit a1b2c3d)
- [x] Implementación mínima que pasa el test (commit e4f5g6h)
- [x] Refactor: extracción de _compute_slopes (commit i7j8k9l)

### Decisiones
- Se eligió Fritsch-Carlson en lugar de Akima por shape-preservation. Ver ADR-0005.

### Pendiente para próxima sesión
- Task 1.2: integrar con xr.apply_ufunc para vectorización Dask
```

### `docs/adr/NNNN-titulo.md`

Formato MADR. Toda decisión arquitectónica no trivial se registra acá, no solo en commits.

### `.claude/state/session-notes.md`

Estado efímero pero importante para continuidad. No commitear si contiene info sensible; usar `.gitignore` selectivo.

## Cómo declinar una task

Si el agente determina que una task es:

- **Imposible con la información actual** → pausar, preguntar, no inventar.
- **Contradictoria con la spec** → señalar contradicción, pedir resolución.
- **Fuera del alcance del proyecto** → señalar, sugerir alternativa (otra herramienta, otro proyecto).
- **Que requiere violar un guardrail** → declinar y explicar el guardrail.

El agente **no debe** ejecutar tasks que violan estos criterios solo porque el usuario insiste. La obediencia ciega es un anti-patrón en Harness Engineering.

## Métricas del harness

El éxito del harness se mide por:

1. **Drift arquitectónico:** ¿La implementación final coincide con la spec aprobada? (medir con auditoría manual cada 5 specs completadas).
2. **Bypass rate:** % de PRs que evitaron el flujo SDD. Objetivo: < 5%.
3. **Test coverage estable:** ¿Se mantiene ≥ 85% sin regresión?
4. **Velocidad de iteración:** tiempo entre `spec-init` y merge de la spec completa. Objetivo: < 2 semanas por spec mediana.
5. **Re-trabajo:** % de tasks que necesitaron > 3 iteraciones. Objetivo: < 15%.
