# /review

Ejecuta auto-revisión sobre una task implementada o sobre el estado actual del repo, antes de pedir review humana.

## Comportamiento

1. **Ejecutar checks técnicos:**
   ```bash
   ruff check src/ tests/
   ruff format --check src/ tests/
   mypy --strict src/
   pytest --cov=src/tempify --cov-report=term-missing
   ```

2. **Verificar contra spec:**
   - Leer la spec activa (`requirements.md`, `design.md`, `tasks.md`)
   - Comparar implementación actual contra criterios de aceptación
   - Identificar gaps

3. **Verificar trazabilidad:**
   - ¿Cada REQ de la spec tiene al menos un test?
   - ¿Cada componente de `design.md` está implementado?
   - ¿Cada task de `tasks.md` marcada como completada está realmente hecha?

4. **Verificar documentación:**
   - Toda función pública con docstring NumPy
   - CHANGELOG actualizado
   - `impl-log.md` actualizado

5. **Generar reporte estructurado:**
   ```
   ## Auto-review report
   
   ### Technical checks
   - Ruff: PASS / FAIL (detalles)
   - mypy: PASS / FAIL
   - Tests: N passing, M failing
   - Coverage: X.Y%
   
   ### Spec compliance
   - REQ-001: ✓ (test_xxx)
   - REQ-002: ✓ (test_yyy)
   - REQ-003: ⚠ Sin cobertura de test
   
   ### Documentation
   - CHANGELOG: ✓
   - impl-log.md: ✓
   - Docstrings: ⚠ 2 funciones públicas sin docstring
   
   ### Recomendación
   - [ ] Listo para review humana
   - [ ] Requiere ajustes antes de review (lista de ajustes)
   ```

## Restricciones

- **No** modificar código durante /review. Solo reportar.
- **No** marcar tasks como completadas si hay gaps.
