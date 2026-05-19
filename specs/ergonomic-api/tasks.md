# Tasks — Ergonomic API (tipo terra)

**Estado:** Approved
**Design doc:** [design.md](design.md)
**Última actualización:** 2026-05-18

## Fase 1: Tests primero (TDD)

### task-1.1: Skeleton de tests

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.1
**Bloqueada por:** —

**Descripción:** Crear `tests/unit/test_api.py` con todos los tests enumerados
en el design (stub con `pytest.mark.skip` o cuerpo mínimo que falla). Añadir
fixture `synthetic_monthly_geotiff` en conftest.

**Criterio de done:**
- [ ] Archivo existe con 14 funciones de test
- [ ] Fixture crea un GeoTIFF de 12 bandas 4×4 px válido
- [ ] `pytest tests/unit/test_api.py --collect-only` lista los 14 tests sin error de import

**Archivos:**
- `tests/unit/test_api.py`
- `tests/conftest.py` (o `tests/unit/conftest.py`)

## Fase 2: Implementación (un commit por task)

### task-2.1: `TempifyRast` + `rast()`

**Tipo:** impl
**Estimación:** 1.5h
**Bloquea:** task-2.2, task-2.3
**Bloqueada por:** task-1.1

**Descripción:** Implementar la clase `TempifyRast` y la función `rast()` en
`src/tempify/api.py`. `TempifyRast.__repr__` usa `raster_info()` de `utils.py`
con captura de stdout. `rast()` usa `GeoTIFFReader`.

**Criterio de done:**
- [ ] Tests `test_rast_*` y `test_repr_*` y `test_str_*` pasan (verde)
- [ ] `r.data is da` (identidad, sin copia)
- [ ] `mypy --strict src/tempify/api.py` sin errores en este módulo
- [ ] `ruff check src/tempify/api.py` limpio

**Archivos:**
- `src/tempify/api.py`

### task-2.2: `plot()`

**Tipo:** impl
**Estimación:** 1.5h
**Bloquea:** task-2.4
**Bloqueada por:** task-2.1

**Descripción:** Implementar `plot()` con layout automático, soporte de `sub`
1-based, recorte silencioso si `sub` excede bandas, colorbar global. Usar
backend `Agg` en tests.

**Criterio de done:**
- [ ] Tests `test_plot_*` pasan
- [ ] `plot(r)` con 12 bandas genera grilla 3×4
- [ ] `plot(r, sub=range(1,17))` con stack diario genera grilla 4×4
- [ ] No lanza si `sub=range(1, 1000)`

**Archivos:**
- `src/tempify/api.py`

### task-2.3: `tempify()` función

**Tipo:** impl
**Estimación:** 2h
**Bloquea:** task-2.4
**Bloqueada por:** task-2.1

**Descripción:** Implementar `tempify()`: renombrar `band`→`month`, asignar
coords, construir `TemporalAxis`, despachar al interpolador correcto, envolver
resultado en `TempifyRast`. Validar nombre de método.

**Criterio de done:**
- [ ] Tests `test_tempify_*` pasan
- [ ] Resultado tiene `dim=time` con 365 o 366 pasos para `to_freq="daily"`
- [ ] `ValueError` con mensaje útil para método desconocido
- [ ] `mypy` y `ruff` limpios

**Archivos:**
- `src/tempify/api.py`

### task-2.4: Exportaciones en `__init__.py`

**Tipo:** chore
**Estimación:** 0.25h
**Bloquea:** task-2.5
**Bloqueada por:** task-2.2, task-2.3

**Descripción:** Agregar imports y `__all__` en `src/tempify/__init__.py`.

**Criterio de done:**
- [ ] `test_import_toplevel` pasa
- [ ] `from tempify import rast, tempify, plot` funciona
- [ ] `test_full_workflow_seven_lines` pasa

**Archivos:**
- `src/tempify/__init__.py`

## Fase 3: Cierre y documentación

### task-3.1: Cobertura y lint completo

**Tipo:** chore
**Estimación:** 0.5h
**Bloqueada por:** task-2.4

**Descripción:** Verificar cobertura ≥ 85% en `api.py`, correr `ruff`, `mypy`,
`pytest` completo. Ajustar tests si hay gaps.

**Criterio de done:**
- [ ] `pytest --cov=tempify.api tests/unit/test_api.py` muestra ≥ 85%
- [ ] Suite completa sin regresiones

**Archivos:**
- `tests/unit/test_api.py`

### task-3.2: Bump versión a 0.1.6 + CHANGELOG

**Tipo:** chore
**Estimación:** 0.25h
**Bloqueada por:** task-3.1

**Descripción:** Actualizar versión y CHANGELOG.

**Criterio de done:**
- [ ] `tempify.__version__ == "0.1.6"` en Python
- [ ] `pyproject.toml` versión = `"0.1.6"`
- [ ] CHANGELOG tiene sección `[0.1.6]` con descripción de la feature

**Archivos:**
- `src/tempify/__init__.py`
- `pyproject.toml`
- `CHANGELOG.md`

## Resumen

| Fase | # tasks | Estimación total |
|---|---|---|
| Fase 1 | 1 | 1h |
| Fase 2 | 4 | 5.25h |
| Fase 3 | 2 | 0.75h |
| **Total** | **7** | **~7h** |
