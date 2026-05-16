# /spec-init <feature-name>

Inicializa una nueva spec siguiendo la convención SDD del proyecto.

## Comportamiento

Cuando el usuario invoca `/spec-init <feature-name>`:

1. **Validar el nombre:**
   - Solo lowercase + guiones
   - No debe existir ya en `specs/`
   - Debe ser descriptivo (>2 chars, <40 chars)

2. **Copiar la plantilla:**
   ```bash
   cp -r specs/_template specs/<feature-name>
   ```

3. **Actualizar la tabla de specs activas** en `CLAUDE.md`:
   - Añadir una fila con estado "Draft"
   - Mantener orden alfabético

4. **Iniciar la fase Specify:**
   - Leer los steering documents (product, architecture)
   - Hacer preguntas al usuario para llenar `requirements.md`:
     - ¿Cuál es el propósito de la feature?
     - ¿Quiénes son los actores?
     - ¿Qué está in-scope y out-of-scope?
     - ¿Hay specs relacionadas que la bloqueen o dependan?
   - Generar el primer draft de `requirements.md` con los requisitos en formato EARS.

5. **Pedir aprobación humana** antes de avanzar a `/spec-design`.

## Restricciones

- **No** crear `design.md`, `tasks.md`, o `impl-log.md` en este paso. Solo `requirements.md`.
- **No** escribir código.
- **No** modificar otros archivos del repo más allá de los listados arriba.

## Output esperado

Después de ejecutar `/spec-init <feature>`, el agente presenta al usuario:

1. Confirmación de que la carpeta `specs/<feature>/` fue creada.
2. El contenido propuesto de `requirements.md` para revisión.
3. Pregunta explícita: "¿Apruebas los requirements para avanzar a /spec-design, o quieres ajustar algo?"
