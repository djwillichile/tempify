# ADR-0006: PyInstaller --onedir + Inno Setup para empaquetado Windows

**Status:** Accepted
**Date:** 2026-05-16
**Decision-makers:** Guillermo Fuentes-Jaque

## Contexto

tempify debe distribuirse a usuarios Windows que no operan entornos Python (investigadores geoespaciales, profesionales de gestión territorial), manteniendo en paralelo la distribución `pip install tempify` para desarrolladores. La spec `specs/packaging/requirements.md` exige un instalador `.exe` self-contained para Windows 10 (19041+) y Windows 11 x64, con wizard en español, accesos directos al menú inicio, asociación opcional de extensiones `.nc` y `.tif`, y compilación automatizada en CI sobre tags `v*`.

El bundle a empaquetar tiene dependencias problemáticas que cargan recursos en runtime y son notoriamente sensibles a las herramientas de empaquetado:

- `rasterio` y `pyproj` traen GDAL y PROJ embebidos en sus wheels, con directorios `gdal-data/` y `proj/` que se resuelven en runtime vía variables de entorno (`GDAL_DATA`, `PROJ_LIB`).
- `PySide6` (ver ADR-0005) carga plugins Qt dinámicamente desde `PySide6/plugins/`, junto con traducciones y recursos por estilo.
- `netcdf4` enlaza HDF5 y libcurl como DLLs nativas.
- `scipy` incluye módulos compilados (`scipy.special._cdflib`, LAPACK/BLAS) que las herramientas de empaquetado a veces omiten en el análisis estático.
- `dask` y sus distribuciones se cargan parcialmente vía `pkg_resources`.

La decisión cubre dos eslabones separables: (1) la toolchain Python → bundle autocontenido, y (2) el envoltorio instalador Windows con wizard nativo.

## Decisión

1. Usar **PyInstaller >= 6.3** en modo **`--onedir`** (no `--onefile`) para generar el bundle Python autocontenido, parametrizado en `packaging/pyinstaller.spec`.
2. Usar **Inno Setup >= 6.2** para envolver ese bundle en un instalador Windows `.exe` con wizard en español, parametrizado en `packaging/installer.iss`.

## Justificación

### Toolchain Python → bundle

#### PyInstaller `--onedir` (elegido)

- Distribuye un directorio con `tempify.exe` + DLLs + recursos como árbol explícito.
- Arranque rápido: no hay extracción a `%TEMP%` previo al primer frame de la GUI; cumple NFR-001 (< 5 s cold start).
- Compatible con la búsqueda de recursos en runtime de `rasterio`/`pyproj`/`PySide6`: los paths relativos al ejecutable funcionan sin tocar variables de entorno globales.
- Fácil de inspeccionar y diagnosticar: cuando un hook falla, el contenido del directorio es directamente legible.
- Ecosistema maduro de hooks, incluyendo entradas oficiales para `rasterio`, `pyproj`, `scipy`, `numpy`, `PySide6`.

#### PyInstaller `--onefile` (descartado)

- Genera un único `.exe` pero extrae todo a `%TEMP%\_MEIxxxx` en cada arranque: cold start lento (suma 3-8 s adicionales), violando NFR-001.
- Incompatible con la resolución de rutas runtime de `rasterio` y `pyproj`: los `gdal-data/` y `proj/` quedan en una carpeta temporal cuyo path cambia entre ejecuciones, rompiendo configuraciones cacheadas.
- Dificulta el diagnóstico (no se puede inspeccionar el bundle sin extraerlo manualmente).
- El instalador Inno Setup ya nos da el wrapper `.exe` final; no necesitamos `--onefile` para presentar al usuario un único archivo.

#### Nuitka (descartado)

- Compila Python a C, prometiendo binarios más pequeños y rápidos.
- Tiempos de build muy superiores (decenas de minutos en CI vs. minutos para PyInstaller), incompatible con iteración ágil.
- Compatibilidad con extensiones C ya compiladas (`numpy`, `scipy`, `rasterio`, `netcdf4`) sigue siendo irregular; reportes recurrentes de fallos en runtime cuando se mezcla código compilado por Nuitka con wheels precompiladas.
- Comunidad y ecosistema de hooks notablemente menor que PyInstaller para el stack científico.

#### Briefcase / BeeWare (descartado)

- Pensado primariamente para apps Toga; el soporte para el stack PySide6 + ciencia (GDAL, NetCDF, scipy) es prematuro.
- Documentación del flujo Windows + dependencias nativas pesadas es escasa.

#### cx_Freeze (descartado)

- Funcionalmente análogo a PyInstaller en modo `--onedir`, pero con comunidad y catálogo de hooks notablemente menores.
- Históricamente más fricción con GDAL/PROJ y PySide6.

### Envoltorio instalador Windows

#### Inno Setup (elegido)

- Wizard nativo Windows con look-and-feel familiar para el usuario final.
- Scripting Pascal expresivo: condicionales, asociación de archivos, detección de instalación previa, preservación de `%APPDATA%\tempify\config.yaml` (REQ-009).
- Soporte de localización maduro, incluyendo paquete oficial `Spanish.isl` (REQ-004).
- Gratuito, sin licencias por seat ni restricciones para distribución comercial.
- Comunidad grande, ejemplos abundantes para casos análogos (empaquetar bundles PyInstaller).
- Instala VC++ Redistributable como dependencia opcional (REQ-007).

#### NSIS (descartado)

- Scripting más arcaico (lenguaje propio basado en macros) y menos legible que Pascal.
- Look del wizard menos pulido; requiere skins de terceros para igualar a Inno Setup.
- Soporte de localización menos uniforme.

#### WiX / MSI (descartado)

- Orientado a entornos empresariales con GPO y despliegue automatizado.
- Curva de aprendizaje alta (XML verboso, modelo de componentes complejo).
- Capacidades excedentes para el escenario de usuario final individual.

#### MSIX (descartado, postpuesto)

- Requiere certificado de code-signing (no disponible en la línea de tiempo de v0.1.0, ver supuestos en `specs/packaging/requirements.md`).
- Distribución vía Microsoft Store o sideload con políticas firmadas: fricción adicional para usuarios académicos.
- Decisión diferida a ADR-0013 cuando exista certificado.

#### Distribución zip portable (complementario, no principal)

- Viable como artefacto adicional para usuarios sin permisos administrativos, pero no cumple REQ-005 (shortcuts) ni REQ-006 (asociación de extensiones).
- Se valorará como salida secundaria del mismo workflow CI, sin reemplazar al `.exe`.

## Consecuencias

### Positivas

- Cumplimiento directo de REQ-001 a REQ-010 de `specs/packaging/requirements.md` con dos herramientas estándar y bien documentadas.
- Build reproducible: `pyinstaller.spec` e `installer.iss` versionados en el repo (NFR-005).
- Cold start rápido por usar `--onedir` (NFR-001).
- Mantiene `pip install tempify` intacto (REQ-010): el empaquetado vive en `packaging/`, no afecta a `pyproject.toml` ni a la estructura del paquete.
- Pipeline CI estándar en GitHub Actions sobre `windows-2022` con tooling disponible vía Chocolatey o actions dedicadas.

### Negativas

- Footprint estimado del bundle: 250-350 MB descomprimido, 80-130 MB para el `.exe` Inno Setup comprimido. Se acerca al umbral NFR-002 (< 300 MB del instalador). Mitigaciones:
  - `--exclude-module` para submódulos no usados de `scipy` (`scipy.optimize._lsq` test data), `numpy.testing`, `PySide6.QtWebEngine*`, `PySide6.Qt3D*`, `PySide6.QtCharts`, `PySide6.QtMultimedia`.
  - Recorte de Qt plugins innecesarios (sólo `platforms/qwindows.dll`, `styles`, `imageformats/{png,jpeg,svg}`).
  - Compresión LZMA2 en Inno Setup.
- Sin firma digital en v0.1.0: SmartScreen marcará el `.exe` como no reconocido. Mitigación documental en README; firma diferida a ADR-0013.
- Dependencia operativa de Inno Setup en el runner CI: añade una action más al workflow.

### Riesgos

- PyInstaller no detecta automáticamente todos los recursos de `rasterio`, `pyproj`, `PySide6` o `netcdf4`. Mitigación: hooks explícitos versionados (ver notas de implementación) y smoke test post-build.
- Versiones futuras de las wheels de `rasterio` o `pyproj` cambian el layout de `gdal-data/` o `proj/`. Mitigación: pin estricto en `pyproject.toml` y smoke test en CI que valida importación y proyección de un raster fixture.
- Imagen base del runner Windows en GitHub Actions cambia entre ejecuciones. Mitigación: pin a `windows-2022` (no `windows-latest`) y revisión cuando GitHub publique cambios al runner.

## Notas de implementación

- **`packaging/pyinstaller.spec`** versionado, con:
  - `datas` explícitos para `rasterio` (`gdal-data/`), `pyproj` (`proj/`), `PySide6` (`plugins/platforms`, `plugins/styles`, `plugins/imageformats`, traducciones `es_*`), `netcdf4` (DLLs HDF5).
  - `hiddenimports` para `scipy.special._cdflib`, `scipy._lib.array_api_compat.numpy`, `rasterio.sample`, `rasterio.vrt`, `rasterio._features`, `pyproj.crs`, `pyproj._network`, `PySide6.QtSvg`.
  - `excludes` para submódulos de Qt y scipy no usados (ver mitigación de footprint).
  - `console=False` para la GUI; CLI separado con `console=True` y entrypoint adicional.
- **`packaging/installer.iss`** con:
  - `Languages` incluyendo `compiler:Languages\Spanish.isl` (REQ-004).
  - `[Tasks]` para asociación opcional de `.nc` y `.tif` (REQ-006), shortcut de escritorio opcional, shortcut de menú inicio obligatorio (REQ-005).
  - `[Registry]` para asociación de extensiones con icono propio.
  - `[Code]` Pascal con `InitializeSetup` que detecta y preserva `%APPDATA%\tempify\config.yaml` durante upgrade (REQ-009).
  - `[Run]` para instalar VC++ Redistributable si no está presente (REQ-007).
  - Modo de instalación **per-machine por defecto** (requiere admin, instala en `Program Files`); opción **per-user** disponible vía `PrivilegesRequired=lowest` con `PrivilegesRequiredOverridesAllowed=dialog`.
  - Compresión `LZMA2/ultra64` para minimizar tamaño del `.exe`.
- **CI**: workflow `.github/workflows/build-windows.yml` con `runs-on: windows-2022` pineado (no `windows-latest`) para reproducibilidad. Inno Setup instalado vía `crazy-max/ghaction-chocolatey` o `Minionguyjpro/Inno-Setup-Action`. Tags `v*` disparan build y attach al GitHub Release.
- **Firma digital**: sin firma en v0.1.0. Se publica un archivo `SHA256SUMS` junto al `.exe` en el release de GitHub para verificación de integridad. La firma con certificado de code-signing queda diferida a ADR-0013.
- **Smoke test**: job CI que instala el `.exe` en VM Windows limpia, lanza la GUI vía pytest-qt headless con `QT_QPA_PLATFORM=offscreen`, procesa un fixture WorldClim reducido, verifica salida y desinstala. Cubre NFR-003 y REQ-001.

## Referencias

- PyInstaller: https://pyinstaller.org
- PyInstaller hooks para rasterio: https://pyinstaller.org/en/stable/hooks.html
- Inno Setup: https://jrsoftware.org/isinfo.php
- rasterio packaging notes: https://rasterio.readthedocs.io/en/stable/installation.html
- pyproj data files: https://pyproj4.github.io/pyproj/stable/installation.html
- Spec: `specs/packaging/requirements.md`
- ADR-0005: PySide6 como framework GUI
- ADR-0013 (pendiente): code-signing y MSIX
