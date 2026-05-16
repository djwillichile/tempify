# Product Context

## Visión

**tempify** es la herramienta de referencia para **densificación temporal** de stacks ráster geoespaciales en flujos científicos y de consultoría ambiental. Convierte series ráster de baja frecuencia (típicamente mensual o climatológica) en series densas (diarias) preservando propiedades estadísticas críticas.

Concepto análogo: igual que la interpolación de fotogramas genera frames intermedios para video más fluido, tempify genera valores diarios intermedios entre nodos mensuales para stacks ráster más densos.

## Problema central

La mayoría de productos climáticos globales se distribuyen a frecuencia mensual o climatológica (WorldClim, CHELSA, TerraClimate, CRU-TS), pero múltiples aplicaciones requieren resolución diaria:

- Cálculo de grados-día (GDD) para fenología y agricultura
- Evapotranspiración (Hargreaves-Samani, Penman-Monteith)
- Índices bioclimáticos derivados
- Modelos hidrológicos distribuidos
- Modelos de distribución de especies (SDM) con cubiertas diarias
- Modelación regional de calidad del aire

Hoy esta conversión se hace con scripts ad-hoc, sin validación sistemática y frecuentemente sin preservación de la media mensual.

## Audiencia objetivo

1. Investigadores en ciencias ambientales (climatología aplicada, hidrología, ecología, SDM).
2. Consultores en evaluación ambiental que preparan inputs climáticos.
3. Docentes de teledetección, GIS y climatología.
4. Equipos de ciencia de datos en organismos públicos (DGA, DMC, MINAGRI, gobiernos regionales).

## Casos de uso prototípicos

### Caso 1: Investigador prepara datos para modelo de cultivos
> "Tengo WorldClim mensual de Chile, necesito 366 días de temperatura media para alimentar un modelo de GDD. Quiero que la media mensual se conserve."

### Caso 2: Consultor prepara EIA con clima diario
> "El cliente me pidió una serie diaria climatológica para una cuenca. Necesito documentación metodológica para justificar el procedimiento ante el SEA."

### Caso 3: Docente arma material de curso
> "Quiero un notebook reproducible que muestre los 4 métodos sobre un dataset pequeño, para una clase de teledetección."

### Caso 4: Operador de pipeline automatizado
> "Tengo un workflow nocturno que descarga ERA5-Land mensual y necesita producir diario. Quiero un comando CLI ejecutable sin intervención humana."

## No-objetivos explícitos

- No es un GIS general (no reproyecta, no recorta, no hace álgebra de mapas).
- No hace downscaling espacial (resolución de entrada = salida).
- No es un weather generator estocástico (no inventa varianza diaria).
- No interpola precipitación con métodos suaves (rechazado por diseño).
- No es un servicio web ni SaaS (en v1.0).
- No analiza ni modela datos: solo prepara.

## Contexto regional (Chile/Latam)

Los ejemplos y tutoriales priorizan casos chilenos y latinoamericanos:

- Datos: WorldClim, CHELSA, CR2, DMC, ERA5-Land sobre Chile.
- Validación canónica: estación Quinta Normal 2020.
- Documentación primaria en español.
- Casos: cuencas hidrográficas, regiones administrativas, dominios DGA.

No excluye uso global; significa que los ejemplos priorizan este contexto.

## Métricas de éxito v1.0

- Procesar WorldClim 2.5min Chile completo + 12 meses en < 10 min, máquina 8 cores 16 GB.
- Conservación de media mensual con error < 1e-4 °C usando PCHIP+RM.
- Instalable con un comando en Linux/macOS/Windows.
- ≥ 5 citaciones académicas o usos en consultoría documentados en 12 meses post-publicación.
