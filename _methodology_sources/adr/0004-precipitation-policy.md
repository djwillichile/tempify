# ADR-0004: Política de precipitación

**Status:** Accepted
**Date:** 2026-05-16
**Decision-makers:** Guillermo Fuentes-Jaque

## Context

La precipitación es una variable cualitativamente distinta a temperatura, humedad o radiación. Sus propiedades estadísticas hacen que la interpolación temporal suave (Lineal, PCHIP, PCHIP+RM, Fourier) produzca resultados no físicos:

- **Intermitente.** La mayoría de los días no presentan precipitación; unos pocos concentran el total mensual.
- **Distribución sesgada a la derecha.** Sin gaussianidad ni autocorrelación temporal comparable a temperatura.
- **Cota inferior dura en cero.** Valores negativos son físicamente imposibles.
- **No suave.** Las tormentas son eventos discretos, no transiciones continuas.

Aplicar un interpolador suave sobre totales mensuales de precipitación produce "drizzle" artificial (todos los días reciben una fracción no nula), elimina la varianza diaria real, subestima eventos extremos y rompe la conservación del cero. La información necesaria para reconstruir variabilidad diaria **no existe** en la serie mensual: debe provenir de un producto diario (CHIRPS, ERA5-Land) o de un weather generator estocástico (LARS-WG, cadenas de Markov + gamma). Ninguna de estas vías está en alcance para tempify v1.0, que es un densificador determinístico.

La política debe equilibrar dos preocupaciones: (a) proteger a usuarios menos expertos de generar outputs científicamente inválidos, y (b) no bloquear completamente a usuarios avanzados que sepan qué hacen (p. ej., benchmarking, comparación de métodos, casos donde el output se postprocesa).

Ver `docs/methodology/precipitation.md` para el desarrollo completo de la justificación.

## Decision

Política dual de **rechazo por defecto** con **override expreso**:

1. **Rechazo por defecto.** El componente `MethodVariableCompatibilityChecker` (Capa 3, Validation) rechaza el par `(variable=precipitation, method ∈ {linear, pchip, pchip_mp, fourier})` lanzando `MethodVariableIncompatibilityError`. La identificación de la variable usa `VariableProfileMatcher` (standard_name, patrones de nombre, unidades). El veto se carga desde `profiles/precipitation.yaml` con `allowed_methods: []` y `rejected_methods: [linear, pchip, pchip_mp, fourier]`.

2. **Override expreso.** Existe un escape consciente vía CLI: `--force-method <method> --i-know-what-i-am-doing`. El override:
   - Requiere **confirmación interactiva** explícita (no se acepta en modo no interactivo sin un segundo flag `--force-method-confirm`).
   - **Estampa metadatos** en el output: `attrs["force_method_used"] = true` y `attrs["force_method_warning"] = "Resultado no recomendado científicamente"`.
   - Registra el evento en el reporte de ejecución.

## Rationale

### Por qué rechazo por defecto y no warning

Los warnings se ignoran rutinariamente: se ahogan en logs, no aparecen en notebooks de exploración, y desaparecen en pipelines automatizados. Un usuario inexperto recibirá un GeoTIFF aparentemente correcto y lo publicará. El rechazo duro convierte el error silencioso en un error explícito que debe resolverse antes de continuar.

### Por qué existe el override

Negar absolutamente el método elimina casos legítimos: benchmarks metodológicos, comparaciones contra una baseline "ingenua", investigación sobre el efecto de la interpolación suave, generación de inputs para pipelines downstream que aplican su propia bias correction. El override expreso preserva estos casos a costa de fricción deliberada.

### Por qué stamping de metadatos

El output puede salir de tempify y entrar en cadenas analíticas largas. Un consumidor downstream (humano o automatizado) debe poder filtrar outputs no recomendados sin reconstruir la procedencia. La metadata viaja con el archivo (NetCDF `attrs`, GeoTIFF tags) y es la única señal persistente.

## Alternatives considered

### Silenciar el rechazo (sólo warning en logs)

Descartado. Mala UX científica: los warnings son ruido. El usuario que no sabe que la interpolación suave es inválida sobre precipitación tampoco va a leer un warning entre cien líneas de log. Riesgo alto de mal uso silencioso.

### Soportar weather generators (estocásticos) en v1.0

Descartado por alcance. Un weather generator robusto (cadenas de Markov para ocurrencia + distribución gamma/exponencial para intensidad, condicionado mensualmente) es un proyecto en sí mismo. tempify se define como **densificador determinístico** y reproducible bit-exact (ver Guardrail 6 en CLAUDE.md). Introducir estocasticidad rompería esa garantía. Puede evaluarse como módulo opt-in en una v2.x.

### Permitir interpolación libre con warning prominente

Descartado. Variante del primer alternativo. Cualquier mecanismo que no detenga la ejecución es ignorable.

### Implementar delta method (bias correction multiplicativa contra un producto diario)

Descartado por alcance. Es una técnica válida (ver `methodology/precipitation.md` Opción B), pero requiere un input adicional (producto diario de referencia), lógica de pareo temporal y espacial, y reabre la pregunta de qué producto usar. Diferido a futuro como módulo opt-in.

## Consequences

### Positive

- **Protege a usuarios menos expertos** del error silencioso más probable del dominio.
- **Señal clara en la metadata** para auditoría y filtrado downstream.
- **Coherente con el principio de fail-fast** del proyecto: errores explícitos sobre warnings.
- **Documenta intención científica** en el output: cualquier reviewer puede detectar un `force_method_used = true`.

### Negative

- **Fricción para usuarios avanzados** que deban justificar conscientemente el override.
- **Confirmación interactiva** complica pipelines no interactivos (mitigado por `--force-method-confirm`).
- **Mantenimiento adicional**: el perfil `precipitation.yaml` y los matchers deben actualizarse a medida que aparezcan nuevas convenciones de nombre o unidades.

### Risks

- Detección de "precipitación" puede tener falsos negativos (variable mal nombrada, sin standard_name, unidades ambiguas). Mitigación: documentar la lista de matchers y permitir al usuario forzar el perfil con `--variable-profile precipitation`.
- Usuarios con experiencia podrían encontrar el flujo de override molesto y abandonar la herramienta. Aceptado como costo de la política.

## Implementation notes

- **`MethodVariableCompatibilityChecker`** (Capa 3, ver `steering/architecture.md`) consulta `VariableProfile.allowed_methods` y `VariableProfile.rejected_methods` cargados desde YAML.
- **`profiles/precipitation.yaml`**: `allowed_methods: []`, `rejected_methods: [linear, pchip, pchip_mp, fourier]`. En futuras versiones podrá listar métodos de conservación de masa cuando existan.
- **CLI**: ante `--force-method` sobre precipitación, mostrar el prompt interactivo:
  > `ATENCIÓN: ¿Confirmas que entiendes que interpolar precipitación con un método suave producirá valores no físicos? (escriba 'si entiendo' para continuar):`
  Solo la cadena exacta `si entiendo` autoriza la ejecución. Cualquier otra entrada aborta con código de salida no cero.
- **Stamping**: obligatorio en todo writer (`io-handlers`). Los `attrs` deben propagarse a NetCDF (atributos globales), GeoTIFF (tags) y Zarr (consolidated metadata).
- **Reporte de validación**: el override debe quedar registrado en el `impl-log` de la corrida y en el reporte estructurado de `specs/validation`.
- **Tests**: cobertura obligatoria para (a) rechazo por defecto, (b) override con confirmación correcta, (c) override sin confirmación rechazado, (d) presencia de `attrs` en outputs forzados.

## References

- `docs/methodology/precipitation.md` — fundamentos científicos y workflows alternativos.
- `steering/architecture.md` § Capa 3 Validation — ubicación de `MethodVariableCompatibilityChecker`.
- `specs/validation/requirements.md` — requisitos donde se enforça la política.
- `specs/cli/requirements.md` — superficie del flag `--force-method` y la confirmación interactiva.
- CLAUDE.md, Guardrail 5: "Precipitación nunca se interpola con métodos suaves."
- Wilks, D. S., & Wilby, R. L. (1999). The weather generation game. *Progress in Physical Geography*, 23(3), 329-357.
