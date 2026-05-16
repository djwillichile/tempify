# ADR-0017: Extensibilidad para métodos basados en redes neuronales

**Estado:** Deferred (v0.1.0) → planificación formal para v0.2.0
**Fecha:** 2026-05-16
**Deciders:** Guillermo Fuentes-Jaque
**Contexto técnico:** core-interpolation (extensibilidad futura)

## Contexto

El estado del arte 2023-2026 en interpolación climatológica incluye modelos basados en redes neuronales pre-entrenados como **ClimaX** (Microsoft Research, 2023), **Pangu-Weather** (Huawei, 2023), **GraphCast** (DeepMind, 2023), **FourCastNet** (NVIDIA, 2022) y modelos de **time-series transformers** (PatchTST, TimesNet). Estos modelos pueden:

1. Generar varianza sinóptica diaria realista (lo que los métodos suaves de v0.1.0 **no pueden** por construcción, ver supuesto en `core-interpolation/requirements.md` §7).
2. Capturar correlaciones espaciales y multi-variables que las interpolaciones puramente temporales pierden.
3. Aprender patrones climatológicos regionales sin requerir parametrización manual.

El usuario ha planteado la pregunta legítima: "¿se puede agregar como método de interpolación alguna red neuronal pre-entrenada?". La respuesta es **sí**, pero la integración tiene costos no triviales que justifican diferirla a v0.2.0 mientras se preserva la extensibilidad arquitectónica.

## Decisión

1. **v0.1.0 NO incluye `NeuralInterpolator`.** Out-of-scope explícito en `core-interpolation/requirements.md`.
2. **v0.1.0 garantiza extensibilidad.** La clase `BaseInterpolator` (`tempify.interpolation.base`) es un ABC público con contrato estable. Cualquier subclase concreta que implemente `interpolate(source, target_axis, *, cyclic, wraparound, nan_policy, chunk_size) -> xr.DataArray` puede integrarse sin tocar el pipeline.
3. **v0.2.0 introduce spec dedicada** `specs/neural-interpolation/` con sus propios `requirements.md`, `design.md`, `tasks.md`, siguiendo el mismo flujo SDD.
4. **Hook documentado:** la sección de extensibilidad de `core-interpolation/design.md` cita este ADR y declara que el ABC es deliberadamente abierto para implementaciones externas (terceros pueden distribuir `tempify_climax` o similar via entry points).

## Plan formal para v0.2.0

Cuando se aborde, la spec `neural-interpolation` debe cubrir al menos:

### Alcance v0.2.0

- **Adapter para ≥1 modelo público con licencia compatible.** Candidatos prioritarios: ClimaX (MIT), Pangu-Weather (BSD-3), FourCastNet (BSD-3). GraphCast (Apache-2.0 con cláusulas) requiere revisión legal antes.
- **Cache local de pesos** en `~/.cache/tempify/models/<model_id>/` con verificación SHA256 contra manifest versionado.
- **Detección automática GPU/CPU** con fallback transparente. GPU es opcional (extra `tempify[neural-gpu]`), CPU es default.
- **Modo `hybrid`**: el método clásico (Linear/PCHIP/RM/Fourier) genera la baseline mean-preserving, y el NN añade la varianza diaria sintética encima. Este modo combina lo mejor de ambos enfoques y es el más defendible científicamente.

### Out-of-scope v0.2.0

- Entrenamiento desde cero (sería v0.3.0).
- Fine-tuning de modelos pre-entrenados.
- Modelos propietarios que requieran licencia comercial.
- Modelos que no acepten 12 valores mensuales como input (lo cual descarta varios forecasting models que esperan inicialización horaria/sinóptica).

### Contrato técnico del adapter

```python
# Bosquejo, no canonical hasta spec aprobada en v0.2.0
class NeuralInterpolator(BaseInterpolator):
    name: ClassVar[str] = "neural"
    wraparound_stamp_on: ClassVar[str] = "neural_implicit"

    def __init__(
        self,
        model: Literal["climax-base", "climax-large", "pangu-1h", "custom"] = "climax-base",
        device: Literal["cpu", "cuda", "auto"] = "auto",
        hybrid_baseline: Literal["pchip_mp", "fourier", None] = "pchip_mp",
        weights_dir: Path | None = None,
        deterministic: bool = True,
    ) -> None: ...

    def interpolate(
        self,
        source: xr.DataArray,
        target_axis: TemporalAxis,
        *,
        cyclic: bool = True,
        wraparound: bool | None = None,
        nan_policy: NanPolicy = "raise",
        chunk_size: int | None = None,
    ) -> xr.DataArray: ...
```

El `attrs` del output deberá incluir:
- `tempify_neural_model` (model id + version).
- `tempify_neural_weights_sha256`.
- `tempify_neural_device` (cpu/cuda).
- `tempify_neural_hybrid_baseline` (si aplica).
- `tempify_neural_deterministic` (bool).

### Dependencias nuevas (extras opcionales)

- `tempify[neural]`: `torch>=2.4` o `jax>=0.4`, `huggingface_hub>=0.20`, `safetensors>=0.4`.
- `tempify[neural-gpu]`: variante con `torch[cu121]` o equivalente.
- Cada extra agrega ~1-2 GB al footprint. Por eso son **opcionales** y NO afectan al instalador `.exe` v0.1.0 (que sigue siendo <300 MB per ADR-0006).

### ADRs derivados que abrirá v0.2.0

- ADR-0018: política de selección del primer modelo (cuál implementar primero).
- ADR-0019: estrategia de cache y versionado de pesos.
- ADR-0020: modo hybrid vs neural-only (decisión final del default).
- ADR-0021: política de reproducibilidad en modo neural (afecta a ADR-0007).

## Alternativas consideradas

| Alternativa | Razón de rechazo en v0.1.0 |
|---|---|
| Implementar NN ahora en v0.1.0 | Footprint, complejidad de packaging, riesgo de licencia, tiempo de validación científica. v0.1.0 perdería su característica clave de "instalación ligera y reproducible". |
| Hacer NN sea un plugin externo (`pip install tempify-neural` separado) | Posible y deseable a largo plazo. v0.2.0 lo evaluará. Pero antes hay que cerrar el contrato del ABC y la spec. |
| Stub vacío en v0.1.0 sin implementación real | Mala UX (usuario llama método y obtiene NotImplementedError). Mejor declarar out-of-scope claramente. |
| Solo herramienta de comparación (no método propio) | Subutiliza el potencial. La spec v0.2.0 lo evaluará como modo `--neural-compare` opcional, pero el método neural primario es más valioso. |

## Consecuencias

### Positivas

- **v0.1.0 se mantiene focused** en el caso de uso reproducible y científicamente validado.
- **API publica estable**: `BaseInterpolator` no cambia entre v0.1.0 y v0.2.0; usuarios que extiendan localmente con su propio adapter NN pueden hacerlo desde hoy sin esperar a tempify.
- **Camino claro para v0.2.0** documentado por adelantado.
- **Cero costo de mantenimiento adicional en v0.1.0**.

### Negativas

- **Diferimos un feature valioso** que algunos usuarios pedirían en v0.1.0. Mitigado por documentación explícita del roadmap.
- **El "supuesto" actual** en `core-interpolation/requirements.md` §7 ("ningún método mensual→diario puede recuperar la varianza sinóptica diaria real") queda **superado conceptualmente** en v0.2.0 con NNs. Requerirá actualización del supuesto cuando se cierre la nueva spec.

### Riesgos para v0.2.0

- **Drift del ABC**: si entre v0.1.0 y v0.2.0 el contrato `interpolate(...)` cambia (e.g., nuevos parámetros), los plugins externos rompen. Mitigación: marcar `BaseInterpolator.interpolate` como API pública estable con SemVer fuerte; cambios breaking solo en major bump (v1.0.0).
- **Licencia de modelos**: GraphCast (Apache-2.0 con cláusulas específicas) requiere revisión legal cuidadosa antes de redistribuir o documentar como soportado.
- **Determinismo**: NNs con float32 + GPU rompen el bit-exact de ADR-0007. v0.2.0 deberá decidir si el modo strict reproducibility es alcanzable o si neural quedará fuera de esa garantía.

## Notas para v0.2.0

Cuando se aborde la spec `neural-interpolation`:

1. Empezar por `/spec-init neural-interpolation` siguiendo el flujo SDD ya establecido.
2. Inventariar modelos candidatos en `docs/methodology/neural-models-survey.md` con licencia, tamaño, performance esperado.
3. Decidir entre `NeuralInterpolator` como subclase única configurable vs varias subclases (`ClimaXInterpolator`, `PanguInterpolator`, etc.). Recomendación: una sola subclase con parámetro `model` (más cercano al patrón actual de `FourierInterpolator(n_harmonics=N)`).
4. Validar contra ground truth real (datos reanálisis ERA5 horario re-agregado a diario) antes de declarar la spec completa.

## Referencias

- Nguyen, T., et al. (2023). *ClimaX: A foundation model for weather and climate*. arXiv:2301.10343.
- Bi, K., et al. (2023). *Accurate medium-range global weather forecasting with 3D neural networks*. Nature 619, 533–538.
- Lam, R., et al. (2023). *Learning skillful medium-range global weather forecasting*. Science 382, 1416–1421.
- Pathak, J., et al. (2022). *FourCastNet: A global data-driven high-resolution weather model using adaptive Fourier neural operators*. arXiv:2202.11214.
- ADR-0001 — xarray como abstracción central (el contrato de I/O del adapter es xr.DataArray).
- ADR-0006 — PyInstaller + Inno Setup packaging (el extra `[neural]` queda fuera del bundle Windows v0.1.0).
- ADR-0007 — Reproducibility policy (relación con determinismo neural pendiente).
- `core-interpolation/requirements.md` §7 Supuestos (a actualizar en v0.2.0).
