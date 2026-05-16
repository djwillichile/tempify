# /spec-tasks

Descompone el design aprobado en tasks atómicas verificables, listas para implementación.

## Pre-condiciones

- Existe `specs/<active>/design.md` con estado **Approved**.

## Comportamiento

1. **Leer `design.md` y `requirements.md`** de la spec activa.

2. **Descomponer en fases y tasks:**
   - Fase 1: Fundamentos (tests esqueleto, interfaces base)
   - Fase 2: Implementación incremental por componente
   - Fase 3: Integración, documentación, tutorial

3. **Cada task debe ser:**
   - Atómica (1 sesión, 1 commit)
   - Verificable (criterio de done observable)
   - Tipada (test | impl | refactor | docs | chore)
   - Estimada en horas

4. **Establecer orden de dependencias** entre tasks.

5. **Pedir aprobación humana** antes de avanzar a `/impl`.

## Heurísticas para tamaño de task

- Si una task estimada > 4h → dividir.
- Si una task toca > 3 archivos no relacionados → dividir.
- Si una task no tiene criterio de done verificable → reformular.

## Output esperado

1. `specs/<active>/tasks.md` generado.
2. Tabla resumen: # tasks por fase, estimación total.
3. Identificación de tasks críticas (path crítico).
4. Pregunta: "¿Apruebas el plan de tasks para empezar /impl?"
