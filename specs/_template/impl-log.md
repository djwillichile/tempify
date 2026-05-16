# Implementation Log — <Feature Name>

**Tasks doc:** [tasks.md](tasks.md)

> Este log es mantenido por el agente durante la implementación.
> Cada sesión añade una entrada. No editar entradas anteriores, solo añadir nuevas.

---

## YYYY-MM-DD (sesión N) — <nombre opcional>

### Estado al inicio de la sesión

- Branch: `feature/...`
- Último commit: `<hash>` <subject>
- Tasks completadas previamente: task-1.1, task-1.2
- Tasks pendientes priorizadas: task-1.3, task-2.1

### Plan aprobado para esta sesión

- task-1.3: ...
- task-2.1: ...

### Ejecutado

#### task-1.3: <título>

- [x] Test añadido (commit `a1b2c3d`)
- [x] Implementación (commit `e4f5g6h`)
- [x] Refactor (commit `i7j8k9l`)
- [x] Coverage: 87.3% (delta: +2.1%)

**Decisiones tomadas:**
- Se eligió X en lugar de Y porque <razón>. Registrado en ADR-NNNN.

**Observaciones:**
- ...

### Bloqueado / por resolver

- task-2.1: depende de definir el contrato de DataclassZ; pendiente discusión con humano.

### Estado al cierre de la sesión

- Branch: `feature/...`
- Último commit: `<hash>` <subject>
- Tests: K pasan, 0 fallan
- Coverage global: X.Y%
- Próxima sesión: empezar por task-2.2

---
