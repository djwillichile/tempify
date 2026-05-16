# Design — <Feature Name>

**Estado:** Draft | In Review | Approved
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** YYYY-MM-DD

## 1. Visión técnica

<Resumen de cómo se va a construir esto, en 1-2 párrafos.>

## 2. Arquitectura propuesta

### Diagrama de componentes

```
<ASCII diagram o referencia a docs/diagrams/>
```

### Componentes nuevos

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| `ClassName` | `src/tempify/<module>.py` | ... |

### Componentes modificados

| Componente | Ubicación | Cambio |
|---|---|---|
| `ExistingClass` | `src/tempify/<module>.py` | ... |

## 3. Contratos públicos (APIs)

### Función / clase 1

```python
def function_name(
    arg1: Type1,
    arg2: Type2,
    *,
    option: bool = False,
) -> ReturnType:
    """Docstring resumen."""
```

**Pre-condiciones:** ...
**Post-condiciones:** ...
**Excepciones lanzadas:** ...

## 4. Modelos de datos

### `DataClass1`

```python
@dataclass(frozen=True)
class DataClass1:
    field1: str
    field2: int
```

## 5. Algoritmos clave

### Algoritmo 1

<Descripción narrativa + pseudo-código si corresponde>

**Complejidad:** O(?)
**Trade-offs considerados:** ...

## 6. Decisiones de diseño

### Decisión 1: <título corto>

**Opciones consideradas:**
1. Opción A: ...
2. Opción B: ...

**Decisión:** Opción A
**Razón:** ...
**Trade-offs:** ...

> Si la decisión es no trivial, registrar como ADR separado en `docs/adr/`.

## 7. Estrategia de testing

### Tests unitarios

- `test_function_name_happy_path` — verifica camino normal
- `test_function_name_edge_case_X` — verifica caso límite X
- `test_function_name_error_Y` — verifica manejo de error Y

### Tests property-based (hypothesis)

- `test_invariant_Z` — propiedad: <descripción>

### Tests de integración

- `test_end_to_end_scenario_W` — flujo completo W

### Fixtures necesarios

- `synthetic_3x3_monthly.nc` — ya existe
- `<nuevo fixture>` — generar en setup

## 8. Plan de migración

<Si la feature modifica algo existente, cómo migrar usuarios actuales>

## 9. Métricas de calidad

| Métrica | Umbral |
|---|---|
| Coverage del módulo | ≥ 85% |
| Performance (input X) | < N segundos |
| Memoria peak (input X) | < M GB |

## 10. Trazabilidad requirements → design

| Requirement | Componente que lo implementa |
|---|---|
| REQ-001 | `function_name` |
| REQ-002 | `ClassName.method` |
| ... | ... |
