# Política de seguridad de `tempify`

## Versiones soportadas

Las versiones que reciben parches de seguridad son las **dos minor más recientes** de la serie 0.x y, una vez publicada, la última major estable.

| Versión | Soporte de seguridad |
|---|---|
| 0.1.x | ✅ Soportada (actual: v0.1.2) |
| < 0.1.0 | ❌ No soportada |

## Cómo reportar una vulnerabilidad

`tempify` es una librería Python de procesamiento local (no levanta servicios de red), por lo que la superficie de ataque es limitada. Aun así, **reporta cualquier hallazgo de seguridad de forma privada**, no como issue público.

**Canales preferidos:**

1. **GitHub Private Vulnerability Reporting** (recomendado): abrí un reporte privado en `https://github.com/djwillichile/tempify/security/advisories/new`. Se manejará confidencialmente con el mantenedor y co-asegurador antes de hacerse público.
2. **Email**: `contacto@icta.cl` — contacto institucional con redirección al mantenedor.

Por favor incluí:

- Descripción del problema y su impacto.
- Pasos reproducibles (idealmente un caso mínimo).
- Versión de `tempify` afectada (`python -c "import tempify; print(tempify.__version__)"`).
- Cualquier mitigación que hayas identificado.

## Tiempo de respuesta esperado

- **Acuse de recibo**: hasta **5 días hábiles**.
- **Triaje inicial y severidad asignada**: hasta **10 días hábiles**.
- **Fix publicado en una release patch**: depende de la severidad
  - CRITICAL/HIGH: hasta **30 días** desde el triaje.
  - MED/LOW: en la próxima release programada.

Si el problema requiere coordinación con upstream (numpy, xarray, rasterio…), te informaremos del estado.

## Política de divulgación

- Damos crédito a quien reporta (a menos que pida anonimato).
- Coordinamos un **embargo** entre fecha del fix mergeado y publicación del advisory.
- Una vez publicado, registramos un **GitHub Security Advisory** con CVE solicitado si aplica.

## Lo que NO es una vulnerabilidad

Para evitar reportes desencaminados:

- **Volcado de path absoluto local** en mensajes de error (esperado en una librería que opera sobre archivos del usuario).
- **DoS por input adversarial** (rásters maliciosamente formados que consumen memoria): tempify confía en `rasterio`/`GDAL` para parsing; reportá a esos proyectos directamente.
- **CVEs en dependencias declaradas con `>=`** sin un escenario de ataque concreto contra tempify: registralos en Dependabot y se atenderán en el ciclo regular.

## Buenas prácticas para quien usa `tempify`

- Mantené `tempify` actualizado: `pip install --upgrade tempify`.
- No corrás `tempify` con privilegios elevados sobre archivos no confiables.
- Para procesamiento batch automático, considerá ejecutarlo en una **sandbox** (Docker, venv aislado).
- Verificá el DOI del release citado (https://doi.org/10.5281/zenodo.20251750 para v0.1.2) antes de utilizar el código en investigación reproducible.

---

Mantenido por **ICTA Ltda.** · Santiago, Chile.
Última actualización: 2026-05-17.
