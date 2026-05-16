# Tasks — packaging

**Estado:** Approved
**Design doc:** [design.md](design.md)
**Última actualización:** 2026-05-15

## Notas previas

Esta spec NO produce código Python runtime. Los entregables son scripts (PowerShell, PyInstaller `.spec`, hooks Python para PyInstaller), configuración Inno Setup, workflow CI y documentación. El "TDD" aplica vía tests CI ejecutables en `windows-2022`: las tareas de tipo `test` son scripts PowerShell o jobs YAML que validan los criterios de aceptación.

Convenciones de archivos por componente: ver `design.md` §2. AppId GUID estable para upgrades: `{{B7A21C3D-4E5F-4A8B-9C2D-1F3E5A7B9C0D}}`.

---

## Fase 1: Fundamentos

### task-1.1: Crear estructura de carpetas `packaging/`

**Tipo:** chore
**Estimación:** 0.5h
**Bloquea:** task-1.2, task-1.3, task-1.4, task-1.5, task-1.6, task-1.7
**Bloqueada por:** —

**Descripción:** Crear el árbol de carpetas para artefactos de build: `packaging/`, `packaging/hooks/`, `packaging/installer/`, `packaging/installer/resources/`, `packaging/scripts/`. Añadir un `packaging/README.md` corto explicando que esta carpeta NO es un paquete Python, sino artefactos de build (ver design §2 y §6, Decisión 7).

**Criterio de done:**
- [ ] Carpetas creadas y versionadas (con `.gitkeep` si vacías).
- [ ] `packaging/README.md` aclara propósito y enlaza al design.
- [ ] Ningún archivo `__init__.py` añadido bajo `packaging/`.

**Archivos:**
- `packaging/README.md`
- `packaging/hooks/.gitkeep`
- `packaging/installer/resources/.gitkeep`
- `packaging/scripts/.gitkeep`

---

### task-1.2: Añadir extra `[packaging]` en `pyproject.toml`

**Tipo:** chore
**Estimación:** 0.5h
**Bloquea:** task-2.4
**Bloqueada por:** task-1.1

**Descripción:** Añadir `[project.optional-dependencies]` con `packaging = ["pyinstaller>=6.3", "pyside6>=6.6"]` en `pyproject.toml`. Si no existen ya, también declarar el script de consola `tempify-cli` en `[project.scripts]` (REQ-010, REQ-011).

**Criterio de done:**
- [ ] `pip install -e ".[packaging]"` instala PyInstaller >= 6.3 y PySide6 >= 6.6.
- [ ] `pip install -e ".[gui,packaging]"` resuelve sin conflictos.
- [ ] `pip install tempify` (sin extras) sigue funcionando (REQ-010).

**Archivos:**
- `pyproject.toml`

---

### task-1.3: Esqueleto `packaging/pyinstaller.spec`

**Tipo:** impl
**Estimación:** 2h
**Bloquea:** task-2.1, task-2.4
**Bloqueada por:** task-1.1

**Descripción:** Crear el `.spec` con dos targets (`tempify-gui` console=False, `tempify-cli` console=True), modo `--onedir`, `hookspath=['packaging/hooks']`, `datas` con perfiles YAML, `excludes` agresivos (`tkinter`, `unittest`, `PySide6.QtWebEngineWidgets`, `PySide6.QtMultimedia`, `PySide6.QtQuick`, `matplotlib.tests`). Nombre del COLLECT: `tempify-0.1.0`. Icono apuntando a `packaging/installer/resources/tempify.ico` (creado en task-2.3).

**Criterio de done:**
- [ ] `pyinstaller --noconfirm packaging/pyinstaller.spec` corre sin error sintáctico (puede fallar por hooks aún no completos).
- [ ] Comentarios NumPy-style explican cada bloque y referencia a los REQ que satisface.
- [ ] Variable `APP_VERSION` parametrizable desde entorno (default `0.1.0`).

**Archivos:**
- `packaging/pyinstaller.spec`

---

### task-1.4: Hook `hook-rasterio.py`

**Tipo:** impl
**Estimación:** 1h
**Bloquea:** task-2.10
**Bloqueada por:** task-1.1

**Descripción:** Implementar el hook PyInstaller para `rasterio`: `collect_data_files('rasterio', includes=['gdal_data/*'])` + `collect_dynamic_libs('rasterio')` + `hiddenimports` para submódulos comunes (`rasterio._shim`, `rasterio.vrt`, `rasterio.sample`, `rasterio.crs`).

**Criterio de done:**
- [ ] Archivo respeta convención `hook-<pkg>.py`.
- [ ] Imports en topo del archivo: `from PyInstaller.utils.hooks import ...`.
- [ ] Comentario referenciando REQ-003.

**Archivos:**
- `packaging/hooks/hook-rasterio.py`

---

### task-1.5: Hook `hook-pyproj.py`

**Tipo:** impl
**Estimación:** 1h
**Bloquea:** task-2.10
**Bloqueada por:** task-1.1

**Descripción:** Hook para `pyproj`: `collect_data_files('pyproj', includes=['proj_data/*'])` + `collect_submodules('pyproj')` para asegurar `pyproj.network`, `pyproj.transformer`, `pyproj.crs`.

**Criterio de done:**
- [ ] Hook resuelve `proj_data` (proj.db, grid shifts).
- [ ] Comentario referenciando REQ-003.

**Archivos:**
- `packaging/hooks/hook-pyproj.py`

---

### task-1.6: Hook `hook-PySide6.py` con exclusiones

**Tipo:** impl
**Estimación:** 1.5h
**Bloquea:** task-2.10, task-2.11
**Bloqueada por:** task-1.1

**Descripción:** Hook para PySide6 incluyendo solo `QtCore`, `QtGui`, `QtWidgets`, plugin de plataforma `windows`, traducciones `qt_es.qm` y `qt_en.qm`. `excludedimports` para `QtWebEngineWidgets`, `QtMultimedia`, `QtQuick`, `QtCharts`, `Qt3DCore`, `QtNetwork` SSL backends. Apunta a control de tamaño (NFR-002).

**Criterio de done:**
- [ ] Lista de exclusiones documentada con comentario por cada módulo.
- [ ] Tamaño post-build de `_internal/PySide6/` < 80 MB (verificable en task-2.11).

**Archivos:**
- `packaging/hooks/hook-PySide6.py`

---

### task-1.7: Hook `hook-netcdf4.py`

**Tipo:** impl
**Estimación:** 1h
**Bloquea:** task-2.10
**Bloqueada por:** task-1.1

**Descripción:** Hook para `netCDF4`: `collect_dynamic_libs('netCDF4')` + HDF5 DLLs transitivos (`hdf5.dll`, `libcurl.dll`, `zlib1.dll`). Documentar las DLLs detectadas en comentarios.

**Criterio de done:**
- [ ] Hook captura HDF5 transitivo (verificable con `dumpbin /dependents` post-build).
- [ ] Comentario referenciando REQ-003.

**Archivos:**
- `packaging/hooks/hook-netcdf4.py`

---

### task-1.8: Documentar AppId GUID estable

**Tipo:** docs
**Estimación:** 0.5h
**Bloquea:** task-2.1
**Bloqueada por:** task-1.1

**Descripción:** Crear `packaging/installer/APPID.md` documentando el GUID `{{B7A21C3D-4E5F-4A8B-9C2D-1F3E5A7B9C0D}}`, su propósito (detección de upgrades en Inno Setup, REQ-009), y advertencia explícita de NUNCA cambiarlo entre versiones. Validar formato GUID v4.

**Criterio de done:**
- [ ] GUID inmutable documentado.
- [ ] Advertencia visible en negrita.
- [ ] Referencia cruzada al ADR-0006 y a `installer.iss`.

**Archivos:**
- `packaging/installer/APPID.md`

---

## Fase 2: Incremental (build, instalador, CI, tests)

### task-2.1: Script `installer.iss` Inno Setup en español

**Tipo:** impl
**Estimación:** 3.5h
**Bloquea:** task-2.7, task-2.13, task-2.14
**Bloqueada por:** task-1.3, task-1.8, task-2.2, task-2.3

**Descripción:** Implementar `packaging/installer.iss` con:
- `[Setup]`: AppId (task-1.8), AppName, AppVersion (parametrizable `{#AppVersion}`), `DefaultDirName={autopf}\tempify`, `PrivilegesRequired=lowest` con `PrivilegesRequiredOverridesAllowed=dialog`, `Compression=lzma2/ultra64`, `SolidCompression=yes`, `WizardStyle=modern`, `OutputBaseFilename=tempify-{#AppVersion}-win64-setup`.
- `[Languages]`: única entrada `spanish` desde `compiler:Languages\Spanish.isl` (REQ-004).
- `[Files]`: recursive copy de `dist\tempify-0.1.0\*`.
- `[Icons]`: shortcut menú inicio "tempify" → `tempify-gui.exe`; desktop shortcut opt-in vía Tasks.
- `[Tasks]`: `desktopicon` (opt-in), `associate_nc` (desmarcado), `associate_tif` (desmarcado) (REQ-006).
- `[Registry]`: entradas condicionales a Tasks para asociaciones `.nc` y `.tif`.
- `[Run]`: VC++ runtime auto-install condicional a per-machine (REQ-007).
- `[UninstallDelete]`: limitado a `{app}` sin tocar `%APPDATA%` (REQ-008).
- `[Code]`: rutina `InitializeSetup` que detecta instalación previa por AppId y preserva `%APPDATA%\tempify\config.yaml` (REQ-009).

**Criterio de done:**
- [ ] `iscc /Q packaging/installer.iss /DAppVersion=0.1.0` compila sin error.
- [ ] El instalador resultante presenta wizard en español.
- [ ] Tasks de asociación están desmarcadas por default.

**Archivos:**
- `packaging/installer.iss`

---

### task-2.2: Recurso `installer/resources/icon.ico` (placeholder)

**Tipo:** chore
**Estimación:** 0.5h
**Bloquea:** task-2.1
**Bloqueada por:** task-1.1

**Descripción:** Añadir icono placeholder `tempify.ico` (16x16, 32x32, 48x48, 256x256) en `packaging/installer/resources/`. Generado desde un PNG simple con `magick convert` o equivalente. Documentar en comentario del recurso que es placeholder a sustituir antes de release final.

**Criterio de done:**
- [ ] `tempify.ico` válido (verificable con `file` o `magick identify`).
- [ ] README en `packaging/installer/resources/` indica origen y carácter de placeholder.

**Archivos:**
- `packaging/installer/resources/tempify.ico`
- `packaging/installer/resources/README.md`

---

### task-2.3: Recurso `installer/resources/LICENSE-es.rtf`

**Tipo:** chore
**Estimación:** 0.5h
**Bloquea:** task-2.1
**Bloqueada por:** task-1.1

**Descripción:** Convertir el archivo `LICENSE` (MIT) a `.rtf` en español neutral. El wizard Inno Setup lo presentará en la página de licencia. Usar `pandoc -f markdown -t rtf` o equivalente.

**Criterio de done:**
- [ ] RTF válido (abre en WordPad sin errores).
- [ ] Texto MIT traducido al español.
- [ ] Encoding UTF-8 sin BOM en el .iss correspondiente.

**Archivos:**
- `packaging/installer/resources/LICENSE-es.rtf`

---

### task-2.4: Script `build_windows.ps1`

**Tipo:** impl
**Estimación:** 3h
**Bloquea:** task-2.5, task-2.6, task-2.7, task-2.10, task-2.11
**Bloqueada por:** task-1.2, task-1.3

**Descripción:** Implementar el orquestador local descrito en design §5.1. Etapas: setup venv, `pip install -e ".[gui,packaging,dev]"` con fail-fast si extras faltan (REQ-012), `pytest -m "not slow"`, limpieza, PyInstaller, validación footprint (< 280 MB bundle, NFR-002), Inno Setup `iscc`, SHA256 sum a `Output/SHA256SUMS.txt` (REQ-014). Setear `SOURCE_DATE_EPOCH` desde `git log -1 --format=%ct` para reproducibilidad (REQ-013). `$ErrorActionPreference = 'Stop'`. Salida con códigos de exit claros.

**Criterio de done:**
- [ ] Script termina con exit 0 en build limpia.
- [ ] Falla con exit != 0 y mensaje claro si extras `[gui]` o `[packaging]` faltan (REQ-012).
- [ ] Genera `Output/tempify-0.1.0-win64-setup.exe` y `Output/SHA256SUMS.txt`.
- [ ] Honra `$env:APP_VERSION` si está seteada.

**Archivos:**
- `packaging/scripts/build_windows.ps1`

---

### task-2.5: Script `verify_sha256.ps1` (REQ-013)

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-2.12
**Bloqueada por:** task-2.4

**Descripción:** Implementar el algoritmo descrito en design §5.2: doble build con limpieza intermedia, hash de ambos `.exe`, exit 1 si difieren con diagnóstico de archivos divergentes dentro del bundle (extracción temporal y `Get-FileHash` por archivo).

**Criterio de done:**
- [ ] Exit 0 si hashes coinciden.
- [ ] Exit 1 con listado de archivos cuyo hash difiere en caso de fallo.
- [ ] Tiempo total documentado (esperado ~10 min).

**Archivos:**
- `packaging/scripts/verify_sha256.ps1`

---

### task-2.6: Script `smoke_test.ps1`

**Tipo:** test
**Estimación:** 2.5h
**Bloquea:** task-2.12
**Bloqueada por:** task-2.4

**Descripción:** Implementar el flujo de design §5.3: install silencioso per-user, verificación de shortcut, medición de cold start (NFR-001, < 5 s), ejecución headless con fixture `tests/fixtures/worldclim_chile_mini/`, verificación de output no vacío, uninstall silencioso, verificación de preservación de outputs fuera de install dir (REQ-008) y de `%APPDATA%\tempify\config.yaml` (REQ-009).

**Criterio de done:**
- [ ] Exit 0 en smoke verde.
- [ ] Falla explícita si cold start > 5 s.
- [ ] No deja residuos tras uninstall (verifica con `Test-Path`).

**Archivos:**
- `packaging/scripts/smoke_test.ps1`

---

### task-2.7: Workflow CI `.github/workflows/build-windows.yml`

**Tipo:** impl
**Estimación:** 3h
**Bloquea:** task-2.12, task-2.15
**Bloqueada por:** task-2.1, task-2.4

**Descripción:** Crear el workflow con triggers `push: tags: ['v*']` + `workflow_dispatch`. Jobs declarados en design §5.5:
1. `build` (windows-2022, Python 3.11, `choco install innosetup --version=6.2.2 -y`, ejecuta `build_windows.ps1`, sube artifact).
2. `reproducibility` (ejecuta `verify_sha256.ps1`).
3. `smoke` (descarga artifact, ejecuta `smoke_test.ps1`).
4. `pip-coexistence` (verifica REQ-010 parte B).
5. `release` (solo tags, `softprops/action-gh-release@v2`, sube `.exe` + `SHA256SUMS.txt`).

`runs-on: windows-2022` pineado, no `windows-latest` (REQ-002).

**Criterio de done:**
- [ ] YAML valida con `actionlint` localmente.
- [ ] Tag de prueba en branch dispara workflow exitosamente.
- [ ] Dependencias entre jobs declaradas (`needs:`).

**Archivos:**
- `.github/workflows/build-windows.yml`

---

### task-2.8: Configurar `SOURCE_DATE_EPOCH` en build script

**Tipo:** impl
**Estimación:** 1h
**Bloquea:** task-2.5
**Bloqueada por:** task-2.4

**Descripción:** Ampliar `build_windows.ps1` para setear `$env:SOURCE_DATE_EPOCH = (git log -1 --format=%ct)`, pasar `--strip` deshabilitado a PyInstaller, y configurar Inno Setup `--% /Q` para suprimir timestamps de UI. Documentar en comentario del script que esto es requisito para REQ-013.

**Criterio de done:**
- [ ] Variable seteada antes de invocar `pyinstaller` e `iscc`.
- [ ] Comentario referencia REQ-013 y design §5.2.
- [ ] `verify_sha256.ps1` (task-2.5) pasa después del cambio.

**Archivos:**
- `packaging/scripts/build_windows.ps1`

---

### task-2.9: Inclusión de perfiles YAML vía hook runtime

**Tipo:** impl
**Estimación:** 1.5h
**Bloquea:** task-2.10
**Bloqueada por:** task-1.3

**Descripción:** Asegurar que los perfiles YAML de variables (`src/tempify/profiles/*.yaml`) se incluyan en el bundle bajo `share/tempify/profiles/` y sean accesibles via `importlib.resources` en runtime. Añadir entrada `datas` en `pyinstaller.spec` y un test ligero en `packaging/hooks/hook-tempify-profiles.py` que use `collect_data_files('tempify.profiles')` para redundancia.

**Criterio de done:**
- [ ] `dist/tempify-0.1.0/share/tempify/profiles/temperature.yaml` existe tras build.
- [ ] `tempify-cli.exe --list-profiles` (si existe el comando, o equivalente headless) los enumera.

**Archivos:**
- `packaging/pyinstaller.spec`
- `packaging/hooks/hook-tempify-profiles.py`

---

### task-2.10: Test `test_bundle_contains_gdal_proj_qt` (REQ-003)

**Tipo:** test
**Estimación:** 1h
**Bloquea:** task-2.12
**Bloqueada por:** task-1.4, task-1.5, task-1.6, task-1.7, task-2.4, task-2.9

**Descripción:** Script PowerShell `packaging/scripts/test_bundle_contents.ps1` que tras un build verifica existencia de `_internal/rasterio/gdal_data/gdal-data` (cualquier file), `_internal/pyproj/proj_data/proj.db`, `_internal/PySide6/plugins/platforms/qwindows.dll`, `_internal/PySide6/translations/qt_es.qm`, y `share/tempify/profiles/temperature.yaml`. Invocable independiente y desde CI.

**Criterio de done:**
- [ ] Exit 0 si todos los recursos presentes.
- [ ] Exit 1 con lista de recursos faltantes.
- [ ] Integrado al job `build` o `smoke` del workflow.

**Archivos:**
- `packaging/scripts/test_bundle_contents.ps1`

---

### task-2.11: Test `test_bundle_size_under_300mb` (NFR-002)

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** task-2.12
**Bloqueada por:** task-2.4

**Descripción:** Script PowerShell `packaging/scripts/test_bundle_size.ps1` que verifica `(Get-Item Output\*.exe).Length -lt 300MB` y separadamente `(Get-ChildItem -Recurse dist\tempify-0.1.0\ | Measure-Object Length -Sum).Sum -lt 280MB`. Reporta tamaño en MB.

**Criterio de done:**
- [ ] Exit 0 si ambos umbrales se cumplen.
- [ ] Salida claramente formateada con tamaños actuales y umbrales.
- [ ] Integrado al job `build` del workflow.

**Archivos:**
- `packaging/scripts/test_bundle_size.ps1`

---

### task-2.12: Tests CI restantes consolidados

**Tipo:** test
**Estimación:** 4h
**Bloquea:** task-2.15
**Bloqueada por:** task-2.5, task-2.6, task-2.7, task-2.10, task-2.11

**Descripción:** Implementar los scripts PowerShell auxiliares invocados por el workflow para los siguientes tests:
- `test_pip_exe_coexistence.ps1` (REQ-010 parte B).
- `test_installer_language_es.ps1` (REQ-004, vía inspección del `.iss` compilado o UI automation con PyAutoGui).
- `test_uninstall_preserves_user_outputs.ps1` (REQ-008).
- `test_upgrade_preserves_config.ps1` (REQ-009).
- `test_sha256_reproducible.ps1` (wrapper de `verify_sha256.ps1`, NFR-005/REQ-013).
- `test_per_user_vs_per_machine.ps1` (REQ-005).
- `test_file_association_optional.ps1` (REQ-006).
- `test_build_fails_without_gui_extras.ps1` (REQ-012).

Cada script con exit codes claros y mensajes diagnóstico.

**Criterio de done:**
- [ ] 8 scripts creados, todos invocables independientemente.
- [ ] Cada script declarado en su job correspondiente del workflow CI.
- [ ] Cada criterio de aceptación de requirements §6 mapeado a uno de estos scripts.

**Archivos:**
- `packaging/scripts/test_pip_exe_coexistence.ps1`
- `packaging/scripts/test_installer_language_es.ps1`
- `packaging/scripts/test_uninstall_preserves_user_outputs.ps1`
- `packaging/scripts/test_upgrade_preserves_config.ps1`
- `packaging/scripts/test_sha256_reproducible.ps1`
- `packaging/scripts/test_per_user_vs_per_machine.ps1`
- `packaging/scripts/test_file_association_optional.ps1`
- `packaging/scripts/test_build_fails_without_gui_extras.ps1`

---

### task-2.13: Generación y upload de `SHA256SUMS.txt` (REQ-014)

**Tipo:** impl
**Estimación:** 0.5h
**Bloquea:** task-2.15
**Bloqueada por:** task-2.1, task-2.4, task-2.7

**Descripción:** Ampliar el job `release` del workflow CI para que suba `SHA256SUMS.txt` como asset junto al `.exe`. El archivo ya se genera en `build_windows.ps1` paso 7; aquí solo se asegura que `softprops/action-gh-release@v2` lo incluya en `files:`.

**Criterio de done:**
- [ ] Tag de prueba genera release con dos assets: `.exe` y `SHA256SUMS.txt`.
- [ ] Contenido del `SHA256SUMS.txt` validable con `sha256sum -c` (Linux) o `Get-FileHash` (Windows).

**Archivos:**
- `.github/workflows/build-windows.yml`

---

### task-2.14: Asociaciones `.nc` / `.tif` como `[Tasks]` opt-in

**Tipo:** impl
**Estimación:** 1h
**Bloquea:** —
**Bloqueada por:** task-2.1

**Descripción:** Verificar y completar las entradas `[Tasks]` y `[Registry]` condicionales en `installer.iss` para `.nc` y `.tif`. Ambas `Flags: unchecked` por default (REQ-006, design Decisión 6). Registro debe usar `HKA` (resuelve HKCU o HKLM según modo) para coexistir con QGIS sin sobrescribir handlers existentes.

**Criterio de done:**
- [ ] Wizard muestra dos checkboxes desmarcadas: "Asociar archivos .nc con tempify" y "Asociar archivos .tif con tempify".
- [ ] Sin marcar → registry no toca handlers existentes.
- [ ] Test `test_file_association_optional.ps1` (task-2.12) verde.

**Archivos:**
- `packaging/installer.iss`

---

## Fase 3: Documentación e integración

### task-3.1: Sección README "Instalación Windows"

**Tipo:** docs
**Estimación:** 1.5h
**Bloquea:** task-3.5
**Bloqueada por:** task-2.7

**Descripción:** Añadir al `README.md` raíz una sección "Instalación" con dos rutas: (a) usuario final descarga el `.exe` desde GitHub Releases, verifica SHA256 contra `SHA256SUMS.txt`, ejecuta el instalador; (b) desarrollador usa `pip install tempify`. Documentar plataformas soportadas (NFR-004: Windows 10 19041+, Windows 11 22H2+).

**Criterio de done:**
- [ ] Sección visible y enlazada desde índice del README.
- [ ] Incluye comando `Get-FileHash -Algorithm SHA256` de ejemplo.
- [ ] Mención de la coexistencia pip + .exe (REQ-010).

**Archivos:**
- `README.md`

---

### task-3.2: Plan de pruebas manuales (release gate)

**Tipo:** docs
**Estimación:** 1.5h
**Bloquea:** task-3.5
**Bloqueada por:** task-2.7

**Descripción:** Crear `specs/packaging/manual-test-plan.md` con el checklist de smoke manual descrito en design §7 "Pruebas manuales (release gate)": VM Win10 22H2 limpia, VM Win11 23H2 limpia, máquina con QGIS preinstalado. Cada test con pasos numerados, datos de entrada, criterios de éxito y casillas para evidencia (screenshots, hashes).

**Criterio de done:**
- [ ] 3 escenarios documentados.
- [ ] Checklist con casillas markdown.
- [ ] Sección "Resultado" con tabla VM / fecha / operador / status.

**Archivos:**
- `specs/packaging/manual-test-plan.md`

---

### task-3.3: Documentar workaround SmartScreen

**Tipo:** docs
**Estimación:** 0.5h
**Bloquea:** task-3.5
**Bloqueada por:** task-3.1

**Descripción:** Añadir al README (o sub-doc enlazado) la nota explicativa sobre el warning de SmartScreen al ejecutar el `.exe` no firmado: instrucciones "Más información" → "Ejecutar de todas formas", explicación de por qué (v0.1.0 sin code-signing, ADR diferida), y mención de la verificación SHA256 como medida compensatoria (REQ-014).

**Criterio de done:**
- [ ] Sección visible en README o `docs/installation-windows.md`.
- [ ] Screenshot del diálogo SmartScreen (opcional pero recomendado).
- [ ] Plan de migración a code-signing referenciado (v0.2.0).

**Archivos:**
- `README.md` o `docs/installation-windows.md`

---

### task-3.4: Actualizar `CHANGELOG.md`

**Tipo:** docs
**Estimación:** 0.5h
**Bloquea:** task-3.5
**Bloqueada por:** task-2.7

**Descripción:** Añadir entrada `## [0.1.0] — YYYY-MM-DD` en `CHANGELOG.md` listando el nuevo artefacto Windows: instalador `.exe`, `SHA256SUMS.txt`, mantenimiento de `pip install tempify`. Referenciar ADR-0006 y esta spec.

**Criterio de done:**
- [ ] Entrada respeta formato Keep-a-Changelog.
- [ ] Lista los REQ cubiertos como bullets de "Added".

**Archivos:**
- `CHANGELOG.md`

---

### task-3.5: Cerrar `impl-log.md`

**Tipo:** docs
**Estimación:** 1h
**Bloquea:** —
**Bloqueada por:** task-3.1, task-3.2, task-3.3, task-3.4

**Descripción:** Actualizar `specs/packaging/impl-log.md` con bitácora cronológica: tasks completadas, decisiones desviadas del design (si hubo), hashes de instaladores de prueba, métricas finales (tamaño bundle, cold start medido, tiempo total de build CI). Marcar spec como `Complete` en su header al final.

**Criterio de done:**
- [ ] Entrada por cada task de Fase 1 y 2 con fecha y commit hash.
- [ ] Métricas finales tabuladas contra umbrales de NFR.
- [ ] Spec en `Approved` → `Complete` al cierre.

**Archivos:**
- `specs/packaging/impl-log.md`

---

## Resumen

| Fase | # tasks | Estimación total |
|---|---|---|
| Fase 1 | 8 | 8.0h |
| Fase 2 | 14 | 26.0h |
| Fase 3 | 5 | 5.0h |
| **Total** | **27** | **39.0h** |

## Trazabilidad tasks → requirements

| Requirement | Tasks que contribuyen |
|---|---|
| REQ-001 | task-1.3, task-2.1, task-2.6 |
| REQ-002 | task-2.7 |
| REQ-003 | task-1.4, task-1.5, task-1.6, task-1.7, task-2.9, task-2.10 |
| REQ-004 | task-2.1, task-2.3, task-2.12 |
| REQ-005 | task-2.1, task-2.12 |
| REQ-006 | task-2.1, task-2.14, task-2.12 |
| REQ-007 | task-2.1 |
| REQ-008 | task-2.1, task-2.6, task-2.12 |
| REQ-009 | task-1.8, task-2.1, task-2.6, task-2.12 |
| REQ-010 | task-1.2, task-2.12 |
| REQ-011 | task-1.2, task-2.7 |
| REQ-012 | task-2.4, task-2.12 |
| REQ-013 | task-2.5, task-2.8, task-2.12 |
| REQ-014 | task-2.4, task-2.13 |
| NFR-001 | task-2.6 |
| NFR-002 | task-1.6, task-2.4, task-2.11 |
| NFR-003 | task-2.6, task-2.7 |
| NFR-004 | task-3.1, task-3.2 |
| NFR-005 | task-1.1 a task-2.14 (versionado en git) |
| NFR-006 | n/a en v0.1.0 (sin código Python auxiliar) |
