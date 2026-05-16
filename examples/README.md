# Ejemplos de tempify

## WorldClim Chile Central

Demo end-to-end con datos sintéticos que reproducen la climatología real
de temperatura media mensual de la Región Metropolitana de Santiago,
siguiendo la convención de nombres de WorldClim v2.1.

### Datos

12 GeoTIFFs de 30×30 píxeles en EPSG:4326, ~50 KB total. No requieren
descarga: se generan localmente a partir de la climatología real
publicada por WorldClim (21 °C verano, 9 °C invierno) más un gradiente
altitudinal este-oeste que simula el efecto andino.

### Cómo ejecutar

```bash
# 1. Generar los archivos sinteticos (una sola vez)
python examples/generate_worldclim_sample.py

# 2. Opcion A: usar el CLI
tempify convert examples/data/worldclim_chile_central \
    --method pchip_mp \
    --year 2023 \
    --output examples/out/cli \
    --report examples/out/cli/report.md

# 3. Opcion B: usar el script API que verifica numericamente
python examples/run_demo.py
```

### Qué verifica el demo

- `tempify` clasifica la entrada como **mode B** (colección de monocapas).
- Infiere frecuencia **climatological** por el patrón WorldClim
  (`wc2.1_2.5m_tavg_NN.tif`).
- Genera un NetCDF diario con 365 valores (año 2023).
- En modo `pchip_mp` la media mensual del output coincide con el input
  dentro de la tolerancia contractual (`atol = 1e-4 °C` per ADR-0010 nivel 2).
- El reporte de procedencia incluye versión, timestamp UTC, MD5 de
  inputs, configuración y resumen de validación.

### Por qué no datos reales de WorldClim

WorldClim distribuye archivos globales de ~50 MB cada uno. Bundlear datos
reales en el repo violaría la práctica de mantener `git clone` ligero y
requiere acceso a internet para clonar el proyecto completo. Los datos
sintéticos preservan las propiedades estadísticas relevantes (rango,
ciclo anual, gradiente espacial) y bastan para validar el flujo
end-to-end. Para experimentos científicos use sus propios datos reales
de WorldClim, CHELSA, CHIRPS o ERA5.
