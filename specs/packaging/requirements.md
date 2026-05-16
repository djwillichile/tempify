# Requirements — packaging

**Estado:** Draft
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-16
**Última actualización:** 2026-05-16

## 1. Propósito

Generar un instalador Windows `.exe` que distribuya el paquete `tempify` y su GUI a usuarios finales sin Python instalado, manteniendo en paralelo la distribución estándar vía `pip` para usuarios desarrolladores. La densificación temporal de stacks ráster debe ser accesible a investigadores y profesionales geoespaciales que no operan entornos Python.

## 2. Alcance

### In-scope

- Script de build PyInstaller (`packaging/pyinstaller.spec`) en modo `--onedir` para producir el bundle del ejecutable.
- Hooks runtime PyInstaller que aseguran inclusión de `rasterio.*`, `pyproj.*`, `netcdf4`, `scipy`, datos de proyección PROJ y `gdal-data`.
- Script Inno Setup (`packaging/installer.iss`) que genera el instalador `.exe` con: paso de instalación, accesos directos (menú inicio y escritorio opcional), asociación opcional de extensiones `.nc` y `.tif` con la GUI.
- Workflow CI `.github/workflows/build-windows.yml` que dispara la compilación sobre tags `v*` y adjunta el instalador al GitHub Release.
- Verificación de tamaño del bundle (umbral) y smoke test post-instalación (instalar, abrir GUI, procesar fixture, desinstalar).
- Mantenimiento simultáneo de la distribución `pip` (no se rompe `pip install tempify`).

### Out-of-scope

- Firma digital del instalador con certificado de code-signing (diferido a v0.2.0 cuando exista certificado).
- Distribución vía MSIX o Microsoft Store.
- Instaladores Linux (`.deb`, `.rpm`, `AppImage`) y macOS (`.dmg`, `.pkg`); cobertura best-effort fuera del scope de esta spec.
- Auto-actualización del cliente (sin updater embebido).

## 3. Actores y casos de uso

### Actor 1: Usuario final Windows sin Python

> Como investigador geoespacial sin entorno Python, quiero instalar tempify desde un `.exe` para usar la GUI sin configurar dependencias.

**Caso de uso típico:** El usuario descarga `tempify-0.1.0-win64-setup.exe` desde GitHub Releases, ejecuta el instalador (next-next-finish), lanza "tempify" desde el menú inicio, abre la GUI, carga un stack mensual WorldClim, configura método PCHIP+RM y procesa el dataset hasta obtener salida diaria.

### Actor 2: Mantenedor

> Como mantenedor del proyecto, quiero que el instalador se construya automáticamente al publicar un tag de release, para no depender de máquinas locales.

**Caso de uso típico:** El mantenedor crea el tag `v0.1.0` en GitHub. El workflow CI compila el bundle PyInstaller, genera el `.exe` Inno Setup, lo adjunta al GitHub Release y publica el changelog asociado.

## 4. Requisitos funcionales (formato EARS)

### REQ-001

THE SYSTEM SHALL provide a Windows installer `.exe` that is self-contained for Windows 10 (build 19041+) and Windows 11 x64, with no requirement that the target machine have Python installed.

### REQ-002

WHEN the CI workflow runs on a tag matching `v*`, THE SYSTEM SHALL build the PyInstaller bundle, generate the Inno Setup `.exe` and attach it as a release asset to the corresponding GitHub Release.

### REQ-003

THE SYSTEM SHALL bundle GDAL data, PROJ data, all Python dependencies declared in `pyproject.toml`, and the Qt resources required by the GUI specified in `../gui/requirements.md`.

### REQ-004

WHEN the user runs the installer, THE SYSTEM SHALL present the Inno Setup wizard with all user-facing texts (welcome, license, install path, finish) in Spanish.

### REQ-005

WHEN the installation finishes, THE SYSTEM SHALL create a Start Menu shortcut named "tempify" that launches the GUI as the default entry point, and an optional Desktop shortcut.

### REQ-006

WHERE the user opts in during installation, THE SYSTEM SHALL register file associations for `.nc` and `.tif` extensions so that double-click opens the file in the tempify GUI.

### REQ-007

IF the target machine lacks the required Microsoft Visual C++ runtime, THEN THE SYSTEM SHALL install it automatically as part of the setup flow.

### REQ-008

WHEN the user uninstalls tempify, THE SYSTEM SHALL remove all program files installed under the installation directory and preserve any output files produced by the user outside that directory.

### REQ-009

WHEN the installer detects an existing tempify installation, THE SYSTEM SHALL preserve the user configuration file located at `%APPDATA%\tempify\config.yaml` during the upgrade.

### REQ-010

THE SYSTEM SHALL keep the `pip install tempify` developer distribution functional and unaffected by the packaging artifacts.

## 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Performance | Cold start de la GUI desde el ejecutable instalado | < 5 s en máquina típica (Windows 11, SSD, 16 GB RAM) medido por smoke test |
| NFR-002 | Memory/Footprint | Tamaño del instalador `.exe` final | < 300 MB; reportado por job CI |
| NFR-003 | Reliability | Smoke test verde en GitHub Actions `windows-latest` | Instala, abre GUI, procesa fixture, desinstala sin errores |
| NFR-004 | Portability | Soporte de plataforma | Windows 10 build 19041 mínimo y Windows 11 22H2; documentado en README |
| NFR-005 | Maintainability | Reproducibilidad del build | `pyinstaller.spec` e `installer.iss` versionados; build reproducible desde el repo |
| NFR-006 | Coverage | Cobertura del módulo `tempify.packaging` (si aplica código Python auxiliar) | >= 85% reportado por `pytest --cov` |

## 6. Criterios de aceptación

- [ ] REQ-001 cubierto por test `test_installer_runs_without_python` (VM Windows limpia en CI).
- [ ] REQ-002 cubierto por verificación del workflow `build-windows.yml` sobre un tag de prueba.
- [ ] REQ-003 cubierto por test `test_bundle_contains_gdal_proj_qt`.
- [ ] REQ-004 cubierto por inspección visual del wizard y test `test_installer_locale_es`.
- [ ] REQ-005 cubierto por test `test_start_menu_shortcut_created`.
- [ ] REQ-006 cubierto por test `test_file_association_optional`.
- [ ] REQ-007 cubierto por test `test_vcruntime_installed`.
- [ ] REQ-008 cubierto por test `test_uninstall_preserves_user_outputs`.
- [ ] REQ-009 cubierto por test `test_upgrade_preserves_config`.
- [ ] REQ-010 cubierto por test `test_pip_install_still_works`.
- [ ] NFR-001 medido y dentro del umbral (< 5 s) por smoke test.
- [ ] NFR-002 medido y reportado (< 300 MB).
- [ ] NFR-003 smoke test verde en `windows-latest`.
- [ ] NFR-006 cobertura medida si hay módulo auxiliar Python.
- [ ] Documentación de packaging actualizada en `docs/`.
- [ ] CHANGELOG actualizado.

## 7. Dependencias y supuestos

### Specs relacionadas

- Bloqueada por `../gui/requirements.md` (la GUI es el entry point por defecto del instalador).
- Bloqueada por `../cli/requirements.md` (debe quedar disponible vía shortcut o consola).
- Bloqueada transitivamente por `../core-interpolation/requirements.md`, `../io-handlers/requirements.md`, `../structure-detection/requirements.md`, `../temporal-frequency-resolver/requirements.md`, `../validation/requirements.md` (el pipeline debe estar funcional para empaquetarlo).
- Bloquea: release v0.1.0.

### Supuestos

- GitHub Actions con runner `windows-latest` está disponible y permanece compatible con PyInstaller >= 6.3.
- Inno Setup 6.x se instala en el runner mediante `chocolatey` o una action equivalente (ej. `inno-setup-action`).
- Las wheels de `rasterio` y `pyproj` distribuidas en PyPI incluyen GDAL/PROJ binarios; no se requiere GDAL nativo en el sistema destino.
- El equipo del autor no dispone de certificado de code-signing en la línea de tiempo de v0.1.0.
- El usuario final tiene permisos administrativos para instalar el `.exe` (modo por defecto) o usa el modo single-user si se ofrece.

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| PyInstaller no detecta automáticamente recursos de `rasterio`, `pyproj` o `netcdf4` | Alta | Alto | Hooks explícitos en `packaging/pyinstaller.spec`, smoke test post-build que valida importación y operación |
| El bundle excede 300 MB por dependencias de PySide6 y `scipy` | Media | Medio | Listas de `--exclude-module` para submódulos no usados, recorte de Qt plugins innecesarios, revisión periódica de tamaño |
| SmartScreen marca el instalador no firmado como riesgoso | Alta | Medio | Documentar workaround temporal en README ("Más información" → "Ejecutar de todas formas"), priorizar code-signing para v0.2.0 |
| Wheels de `rasterio`/`pyproj` cambian de layout y rompen el spec | Media | Alto | Pinear versiones en `pyproject.toml`, smoke test en CI que detecta regresiones |
| GitHub Actions `windows-latest` cambia su imagen base | Baja | Medio | Pinear versión específica del runner en el workflow cuando sea posible |

## 8. Referencias

- PyInstaller: https://pyinstaller.org
- Inno Setup: https://jrsoftware.org/isinfo.php
- Rasterio packaging guide: https://rasterio.readthedocs.io/en/stable/installation.html
- Microsoft SmartScreen: https://learn.microsoft.com/en-us/windows/security/operating-system-security/virus-and-threat-protection/microsoft-defender-smartscreen/
- Steering: `../../steering/product.md`, `../../steering/tech.md`
- ADR pendiente: ADR-0006 (selección PyInstaller + Inno Setup)
