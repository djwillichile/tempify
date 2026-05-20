# ADR-0010: Política unificada de tolerancia para conservación de la media mensual

**Status:** Accepted
**Date:** 2026-05-16
**Decision-makers:** Guillermo Fuentes-Jaque

## Contexto

La propiedad central de tempify (en su método estrella PCHIP+Rymes-Myers) es que la media mensual del output diario reconstruye exactamente la media mensual del input. "Exactamente" requiere, en aritmética de punto flotante, una tolerancia explícita. Hoy el proyecto declara tres tolerancias distintas en tres lugares distintos, todas nominalmente relacionadas con "conservación de la media mensual":

1. `1e-6` en `specs/core-interpolation/requirements.md` REQ-006, como criterio de convergencia del iterador Rymes-Myers (en unidades de la variable).
2. `1e-4` en `specs/validation/requirements.md` REQ-004, como criterio absoluto del post-validator que recibe el output ya producido.
3. `1e-4 °C` en `steering/product.md` como métrica de éxito v1.0, específica para temperatura.

La triplicación es problemática:

- **Ambigüedad semántica.** No es obvio si las tres tolerancias son "la misma cosa" expresada distinto o tres cosas conceptualmente distintas.
- **Ambigüedad de tipo.** No se aclara si son absolutas o relativas. Una tolerancia absoluta de `1e-4` es trivial para temperatura en °C pero inadecuada para radiación en `W m-2` o estricta de más para presión en Pa.
- **Sin enganche por variable.** Una sola tolerancia global no escala a un proyecto que aspira a manejar familias de variables con magnitudes muy distintas.
- **Riesgo de drift.** Si un módulo se actualiza y otro no, el contrato implícito al usuario se rompe silenciosamente.

Se requiere unificar la política y dejar trazable qué tolerancia rige cuándo y por qué.

## Decisión

Adoptar una **política de tres niveles**, donde cada nivel tiene un dueño claro, un valor por defecto explícito y un mecanismo de configuración bien delimitado. Los tres niveles no se contradicen: cada uno opera en una capa distinta del flujo, con un propósito distinto.

| Nivel | Quién | Valor por defecto | Tipo | Configurable |
|---|---|---|---|---|
| 1 | Iterator (Rymes-Myers) | `1e-6` | absoluta, unidades de la variable | sí, vía `PchipMeanPreservingInterpolator(convergence_tol=...)` |
| 2 | PostInterpolationValidator | `atol=1e-4`, `rtol=1e-6` | mixta (absoluta + relativa) | sí, vía `VariableProfile.acceptable_mean_error` |
| 3 | VariableProfile (YAML) | depende de la variable | absoluta, unidades de la variable | sí, en el perfil YAML del usuario |

### Nivel 1: tolerancia de convergencia del iterador Rymes-Myers

- **Dueño:** módulo `tempify.core.interpolation.pchip_mp` (el iterador).
- **Default:** `convergence_tol = 1e-6` en unidades de la variable.
- **Naturaleza:** criterio **interno** del algoritmo. Determina cuándo el bucle Rymes-Myers para de iterar.
- **No es** una garantía contractual al usuario. Es una decisión sobre cuándo el algoritmo declara "convergí".
- **Configurable** mediante el constructor del interpolador.

### Nivel 2: tolerancia contractual post-interpolación

- **Dueño:** módulo `tempify.validation.post.PostInterpolationValidator`.
- **Default:** `atol = 1e-4` y `rtol = 1e-6` aplicados como `|reconstructed - original| <= atol + rtol * |original|`.
- **Naturaleza:** **promesa al usuario**. El método se compromete a que la media mensual reconstruida del output coincide con la del input dentro de esta tolerancia.
- **Acción al fallar:** se emite WARNING en el `ValidationReport`; el procesamiento continúa. El fallo indica que el iterador no convergió suficientemente o que el método aplicado no es mean-preserving (lineal, PCHIP puro, Fourier sin restricción).
- **Configurable** indirectamente: el `PostValidator` consulta primero el `VariableProfile` (nivel 3); si éste no declara una tolerancia propia, cae al default del nivel 2.

### Nivel 3: tolerancia informativa por variable

- **Dueño:** archivos `variable-profile.yaml` (perfil de variable).
- **Default:** depende de la variable. Ejemplos:
  - temperatura (°C): `acceptable_mean_error: 1e-4`
  - precipitación (mm): `acceptable_mean_error: 0.1` (no aplica a métodos suaves, pero sí a un eventual módulo delta-method)
  - radiación (W m-2): `acceptable_mean_error: 1e-2`
- **Naturaleza:** criterio físicamente significativo, ajustado a la magnitud típica y al uso aceptado de la variable.
- **Configurable** por el usuario en su propio perfil YAML.

### Trazabilidad de las constantes

Las tres tolerancias se exponen como `Final` literales en un módulo central `tempify.constants`, no hard-coded en cada módulo:

```python
# tempify/constants.py
from typing import Final

RYMES_MYERS_CONVERGENCE_TOL: Final[float] = 1e-6
RYMES_MYERS_MAX_ITERATIONS: Final[int] = 50
POST_VALIDATION_ABS_TOL: Final[float] = 1e-4
POST_VALIDATION_REL_TOL: Final[float] = 1e-6
```

Cada módulo importa de ahí. Los perfiles YAML declaran su propia `acceptable_mean_error`. El `PostValidator` resuelve en orden: perfil → constantes.

## Alternativas consideradas

### Alternativa A: una sola tolerancia global

Definir un único `MEAN_PRESERVATION_TOL = 1e-6` y aplicarlo en todas partes.

**Rechazado.** No funciona para precipitación (escala mm, donde `1e-6` es ruido numérico irrelevante) ni para radiación (escala W m-2, donde `1e-6` es absurdamente estricto). Tampoco distingue el rol interno (convergencia) del rol contractual (validación), que son conceptualmente distintos.

### Alternativa B: tolerancia 100% relativa

Usar siempre `rtol * |original|` sin componente absoluta.

**Rechazado.** Se rompe para variables que pueden cruzar cero o estar cerca de cero (anomalías de temperatura, NDVI cerca de 0, balance de radiación nocturno). Una tolerancia relativa pura diverge cuando `|original| → 0`.

### Alternativa C: tolerancia única `atol + rtol`

Una sola dupla `(atol, rtol)` global, sin diferenciar convergencia interna vs. validación contractual.

**Rechazado.** Confunde dos contratos: el iterador necesita un criterio de parada (idealmente más estricto que la promesa al usuario, para tener margen); el validator necesita un criterio de auditoría. Mezclarlos hace que cambiar uno fuerce a cambiar el otro.

## Consecuencias

### Positivas

- Cada tolerancia tiene un dueño identificable y un propósito claro.
- El usuario puede ajustar la tolerancia contractual por variable sin tocar código.
- El equipo de desarrollo puede experimentar con el criterio de convergencia interno sin alterar la promesa al usuario.
- Las constantes viven en un solo lugar, fácil de auditar.

### Negativas

- Tres tolerancias requieren tres tests dedicados y tres entradas en la documentación.
- El orden de resolución (perfil → default) es una capa de indirección que el lector novato debe internalizar.

### Enmiendas requeridas

Esta ADR obliga a actualizar:

1. `specs/core-interpolation/requirements.md` REQ-006: aclarar que `1e-6` es la tolerancia de convergencia (nivel 1), no la garantía contractual.
2. `specs/validation/requirements.md` REQ-004: explicitar `atol=1e-4` y `rtol=1e-6`, y la resolución por perfil de variable.
3. `specs/_template/variable-profile.schema.yaml` (o equivalente): añadir el campo opcional `acceptable_mean_error: float`.
4. `steering/product.md`: aclarar que el `< 1e-4 °C` es el nivel 3 para temperatura, no una constante global.

## Notas de implementación

- Definir las constantes en `tempify/constants.py` como `Final[float]`. Importar desde allí en `pchip_mp.py`, `post_validator.py` y `variable_profile.py`.
- El `PostInterpolationValidator` recibe el `VariableProfile` resuelto al construirse; si el perfil declara `acceptable_mean_error`, ese valor sobreescribe `POST_VALIDATION_ABS_TOL` para esa ejecución.
- El `ValidationReport` debe registrar qué tolerancia se usó efectivamente (origen: perfil vs. default) para trazabilidad.
- Tests dedicados: `test_constants_immutable`, `test_postvalidator_uses_profile_tolerance_when_present`, `test_postvalidator_falls_back_to_default`, `test_rymes_myers_convergence_tol_independent_of_postvalidator`.

## Referencias

- Rymes, M. D., & Myers, D. R. (2001). Mean preserving algorithm for smoothly interpolating averaged data. *Solar Energy*, 71(4), 225-231.
- CF Conventions: https://cfconventions.org/
- ADR-0001: Use xarray.DataArray as central data abstraction (formato base de este ADR).
- `specs/core-interpolation/requirements.md` REQ-006.
- `specs/validation/requirements.md` REQ-004.
- `docs/methodology/precipitation.md` (contexto sobre por qué la tolerancia de nivel 3 es variable-específica).
