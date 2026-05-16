# /spec-design

Genera el documento de diseño técnico para la spec activa, una vez aprobados los requirements.

## Pre-condiciones

- Existe `specs/<active>/requirements.md` con estado **Approved**.
- El usuario ha confirmado explícitamente la aprobación.

Si las pre-condiciones no se cumplen, **abortar** y pedir aprobación primero.

## Comportamiento

1. **Leer contexto completo:**
   - `CLAUDE.md`
   - `steering/architecture.md` (decisiones arquitectónicas vigentes)
   - `steering/tech.md` (stack tecnológico)
   - `specs/<active>/requirements.md` (lo que hay que diseñar)
   - Specs relacionadas si la actual depende de ellas.

2. **Proponer el diseño** en `specs/<active>/design.md`:
   - Visión técnica
   - Componentes nuevos y modificados
   - Contratos públicos (firmas de funciones/clases)
   - Modelos de datos (dataclasses, enums)
   - Algoritmos clave (descripción + pseudo-código si aplica)
   - Decisiones de diseño con alternativas consideradas
   - Estrategia de testing (unit, property-based, integration)
   - Trazabilidad requirements → design

3. **Identificar ADRs necesarios:**
   - Si alguna decisión es no trivial (afecta >1 spec, cambia arquitectura, agrega dependencia), proponer crear ADR en `docs/adr/NNNN-titulo.md`.

4. **Pedir aprobación humana** antes de avanzar a `/spec-tasks`.

## Restricciones

- **No** crear `tasks.md` ni `impl-log.md`.
- **No** escribir código de producción.
- **No** modificar `steering/` sin discusión explícita.

## Output esperado

1. `specs/<active>/design.md` generado.
2. Resumen de las decisiones clave para revisión humana.
3. Lista de ADRs propuestos (si corresponde).
4. Pregunta: "¿Apruebas el design para avanzar a /spec-tasks?"
