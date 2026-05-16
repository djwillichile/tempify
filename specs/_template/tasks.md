# Tasks — <Feature Name>

**Estado:** Draft | Approved | In Progress | Complete
**Design doc:** [design.md](design.md)
**Última actualización:** YYYY-MM-DD

## Reglas para tasks

Cada task debe ser:

- **Atómica:** completable en una sesión, un commit.
- **Verificable:** tiene un criterio de done observable.
- **Independiente** (en lo posible): no depende de tasks no iniciadas.
- **Estimada:** rough estimate en horas o líneas de código.

Formato de cada task:

```
### task-N.M: <título corto>

**Tipo:** test | impl | refactor | docs | chore
**Estimación:** <horas>h
**Bloquea:** task-X.Y, task-X.Z
**Bloqueada por:** task-W.V

**Descripción:** ...
**Criterio de done:**
- [ ] ...
- [ ] ...
**Archivos:**
- `path/to/file.py`
- `tests/unit/test_file.py`
```

## Fase 1: Fundamentos

### task-1.1: <título>

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-1.2
**Bloqueada por:** —

**Descripción:** Escribir test esqueleto para <X>.

**Criterio de done:**
- [ ] Test creado, falla con TODO en implementación
- [ ] Coverage report identifica el módulo target

**Archivos:**
- `tests/unit/test_module.py`

### task-1.2: <título>

**Tipo:** impl
**Estimación:** 2h
**Bloquea:** task-1.3
**Bloqueada por:** task-1.1

**Descripción:** Implementar la funcionalidad mínima que hace pasar el test de task-1.1.

**Criterio de done:**
- [ ] Test pasa (verde)
- [ ] mypy --strict pasa
- [ ] ruff pasa
- [ ] Docstring NumPy completo

**Archivos:**
- `src/tempify/module.py`

## Fase 2: <nombre>

### task-2.1: ...

## Fase 3: Documentación e integración

### task-3.1: Tutorial

**Tipo:** docs
**Estimación:** 2h

**Descripción:** ...

**Criterio de done:**
- [ ] Notebook ejecuta end-to-end sin errores
- [ ] Incluido en `docs/tutorials/`
- [ ] Enlazado desde README

**Archivos:**
- `docs/tutorials/<nombre>.ipynb`

## Resumen

| Fase | # tasks | Estimación total |
|---|---|---|
| Fase 1 | N | Xh |
| Fase 2 | M | Yh |
| Fase 3 | K | Zh |
| **Total** | | **Xh + Yh + Zh** |
