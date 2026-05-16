# Design — packaging

**Estado:** Draft
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-15

## 1. Visión técnica

El sistema de packaging produce un instalador `.exe` autocontenido para Windows 10/11 x64 que distribuye la GUI y la CLI de tempify a usuarios finales sin Python instalado. La estrategia se apoya en dos herramientas complementarias y desacopladas (ver ADR-0006): PyInstaller en modo `--onedir` materializa un bundle reproducible con todas las dependencias Python, recursos GDAL/PROJ y plugins Qt necesarios, e Inno Setup 6.x envuelve ese bundle en un wizard nativo Windows con textos en español, accesos directos, asociaciones opt-in y manejo del runtime VC++.

Toda la maquinaria vive en una carpeta `packaging/` en la raíz del repositorio, que **no es un módulo Python importable** sino un conjunto de scripts (PyInstaller spec, hooks de runtime, script Inno Setup, scripts PowerShell de build y verificación). La distribución `pip install tempify` permanece intacta y se garantiza la coexistencia con el ejecutable instalado (REQ-010). El build se ejecuta en GitHub Actions sobre runner pineado `windows-2022` (REQ-002, REQ-013) y publica además un `SHA256SUMS.txt` que compensa la ausencia de code-signing en v0.1.0 (REQ-014, ADR-0013 diferida).

## 2. Arquitectura propuesta

### Diagrama de componentes

```
repo-root/
├── pyproject.toml                      (extra [packaging] añadido)
├── src/tempify/                        (código runtime, sin cambios)
├── packaging/                          (NUEVO; no es paquete Python)
│   ├── pyinstaller.spec                ─┐
│   ├── hooks/                           │  PyInstaller stage
│   │   ├── hook-rasterio.py             │  produces:
│   │   ├── hook-pyproj.py               │  dist/tempify-0.1.0/
│   │   ├── hook-PySide6.py              │   ├── tempify-gui.exe
│   │   └── hook-netcdf4.py             ─┘   ├── tempify-cli.exe
│   │                                        ├── python311.dll
│   ├── installer.iss                   ─┐   ├── _internal/
│   ├── installer/                       │   │    ├── rasterio/gdal_data/
│   │   └── resources/                   │   │    ├── pyproj/proj_data/
│   │       ├── tempify.ico              │   │    └── PySide6/translations/
│   │       ├── LICENSE-es.txt           │   └── share/tempify/profiles/*.yaml
│   │       └── wizard-banner.bmp        │
│   │                                    │  Inno Setup stage
│   │                                    │  produces:
│   │                                    │  Output/tempify-0.1.0-win64-setup.exe
│   │                                   ─┘
│   └── scripts/
│       ├── build_windows.ps1
│       ├── verify_sha256.ps1
│       └── smoke_test.ps1
│
└── .github/workflows/
    └── build-windows.yml                (CI orchestration)
```

### Componentes nuevos (todos artefactos de build, no Python runtime)

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| `pyinstaller.spec` | `packaging/pyinstaller.spec` | Declara dos targets (`tempify-gui` console=False, `tempify-cli` console=True), módulos ocultos, exclusiones, recursos a copiar, modo `--onedir`. |
| `hook-rasterio.py` | `packaging/hooks/` | `collect_data_files('rasterio', includes=['gdal_data/*'])` + `collect_dynamic_libs`. |
| `hook-pyproj.py` | `packaging/hooks/` | `collect_data_files('pyproj', subdir='proj_data')` y `collect_submodules`. |
| `hook-PySide6.py` | `packaging/hooks/` | Inclusión de `QtCore`, `QtGui`, `QtWidgets`, plataforma `windows`, traducciones es/en; exclusión de QtWebEngine, QtMultimedia, QtQuick, QtNetwork SSL backends no usados. |
| `hook-netcdf4.py` | `packaging/hooks/` | `collect_dynamic_libs('netCDF4')` + HDF5 DLLs transitivos. |
| `installer.iss` | `packaging/installer.iss` | Script Inno Setup 6.x: secciones `[Setup]`, `[Languages]` (spanish.isl), `[Files]`, `[Icons]`, `[Tasks]` (asociaciones opt-in, desktop shortcut opt-in), `[Run]` (VC++ runtime), `[UninstallDelete]`, `[Code]` (detección de instalación previa y preservación `%APPDATA%`). |
| `installer/resources/` | `packaging/installer/resources/` | Icono `.ico`, licencia traducida `LICENSE-es.txt`, banner del wizard (BMP 164x314 y 55x58). |
| `build_windows.ps1` | `packaging/scripts/` | Orquestador local del build end-to-end. |
| `verify_sha256.ps1` | `packaging/scripts/` | Doble build + diff de SHA256 para REQ-013. |
| `smoke_test.ps1` | `packaging/scripts/` | Instalación silenciosa, ejecución headless, validación de output, desinstalación. |
| `build-windows.yml` | `.github/workflows/` | Workflow CI disparado por tag `v*`, runner `windows-2022`. |

### Componentes modificados

| Componente | Ubicación | Cambio |
|---|---|---|
| `pyproject.toml` | raíz | Añadir extra `[project.optional-dependencies] packaging = ["pyinstaller>=6.3", "pyside6>=6.6"]`. Declarar `[project.scripts] tempify-cli = "tempify.cli:app"` (alias para console exe). |
| `README.md` | raíz | Sección de instalación con dos vías: `.exe` para usuarios finales (incluye nota de SmartScreen y verificación SHA256) y `pip` para desarrolladores. Documentar plataformas soportadas (NFR-004). |
| `CHANGELOG.md` | raíz | Entrada v0.1.0 con artefacto Windows. |

## 3. Contratos del bundle y del instalador

### 3.1 Contrato del bundle PyInstaller

El directorio `dist/tempify-0.1.0/` producido por PyInstaller debe satisfacer la siguiente estructura mínima, verificada por `smoke_test.ps1`:

```
tempify-0.1.0/
├── tempify-gui.exe                         (Windows GUI subsystem, no console)
├── tempify-cli.exe                         (console subsystem, hereda stdout)
├── python311.dll
├── _internal/
│   ├── base_library.zip
│   ├── rasterio/
│   │   └── gdal_data/                      (PROJ.4 y GDAL data files)
│   ├── pyproj/
│   │   └── proj_data/                      (proj.db, grid shifts)
│   ├── PySide6/
│   │   ├── plugins/platforms/qwindows.dll
│   │   ├── plugins/imageformats/
│   │   └── translations/qt_es.qm
│   ├── netCDF4/                            (con hdf5.dll, libcurl.dll embebidos)
│   ├── scipy/
│   ├── numpy/
│   └── tempify/                            (paquete propio, .pyc compilados)
└── share/tempify/
    └── profiles/                           (perfiles de variable YAML)
        ├── temperature.yaml
        ├── precipitation.yaml
        └── *.yaml
```

**Pre-condiciones del bundle:** entorno virtual con `tempify[gui,packaging]` instalado, `pytest -m "not slow"` verde.
**Post-condiciones:** ejecutar `tempify-gui.exe` arranca la GUI sin Python en el sistema; ejecutar `tempify-cli.exe --version` imprime `tempify 0.1.0`.
**Excepciones de build:** `BuildAbort` si PyInstaller no resuelve un hook crítico (REQ-012); `SizeExceeded` si el tamaño total excede 300 MB (NFR-002, abortado por `build_windows.ps1` antes de invocar Inno Setup).

### 3.2 Contrato del instalador Inno Setup

El artefacto final `tempify-0.1.0-win64-setup.exe` (Output Inno Setup) debe:

**Modos de instalación:**

| Modo | Directorio destino | Privilegios | VC++ runtime |
|---|---|---|---|
| Per-machine (default) | `%ProgramFiles%\tempify\` | Admin | Auto-install via `[Run]` si falta |
| Per-user (opt-in) | `%LOCALAPPDATA%\Programs\tempify\` | Usuario | Omite VC++; GUI da error explícito si falta |

**Items siempre creados:** shortcut "tempify" en menú inicio que apunta a `tempify-gui.exe`.

**Items opt-in mediante `[Tasks]` checkboxes en wizard:**
- Desktop shortcut.
- Asociación `.nc` → `tempify-gui.exe %1`.
- Asociación `.tif` → `tempify-gui.exe %1`.

**Comportamiento de upgrade:** detección de instalación previa por `AppId` GUID estable; preservación del archivo `%APPDATA%\tempify\config.yaml` y del directorio `%APPDATA%\tempify\` completo (REQ-009).

**Comportamiento de uninstall:** elimina `%ProgramFiles%\tempify\` o `%LOCALAPPDATA%\Programs\tempify\`, los shortcuts y las asociaciones registradas; **no toca** `%APPDATA%\tempify\` ni archivos generados por el usuario fuera del install dir (REQ-008).

**Idioma:** todos los textos del wizard en español (welcome, license, install path, ready, finish), declarados en `[Languages]` con `spanish.isl` como única entrada (REQ-004).

## 4. Modelos de datos

No aplica modelos Python en esta spec (packaging no introduce código de runtime). Los "modelos" relevantes son los archivos de configuración del propio empaquetado:

### `pyinstaller.spec` (estructura conceptual)

```
Analysis(
    scripts=['src/tempify/gui/__main__.py', 'src/tempify/cli/__main__.py'],
    pathex=[...],
    binaries=[],
    datas=[('src/tempify/profiles/*.yaml', 'share/tempify/profiles')],
    hiddenimports=['rasterio._shim', 'rasterio.vrt', 'pyproj.network', ...],
    hookspath=['packaging/hooks'],
    excludes=['tkinter', 'unittest', 'PySide6.QtWebEngineWidgets',
              'PySide6.QtMultimedia', 'PySide6.QtQuick', 'matplotlib.tests'],
)
EXE(name='tempify-gui', console=False, icon='packaging/installer/resources/tempify.ico')
EXE(name='tempify-cli', console=True,  icon='packaging/installer/resources/tempify.ico')
COLLECT(name='tempify-0.1.0')   # onedir
```

### Variables de Inno Setup (`installer.iss`)

| Variable | Valor |
|---|---|
| `AppId` | `{{F2A5C8E1-7B3D-4F2A-9E1C-TEMPIFY00001}}` (GUID estable para upgrades) |
| `AppName` | `tempify` |
| `AppVersion` | `0.1.0` (sustituido por CI desde tag) |
| `AppPublisher` | `Guillermo Fuentes-Jaque` |
| `DefaultDirName` | `{autopf}\tempify` (resuelve per-machine vs per-user) |
| `PrivilegesRequired` | `lowest` con `PrivilegesRequiredOverridesAllowed=dialog` |
| `OutputBaseFilename` | `tempify-{#AppVersion}-win64-setup` |
| `Compression` | `lzma2/ultra64` |
| `SolidCompression` | `yes` |
| `WizardStyle` | `modern` |

## 5. Algoritmos clave (scripts de build y verificación)

### 5.1 `build_windows.ps1` — orquestador local

Ejecutado tanto por el desarrollador en su máquina como por el job de CI. Etapas:

1. **Setup del entorno.** Crea venv limpio `.venv-build/`, activa, ejecuta `pip install --upgrade pip` y luego `pip install -e ".[gui,packaging,dev]"`. Falla con mensaje claro si los extras `gui` o `packaging` no están declarados (REQ-012).
2. **Tests rápidos.** Ejecuta `pytest -m "not slow"`. Si falla, aborta el build.
3. **Limpieza de artefactos previos.** Borra `build/`, `dist/`, `Output/`.
4. **PyInstaller.** Ejecuta `pyinstaller --clean --noconfirm packaging/pyinstaller.spec`. Verifica que `dist/tempify-0.1.0/tempify-gui.exe` y `dist/tempify-0.1.0/tempify-cli.exe` existen.
5. **Validación de footprint.** Calcula tamaño total de `dist/tempify-0.1.0/`. Aborta si excede 300 MB (NFR-002 con margen para el comprimido Inno).
6. **Inno Setup.** Ejecuta `iscc packaging/installer.iss /DAppVersion=0.1.0`. Verifica que `Output/tempify-0.1.0-win64-setup.exe` existe y es < 300 MB.
7. **Checksum.** Calcula `Get-FileHash -Algorithm SHA256` del `.exe` y lo escribe en `Output/SHA256SUMS.txt` con formato `<hash>  tempify-0.1.0-win64-setup.exe`.

**Complejidad:** lineal en tamaño del bundle; tiempo dominante = PyInstaller (~3-5 min en `windows-2022`).
**Trade-offs:** invocar pytest en cada build encarece ~1 min pero detecta regresiones antes de gastar tiempo en PyInstaller; aceptable.

### 5.2 `verify_sha256.ps1` — reproducibilidad bit-exact (REQ-013)

1. Ejecuta `build_windows.ps1`, guarda el SHA256 en `$hash1`.
2. Limpia `build/`, `dist/`, `Output/`.
3. Ejecuta `build_windows.ps1` nuevamente, guarda el SHA256 en `$hash2`.
4. Compara: si `$hash1 -ne $hash2`, exit code 1 con diagnóstico (lista de archivos con timestamps divergentes dentro del bundle, usando `(Get-FileHash) sobre cada archivo del unzip`).

**Notas de reproducibilidad:** PyInstaller emite timestamps en PE headers; se mitiga con la variable `SOURCE_DATE_EPOCH` derivada del commit del tag y con `--strip` deshabilitado para mantener determinismo. Inno Setup también acepta `SignTool` y `OutputManifestFile` para auditoría; en este caso usamos `--% /Q` (silent) y dependemos de que el contenido sea idéntico (lzma2 es determinístico dado mismo input).

### 5.3 `smoke_test.ps1` — validación end-to-end post-build (NFR-001, NFR-003)

1. Instalación silenciosa per-user: `tempify-0.1.0-win64-setup.exe /VERYSILENT /SUPPRESSMSGBOXES /CURRENTUSER /DIR="$env:LOCALAPPDATA\Programs\tempify"`.
2. Verifica existencia de `tempify-gui.exe` y shortcut en menú inicio.
3. Mide cold start: `Measure-Command { & "$installDir\tempify-cli.exe" --version }`. Aborta si > 5 s (NFR-001).
4. Ejecuta procesamiento mínimo: `& "$installDir\tempify-gui.exe" --headless --process tests/fixtures/worldclim_chile_mini/ --out $env:TEMP\smoke_out --method linear`.
5. Verifica existencia de output y no-vacío.
6. Desinstalación silenciosa: invoca `unins000.exe /VERYSILENT`.
7. Verifica que el output del paso 4 (fuera del install dir) **sigue presente** (REQ-008).
8. Verifica que `%APPDATA%\tempify\config.yaml`, si existía, sigue presente (REQ-009).

### 5.4 Hooks PyInstaller

Algoritmo común: cada hook usa `PyInstaller.utils.hooks.collect_data_files`, `collect_dynamic_libs`, `collect_submodules` para los paquetes mencionados, y declara `excludedimports` para podar subpaquetes pesados que tempify no usa (ej. `PySide6.QtWebEngineWidgets`, `PySide6.QtMultimedia`, `PySide6.QtQuick`, `PySide6.QtCharts`, `PySide6.Qt3DCore`). Cada hook está versionado y revisado manualmente si la versión de la dependencia upstream cambia.

### 5.5 Workflow CI (`build-windows.yml`)

Disparadores: `on: push: tags: ['v*']` y `on: workflow_dispatch` para pruebas manuales. Jobs:

1. **build.** `runs-on: windows-2022` (pineado, REQ-002). Steps:
   - `actions/checkout@v4` con `fetch-depth: 0`.
   - `actions/setup-python@v5` con `python-version: '3.11'`.
   - Instala Inno Setup: `choco install innosetup --version=6.2.2 -y`.
   - Ejecuta `packaging/scripts/build_windows.ps1`.
   - Sube artifact `tempify-0.1.0-win64-setup.exe` + `SHA256SUMS.txt`.

2. **reproducibility.** Depende de `build`. Ejecuta `verify_sha256.ps1` y publica resultado como check.

3. **smoke.** Depende de `build`. Descarga el artifact y ejecuta `smoke_test.ps1`.

4. **pip-coexistence** (REQ-010). Crea venv limpio, ejecuta `pip install .`, instala el `.exe` también, ejecuta `tempify --version` (pip) y `tempify-gui.exe --version` (bundle) y verifica que ambos responden sin conflicto de PATH.

5. **release.** Solo si tag `v*` y todos los jobs anteriores verdes. Usa `softprops/action-gh-release@v2` para crear release con assets: `.exe` + `SHA256SUMS.txt`.

## 6. Decisiones de diseño

### Decisión 1: PyInstaller `--onedir` vs `--onefile`

**Decisión:** `--onedir`.
**Razón:** registrada en ADR-0006. `--onefile` extrae a `%TEMP%` en cada arranque (cold start > 10 s en máquinas modestas, viola NFR-001) y dispara más falsos positivos antivirus. `--onedir` permite además que Inno Setup empaquete cada archivo individualmente y mantenga su signature en `[Files]` para verificación.
**Trade-offs:** carpeta visible al usuario con ~250 MB de archivos; mitigado porque Inno Setup oculta el detalle tras un solo `.exe` instalador.

### Decisión 2: Modo per-machine como default, per-user opcional

**Decisión:** Inno Setup arranca pidiendo admin (per-machine) pero ofrece downgrade a per-user vía `PrivilegesRequiredOverridesAllowed=dialog`.
**Razón:** REQ-005 + REQ-007: la auto-instalación de VC++ runtime requiere admin, y la mayoría de los usuarios espera ese flujo en Windows. El modo per-user es escape hatch para entornos sin admin (laboratorios universitarios, máquinas corporativas).
**Trade-offs:** complejidad ligeramente mayor en `installer.iss` (rama condicional para VC++); aceptable.

### Decisión 3: Sin code-signing en v0.1.0

**Decisión:** publicar el instalador sin firma; compensar con `SHA256SUMS.txt` y documentación.
**Razón:** el equipo no dispone de certificado EV; obtenerlo retrasaría la release. ADR-0013 difiere code-signing a v0.2.0.
**Trade-offs:** SmartScreen mostrará warning ("Más información" → "Ejecutar de todas formas") los primeros días/semanas hasta acumular reputación. Documentado en README.

### Decisión 4: Runner CI pineado `windows-2022`

**Decisión:** explícitamente `windows-2022`, no `windows-latest`.
**Razón:** REQ-002 + REQ-013: la reproducibilidad bit-exact entre builds requiere imagen base estable. `windows-latest` migra a `windows-2025` sin aviso y rompería el hash determinístico.
**Trade-offs:** mantenimiento manual cuando GitHub deprecia `windows-2022` (preaviso de ~6 meses); aceptable.

### Decisión 5: Inno Setup instalado vía chocolatey en CI

**Decisión:** `choco install innosetup --version=6.2.2 -y` en el workflow.
**Razón:** versión pineada (REQ-011), reproducible y mantenida; alternativa `winget` no está garantizada en runner Windows Server. Chocolatey está preinstalado en `windows-2022`.
**Trade-offs:** dependencia operativa de chocolatey.org; mitigada porque el paquete está cacheado en GitHub Actions infrastructure.

### Decisión 6: Asociaciones `.nc`/`.tif` siempre opt-in

**Decisión:** sección `[Tasks]` con checkboxes **desmarcados** por default.
**Razón:** REQ-006 + análisis de riesgo: muchos usuarios tienen QGIS u otro GIS asociado a esos formatos; sobrescribir sin consentimiento explícito sería destructivo.
**Trade-offs:** descubribilidad menor; mitigada porque el wizard español describe la opción claramente.

### Decisión 7: `packaging/` como carpeta de scripts, no paquete Python

**Decisión:** `packaging/` queda fuera de `src/`, sin `__init__.py`, no es importable.
**Razón:** son artefactos de build, no código de aplicación. Mezclarlo con `src/tempify/` contaminaría el namespace público y añadiría dependencia transitiva de PyInstaller en runtime.
**Trade-offs:** los scripts PowerShell no se pueden testear con pytest; mitigado porque la validación es end-to-end vía CI.

## 7. Estrategia de testing

### Tests automatizados en CI

- `test_installer_runs_without_python` — VM-like environment (runner sin Python sistema): instala `.exe`, ejecuta GUI headless. Cubre REQ-001.
- `test_bundle_contains_gdal_proj_qt` — script PowerShell que verifica existencia de `_internal/rasterio/gdal_data/`, `_internal/pyproj/proj_data/`, `_internal/PySide6/translations/`. Cubre REQ-003.
- `test_installer_locale_es` — invoca el instalador con `/LANG=spanish` y captura textos del wizard via UI automation (PyAutoGui o equivalente); valida presencia de cadenas castellanas conocidas. Cubre REQ-004.
- `test_start_menu_shortcut_created` — tras instalación, valida existencia de `.lnk` en `%ProgramData%\Microsoft\Windows\Start Menu\Programs\tempify\tempify.lnk` (per-machine) o equivalente per-user. Cubre REQ-005.
- `test_per_user_vs_per_machine_modes` — corre instalación en ambos modos y verifica directorios destino. Cubre REQ-005.
- `test_file_association_optional` — instala dos veces: una sin marcar tasks (verifica que `.nc` NO está asociado), otra marcando tasks (verifica HKCR registry). Cubre REQ-006.
- `test_vcruntime_installed` — desinstala VC++ runtime del runner antes del test, corre instalador, verifica que VC++ queda instalado. Cubre REQ-007.
- `test_uninstall_preserves_user_outputs` — crea archivo en `%USERPROFILE%\Documents\tempify_output\` antes de desinstalar, verifica que sobrevive. Cubre REQ-008.
- `test_upgrade_preserves_config` — instala v0.1.0, modifica `%APPDATA%\tempify\config.yaml`, instala v0.1.0 nuevamente (simulando upgrade), verifica que el archivo no cambió. Cubre REQ-009.
- `test_pip_install_still_works` — venv limpio, `pip install .`, ejecuta `tempify --version`. Cubre REQ-010 parte A.
- `test_pip_exe_coexistence` — máquina con `.exe` instalado, además crea venv, ejecuta `pip install tempify`, valida que ambos shortcuts y comandos PATH resuelven sin colisión (`Get-Command tempify` debe apuntar al venv cuando activado; al `.exe` cuando no). Cubre REQ-010 parte B.
- `test_build_fails_without_gui_extras` — venv sin extras, ejecuta `build_windows.ps1`, verifica exit code != 0 y mensaje claro. Cubre REQ-012.
- `test_build_reproducibility_sha256` — job que ejecuta `verify_sha256.ps1`. Cubre REQ-013.
- `test_sha256sums_attached_to_release` — verifica que el release de GitHub tiene el asset `SHA256SUMS.txt`. Cubre REQ-014.
- `test_bundle_footprint` — verifica `(Get-Item Output\*.exe).Length -lt 300MB`. Cubre NFR-002.

### Pruebas manuales (release gate)

Antes de marcar un release como `latest`:

- VM Windows 10 22H2 limpia (sin Python, sin VC++): instalar, lanzar GUI, procesar fixture `worldclim_chile_mini`, desinstalar; verificar que `%APPDATA%\tempify\` se preservó.
- VM Windows 11 23H2 limpia: idem.
- Máquina con QGIS instalado: instalar tempify sin opt-in de asociaciones, confirmar que QGIS sigue siendo el handler de `.tif`.

### Fixtures necesarios

- `tests/fixtures/worldclim_chile_mini/` — 12 GeoTIFFs mensuales de temperatura, ~5x5 pixels, ya producido por la spec `io-handlers`.
- `tests/fixtures/installer-test-config.yaml` — config dummy para validar preservación en upgrade (REQ-009).

## 8. Plan de migración

No aplica: es la primera versión empaquetada. Para futuras versiones, el `AppId` GUID estable garantiza upgrades in-place y la cláusula `[Code]` de Inno Setup detecta la versión instalada previa para preservar configuración.

## 9. Métricas de calidad

| Métrica | Umbral | Verificable por |
|---|---|---|
| Tamaño bundle PyInstaller | < 280 MB | `build_windows.ps1` paso 5 |
| Tamaño instalador `.exe` | < 300 MB (NFR-002) | `build_windows.ps1` paso 6 |
| Cold start GUI desde `.exe` | < 5 s (NFR-001) | `smoke_test.ps1` paso 3 |
| SHA256 reproducible build a build | hash idéntico (REQ-013) | `verify_sha256.ps1` |
| Smoke test verde en CI | exit 0 (NFR-003) | job `smoke` |
| Cobertura módulo Python auxiliar (si surge) | >= 85% (NFR-006) | `pytest --cov`; en v0.1.0 no aplica porque `packaging/` no contiene Python |
| Soporte plataforma | Windows 10 build 19041+, Windows 11 22H2+ (NFR-004) | documentado en README, validado en VMs |
| Versionado de scripts | `pyinstaller.spec` e `installer.iss` en git (NFR-005) | inspección del repo |

## 10. Trazabilidad requirements → design

| Requirement | Componente que lo implementa |
|---|---|
| REQ-001 | `pyinstaller.spec` (onedir self-contained) + `installer.iss` ([Files] copia todo el bundle) |
| REQ-002 | `.github/workflows/build-windows.yml` con `runs-on: windows-2022` y trigger `tags: ['v*']` |
| REQ-003 | `hook-rasterio.py`, `hook-pyproj.py`, `hook-PySide6.py`, `hook-netcdf4.py` |
| REQ-004 | `installer.iss` sección `[Languages]` con `spanish.isl` + `LICENSE-es.txt` |
| REQ-005 | `installer.iss` `[Icons]` (shortcut menú inicio) + `[Tasks]` desktop opt-in + `PrivilegesRequiredOverridesAllowed=dialog` |
| REQ-006 | `installer.iss` `[Tasks]` con checkboxes `associate_nc` y `associate_tif` desmarcados, más entradas `[Registry]` condicionales |
| REQ-007 | `installer.iss` `[Run]` con VC++ redistributable bundled, condicional a modo per-machine |
| REQ-008 | `installer.iss` `[UninstallDelete]` limitado al `{app}` dir, sin tocar `%APPDATA%` |
| REQ-009 | `installer.iss` `[Code]` con `CurStepChanged` que detecta upgrade y preserva `%APPDATA%\tempify\config.yaml` |
| REQ-010 | `pyproject.toml` mantiene `[project.scripts] tempify`, hatchling build intacto; CI job `pip-coexistence` |
| REQ-011 | `pyproject.toml` añade `[packaging] = ["pyinstaller>=6.3", "pyside6>=6.6"]`; workflow declara `choco install innosetup --version=6.2.2` |
| REQ-012 | `build_windows.ps1` paso 1 valida extras antes de continuar |
| REQ-013 | `verify_sha256.ps1` + job CI `reproducibility` |
| REQ-014 | `build_windows.ps1` paso 7 genera `SHA256SUMS.txt`; workflow `release` lo sube como asset |
| NFR-001 | `smoke_test.ps1` paso 3 mide cold start; `--onedir` (Decisión 1) minimiza arranque |
| NFR-002 | `build_windows.ps1` paso 5 + `pyinstaller.spec` con `excludes` agresivos en PySide6/scipy |
| NFR-003 | `smoke_test.ps1` completo + job CI `smoke` |
| NFR-004 | Documentación README; validación manual en VMs Windows 10/11 |
| NFR-005 | Todos los artefactos de `packaging/` versionados en git |
| NFR-006 | No aplica en v0.1.0 (sin código Python auxiliar); placeholder para futuro |
