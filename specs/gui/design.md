# Design — gui

**Estado:** Draft
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-16

## 1. Visión técnica

`tempify.gui` es una **capa cliente** del pipeline equivalente al CLI: traduce gestos del usuario (drag&drop, clicks) a un `PipelineConfig`, delega ejecución en `TempifyPipeline.run()` y refleja eventos del callback de progreso en widgets Qt. NO contiene lógica de detección, validación, interpolación ni I/O (REQ-002).

Se distribuye como **extra opcional** `tempify[gui]` (pip) y como parte del bundle PyInstaller (`packaging`, ADR-0006). Implementada en PySide6 ≥ 6.6 (ADR-0005) con threading vía `QThread` subclass (REQ-016), renderizado Markdown vía `QTextBrowser` (REQ-014), e i18n vía Qt Linguist (REQ-009/010).

Una clase puente, `ProgressCallbackBridge`, adapta el `ProgressCallback` Protocol del pipeline (`specs/pipeline/requirements.md` REQ-003, 7 fases canónicas) a `Signal` de Qt usando `Qt.QueuedConnection` para thread-safety. La cancelación es cooperativa vía `threading.Event` consultado por el pipeline (a futuro); mientras el pipeline no consulte el evento, la atomicidad de outputs se garantiza por escritura `.tmp` + `os.replace` final (NFR-003).

## 2. Arquitectura propuesta

### Diagrama de componentes

```
┌────────────────────────────────────────────────────────────────────┐
│ tempify.gui                                                        │
│                                                                    │
│  app.py            ─→ QApplication(locale=es_CL), instala traductor│
│   │                                                                │
│   └─ windows/main_window.py  (MainWindow)                          │
│        │                                                           │
│        ├─ widgets/file_drop_area.py     (dragEnterEvent/dropEvent) │
│        ├─ widgets/method_selector.py    (consulta VariableProfile) │
│        ├─ widgets/detection_preview.py  (muestra DetectionResult)  │
│        ├─ widgets/progress_panel.py     (QProgressBar + Cancelar)  │
│        ├─ widgets/report_viewer.py      (QTextBrowser.setMarkdown) │
│        ├─ widgets/log_panel.py          (QPlainTextEdit append)    │
│        │                                                           │
│        ├─ dialogs/frequency_disambiguation.py                      │
│        ├─ dialogs/error_dialog.py                                  │
│        ├─ dialogs/force_method_confirmation.py                     │
│        │                                                           │
│        └─ workers/pipeline_worker.py  (QThread subclass)           │
│             │                                                      │
│             └─ signals.py  (Signal definitions)                    │
│                  │                                                 │
│                  └─ ProgressCallbackBridge                         │
│                       │   Qt.QueuedConnection                      │
│                       ▼                                            │
│                  tempify.pipeline.TempifyPipeline.run()            │
│                                                                    │
│  i18n/             tempify_es.ts, tempify_es_CL.ts, *.qm           │
│  resources/        resources.qrc → resources_rc.py                 │
└────────────────────────────────────────────────────────────────────┘
```

### Componentes nuevos

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| `main()` | `tempify/gui/app.py` | Entry point; crea `QApplication`, instala `QTranslator` `es_CL`/`es`, verifica display, lanza `MainWindow` |
| `MainWindow` | `tempify/gui/windows/main_window.py` | Ventana principal, layout, tabs `convert`/`inspect`/`validate`, atajos teclado, orquestación de widgets |
| `FileDropArea` | `tempify/gui/widgets/file_drop_area.py` | QWidget con `acceptDrops(True)`, emite `paths_dropped: Signal(list[Path])` |
| `MethodSelector` | `tempify/gui/widgets/method_selector.py` | `QComboBox` filtrado por `VariableProfile.allowed_methods`; toggle "Modo experto" |
| `DetectionPreview` | `tempify/gui/widgets/detection_preview.py` | Muestra `DetectionResult` (estructura A/B/C, frecuencia, perfil, count) |
| `ProgressPanel` | `tempify/gui/widgets/progress_panel.py` | `QProgressBar` por fase + label + botón Cancelar |
| `ReportViewer` | `tempify/gui/widgets/report_viewer.py` | Subclass `QTextBrowser` con `setMarkdown(text)` + acción "Guardar reporte como…" |
| `LogPanel` | `tempify/gui/widgets/log_panel.py` | `QPlainTextEdit` read-only, append por slot conectado al worker |
| `FrequencyDisambiguationDialog` | `tempify/gui/dialogs/frequency_disambiguation.py` | `QDialog` modal, satisface `frequency_resolver_callback` (REQ-012 pipeline) |
| `ErrorDialog` | `tempify/gui/dialogs/error_dialog.py` | `QDialog` modal con código de error referenciable + mensaje en español |
| `ForceMethodConfirmationDialog` | `tempify/gui/dialogs/force_method_confirmation.py` | Confirmación tipeada `"si entiendo"` para override de precipitación (ADR-0004) |
| `PipelineWorker` | `tempify/gui/workers/pipeline_worker.py` | `QThread` subclass que ejecuta `TempifyPipeline.run()` |
| `ProgressCallbackBridge` | `tempify/gui/workers/pipeline_worker.py` | Adapta `ProgressCallback` Protocol → `Signal` con `Qt.QueuedConnection` |
| `Signals` | `tempify/gui/signals.py` | Definiciones tipadas centralizadas (re-exportadas para tests) |
| `NoDisplayError` | `tempify/gui/app.py` | Excepción tipada con mensaje en español, exit 4 (REQ-012) |
| `MarkdownReportRenderer` | `tempify/gui/widgets/report_viewer.py` | Alias semántico de `ReportViewer` para el contrato público |

### Componentes modificados

| Componente | Ubicación | Cambio |
|---|---|---|
| `pyproject.toml` | repo root | Añadir extra opcional `gui` con `PySide6>=6.6,<7`, `pytest-qt>=4.3` (en `dev`) |
| `tempify.__init__` | `tempify/__init__.py` | Sin cambio: `tempify.gui` se importa lazy desde el entry point |

## 3. Contratos públicos (APIs)

### `tempify.gui.app.main`

```python
def main(argv: list[str] | None = None) -> int:
    """Entry point de la GUI. Verifica display, configura locale es_CL/es,
    crea QApplication, lanza MainWindow.

    Returns
    -------
    int
        Código de salida: 0 normal, 4 si NoDisplayError, otro código si falla.
    """
```

**Pre-condiciones:** `PySide6` instalado.
**Post-condiciones:** ventana cerrada o exit no cero.
**Excepciones:** `NoDisplayError` (envuelta y traducida a exit 4).

### `MainWindow`

```python
class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None: ...

    # API pública para tests y entry points externos
    def set_source(self, paths: list[Path]) -> None:
        """Establece la fuente y dispara dry_run en worker para
        poblar DetectionPreview. Slot conectado al signal paths_dropped."""

    def start_processing(self) -> None:
        """Construye PipelineConfig desde el estado visual y lanza
        PipelineWorker. Activa ProgressPanel y desactiva controles."""

    def cancel(self) -> None:
        """Setea el cancel_event del worker y muestra diálogo de
        confirmación. En confirmación, elimina archivos *.tmp del
        directorio de salida."""
```

### `PipelineWorker`

```python
class PipelineWorker(QThread):
    # Signals tipados (declarados como atributos de clase)
    phase_started   : ClassVar[Signal] = Signal(str)              # phase name
    progress_updated: ClassVar[Signal] = Signal(float, str)       # fraction, message
    log_emitted     : ClassVar[Signal] = Signal(str)              # log line
    pipeline_finished: ClassVar[Signal] = Signal(object)          # PipelineResult
    pipeline_failed : ClassVar[Signal] = Signal(Exception)        # any pipeline error

    def __init__(
        self,
        config: PipelineConfig,
        source: Path | list[Path],
        cancel_event: threading.Event,
        parent: QObject | None = None,
    ) -> None: ...

    def run(self) -> None:
        """Ejecuta TempifyPipeline.run(). El callback de progreso del
        config debe ser un ProgressCallbackBridge construido por el caller
        que reemite hacia los signals de esta instancia."""
```

**Pre-condiciones:** `config.progress_callback` debe ser un `ProgressCallbackBridge`.
**Post-condiciones:** emite exactamente uno de `pipeline_finished` o `pipeline_failed`.
**Excepciones:** no propaga; las envuelve en `pipeline_failed`.

### `ProgressCallbackBridge`

```python
class ProgressCallbackBridge(QObject):
    """Adapta ProgressCallback Protocol → Qt Signals con QueuedConnection."""

    phase_started   : ClassVar[Signal] = Signal(str)
    progress_updated: ClassVar[Signal] = Signal(float, str)

    def __call__(
        self,
        phase: Literal[
            "detect", "validate_geospatial", "validate_compatibility",
            "interpolate", "validate_post", "write", "generate_report",
        ],
        progress: float,
        message: str | None = None,
    ) -> None:
        """Invoke desde cualquier thread; emite signal con QueuedConnection
        para que el slot corra en el thread de UI."""
```

### `MarkdownReportRenderer` (alias de `ReportViewer`)

```python
class MarkdownReportRenderer(QTextBrowser):
    """Visor del reporte Markdown final. NO usa QWebEngineView (REQ-014)."""
    def render(self, markdown_text: str) -> None: ...
    def save_as(self, target: Path) -> None: ...
```

### Excepción `NoDisplayError`

```python
class NoDisplayError(TempifyError):
    """REQ-012. Mensaje en español. exit code 4."""
    code: ClassVar[str] = "GUI-001"
```

## 4. Modelos de datos

### `GuiSessionState` (inmutable, en memoria)

```python
@dataclass(frozen=True)
class GuiSessionState:
    source: tuple[Path, ...]
    detection: DetectionResult | None
    method: Literal["linear", "pchip", "pchip_mp", "fourier"]
    output_dir: Path | None
    output_format: Literal["netcdf", "geotiff_collection", "geotiff_multiband", "zarr"]
    expert_mode: bool
    force_method: bool
```

### Persistencia de configuración

Archivo `%APPDATA%/tempify/gui_session.yaml` (Windows) o `QStandardPaths.AppConfigLocation` equivalente. Estructura mínima: `last_output_dir`, `last_method`, `expert_mode`, `locale`. Cargado al iniciar `MainWindow`, persistido al cerrar.

## 5. Algoritmos clave

### Threading pattern (REQ-016, NFR-002)

`QThread` subclass. El worker:
1. Construye su propio `ProgressCallbackBridge` con `moveToThread(QApplication.instance().thread())` para que los signals se entreguen al UI thread.
2. Conecta los signals del bridge a los slots de `MainWindow` con `Qt.QueuedConnection` explícita.
3. Llama `TempifyPipeline(config).run(source)` dentro de `run()`.
4. Emite `pipeline_finished` o `pipeline_failed` y termina.

`QRunnable` + `QThreadPool` se difiere a v0.2 (REQ-016).

### Drag&drop (REQ-003)

`FileDropArea` override:

```python
def dragEnterEvent(self, e: QDragEnterEvent) -> None:
    if e.mimeData().hasUrls():
        e.acceptProposedAction()

def dropEvent(self, e: QDropEvent) -> None:
    paths = [Path(u.toLocalFile()) for u in e.mimeData().urls()]
    self.paths_dropped.emit(paths)
```

### Detección previa (REQ-003)

Al recibir `paths_dropped`, `MainWindow` construye `PipelineConfig(dry_run=True, ...)` y lanza un `PipelineWorker` desechable. El `PipelineResult` resultante (con `outputs=[]` y `detection`) pobla `DetectionPreview`. El método queda activado solo si la detección es exitosa.

### Cancelación atómica (REQ-008, NFR-003)

1. `MainWindow.cancel()` setea `self.cancel_event.set()`.
2. El pipeline (a futuro) consulta `cancel_event` entre fases y aborta cooperativamente.
3. Independiente del soporte del pipeline, **todos los writers** escriben a `<target>.tmp` y hacen `os.replace(target.tmp, target)` solo al final. La GUI, en cancelación confirmada, recorre `output_dir.glob("*.tmp")` y elimina.
4. `cancel_event` se pasa al `PipelineWorker` y se reusa entre dry_run y run principal (se resetea con `.clear()`).

### Bloqueo de métodos suaves para precipitación (REQ-015)

`MethodSelector.update_for_profile(profile: VariableProfile)`:

```
allowed = set(profile.allowed_methods)
for method in {"linear", "pchip", "pchip_mp", "fourier"}:
    item = self.combo.item(method)
    if method not in allowed:
        item.setEnabled(False)
        item.setToolTip(tr("Bloqueado: ver ADR-0004 (política de precipitación)"))
```

Si el usuario activa "Modo experto" (REQ-013), aparece un checkbox "Forzar método". Marcado, los métodos vetados se re-habilitan visualmente, pero al pulsar "Procesar" se dispara `ForceMethodConfirmationDialog`: campo de texto, solo `si entiendo` autoriza; el resultado se inyecta en `PipelineConfig.force_method=True` para que el pipeline estampe la metadata (ADR-0004).

### Markdown rendering (REQ-014)

```python
self.text_browser = QTextBrowser(self)
self.text_browser.setOpenExternalLinks(True)
self.text_browser.setMarkdown(markdown_text)  # nativo Qt 6
```

Sin `QWebEngineView`. Sin dependencias adicionales.

### Resolución de frecuencia interactiva (REQ-006, REQ-012 pipeline, ADR-0010)

`MainWindow` registra como `PipelineConfig.frequency_resolver_callback` un closure que:
1. Emite un signal `frequency_resolution_needed: Signal(list[str])` al UI thread.
2. Espera (en el worker thread, vía `threading.Event`) la respuesta poblada por el slot que abre `FrequencyDisambiguationDialog`.
3. Devuelve la frecuencia elegida al pipeline.

Este patrón usa `QMetaObject.invokeMethod(..., Qt.BlockingQueuedConnection)` para no bloquear el UI thread y mantener responsividad.

### i18n (REQ-009, REQ-010)

- Todos los strings UI envueltos en `self.tr("...")`.
- `tempify_es.ts` (base) y `tempify_es_CL.ts` (variante regional) en `tempify/gui/i18n/`.
- Compilación en build: `pyside6-lrelease tempify_es.ts -qm tempify_es.qm`.
- En `app.py`:

```
translator = QTranslator()
locale = QLocale.system().name()  # ej "es_CL"
if not translator.load(f"tempify_{locale}", ":/i18n/"):
    translator.load("tempify_es", ":/i18n/")
app.installTranslator(translator)
```

Hook pre-commit `check_i18n_strings.py` ejecuta `pyside6-lupdate --no-obsolete` y falla si quedan strings sin traducir (NFR-008).

## 6. Decisiones de diseño

### Decisión 1: `QTextBrowser` vs `QWebEngineView`

**Opciones:**
1. `QTextBrowser` (Qt nativo, ~0 MB extra)
2. `QWebEngineView` (Chromium embebido, ~80 MB extra)

**Decisión:** `QTextBrowser` (REQ-014, ADR-0005).
**Razón:** evita inflar el bundle PyInstaller (`packaging` NFR-002 ≤300 MB) y elimina problemas de sandbox Chromium en Windows packaged. El reporte Markdown del pipeline (schema en `docs/schemas/processing-report.schema.md`) usa solo tablas, listas y código inline, soportado por Qt 6.
**Trade-offs:** sin Mermaid ni syntax highlighting avanzado; fallback `QWebEngineView` queda fuera de scope v0.1 (re-evaluable si los usuarios reportan limitaciones reales).

### Decisión 2: `QThread` subclass vs `QRunnable` + `QThreadPool`

**Opciones:**
1. `QThread` subclass (REQ-016 actual)
2. `QRunnable` + `QThreadPool` (sugerencia inicial de ADR-0005)

**Decisión:** `QThread` subclass.
**Razón:** v0.1 corre una sola conversión a la vez; no se necesita pool. Subclass facilita exponer signals tipados y método `cancel()`. `QRunnable` agrega indirection sin beneficio mientras no haya paralelismo entre conversiones.
**Trade-offs:** migración futura a `QThreadPool` requerirá refactor (aceptable, diferido a v0.2 si aparece batch processing).

### Decisión 3: Locale default `es_CL` con fallback `es`

**Opciones:**
1. Solo `es` neutro
2. `es_CL` con fallback `es`

**Decisión:** opción 2.
**Razón:** la audiencia primaria es chilena (Guillermo Fuentes-Jaque y comunidad local); `es_CL` permite formatos numéricos y de fecha locales sin perder portabilidad a otras variantes hispanohablantes.
**Trade-offs:** dos archivos `.ts` que mantener (mitigado: `es_CL` solo sobre-traduce strings divergentes).

### Decisión 4: Cancelación atómica vía `.tmp` + `os.replace`

**Opciones:**
1. Confiar exclusivamente en cancelación cooperativa del pipeline
2. Escritura a archivo temporal + rename atómico al final
3. Combinar ambas

**Decisión:** opción 3 (combinar).
**Razón:** mientras la cancelación cooperativa del pipeline esté pendiente, el rename atómico garantiza atomicidad observable por el usuario (NFR-003) sin acoplar la GUI a internals del pipeline.
**Trade-offs:** duplica espacio en disco brevemente; aceptable.

### Decisión 5: Configuración de usuario en `QStandardPaths.AppConfigLocation`

**Opciones:**
1. `QSettings` (registry en Windows)
2. YAML en `%APPDATA%\tempify\gui_session.yaml`

**Decisión:** opción 2.
**Razón:** coherente con el resto de tempify (perfiles YAML), portable a Linux/macOS, inspeccionable por el usuario.
**Trade-offs:** lectura/escritura manual vs API automática de `QSettings`.

### Decisión 6: Sin internet, sin telemetría

**Decisión:** ningún módulo de `tempify.gui` puede importar `urllib`, `requests`, `httpx`, ni abrir sockets. Test de imports prohibidos en CI.

## 7. Estrategia de testing

Framework: `pytest-qt` con fixture `qtbot`. Cobertura mínima módulo `tempify.gui` ≥ 70% (NFR-005, excepción documentada en ADR-0005). Tests headless en CI via `pytest-qt` modo offscreen (`QT_QPA_PLATFORM=offscreen`).

### Tests unitarios por widget

- `test_file_drop_area_emits_paths_dropped` — simula `QDropEvent` con URLs locales.
- `test_method_selector_disables_smooth_for_precipitation` — perfil `precipitation` deshabilita 4 métodos suaves (REQ-015).
- `test_method_selector_expert_mode_reveals_force_checkbox` — REQ-013.
- `test_detection_preview_renders_detection_result` — DTO → labels.
- `test_progress_panel_updates_on_signal` — emite signals, verifica QProgressBar.
- `test_report_viewer_uses_qtextbrowser` — `isinstance(viewer, QTextBrowser)` y verifica que `QWebEngineView` NO se importa en `tempify.gui` (AST check).
- `test_report_viewer_save_as` — guarda Markdown a tmp_path.
- `test_log_panel_appends_lines` — slot append.
- `test_frequency_disambiguation_dialog_returns_choice` — selección modal.
- `test_error_dialog_format` — código + mensaje español (NFR-007).
- `test_force_method_confirmation_only_accepts_si_entiendo` — ADR-0004.

### Tests del worker y bridge

- `test_pipeline_worker_emits_finished_on_success` — mock de `TempifyPipeline`.
- `test_pipeline_worker_emits_failed_on_exception` — mock que lanza.
- `test_progress_callback_bridge_uses_queued_connection` — verifica `Qt.ConnectionType.QueuedConnection`.
- `test_pipeline_runs_in_qthread_worker` — `isinstance(worker, QThread)` y verifica que el thread del worker ≠ UI thread (REQ-016).
- `test_cancel_event_clears_tmp_files` — crea `.tmp`, cancela, verifica eliminación.
- `test_gui_cancel_no_partial_output` — smoke (NFR-003).

### Tests de imports y arquitectura

- `test_gui_invokes_pipeline_only` — AST checking sobre todos los módulos de `tempify.gui`: no se importa nada de `tempify.detection`, `tempify.validation`, `tempify.interpolation`, `tempify.io` (REQ-002).
- `test_gui_no_qwebengineview_import` — AST check (REQ-014).
- `test_gui_no_network_imports` — AST check (Decisión 6).

### Tests i18n

- `test_gui_all_strings_spanish` — recorre widgets visibles y verifica que no hay strings inglesas conocidas (NFR-001).
- `test_gui_ts_files_present_and_compilable` — REQ-010.

### Tests teclado y navegación

- `test_gui_keyboard_shortcuts` — Ctrl+O, Ctrl+S, F1, Esc (REQ-011).
- `test_gui_keyboard_navigation` — orden de Tab (NFR-006).

### Test no-display

- `test_gui_raises_no_display_error` — monkeypatch `QGuiApplication.platformName()` o lanza con `QT_QPA_PLATFORM=` vacío; verifica `NoDisplayError`, exit 4 (REQ-012).

### Test responsividad

- `test_gui_ui_responsive_during_processing` — lanza worker dummy que duerme; mide latencia de `QTest.qWait` + click → respuesta < 100 ms (NFR-002).

### Smoke test integral

- `test_gui_full_workflow_with_fixture` — drag de fixture WorldClim sintética (12 GeoTIFFs en `tests/fixtures/worldclim_synthetic/`), método PCHIP+RM, output a `tmp_path`, formato NetCDF; verifica que aparece `ReportViewer` con contenido Markdown y que existe el NetCDF resultante.

### Fixtures necesarios

- `worldclim_synthetic` (12 GeoTIFFs mensuales 3×3 px) — generar en `conftest.py` si no existe.
- `mock_pipeline` — fake `TempifyPipeline` que respeta el contrato pero no procesa.
- `qapp` — fixture `pytest-qt` estándar.

## 8. Plan de migración

Feature nueva: no hay usuarios actuales. La spec se entrega cuando los criterios de aceptación de `requirements.md §6` se cumplan. Coordinación con `packaging` para que `pyinstaller.spec` empaquete `tempify/gui/i18n/*.qm` y `tempify/gui/resources/*` correctamente.

## 9. Métricas de calidad

| Métrica | Umbral |
|---|---|
| Cobertura `tempify.gui` | ≥ 70% (excepción documentada NFR-005, ADR-0005) |
| Tiempo arranque GUI (cold) | < 5 s (alineado a `packaging` NFR-001) |
| Latencia respuesta UI durante job | < 100 ms (NFR-002) |
| Tamaño contribuido al bundle | < 90 MB (subset de `packaging` NFR-002 ≤ 300 MB) |
| Strings sin traducir | 0 (hook pre-commit `check_i18n_strings.py`, NFR-008) |

## 10. Trazabilidad requirements → design

| Requirement | Componente que lo implementa |
|---|---|
| REQ-001 | `MainWindow` (tabs convert/inspect/validate) |
| REQ-002 | `PipelineWorker` (única invocación de `TempifyPipeline.run`); test AST `test_gui_invokes_pipeline_only` |
| REQ-003 | `FileDropArea` + `MainWindow.set_source` + `PipelineWorker` (modo dry_run) + `DetectionPreview` |
| REQ-004 | `ProgressPanel` + `ProgressCallbackBridge` + `LogPanel` + botón Cancelar |
| REQ-005 | `ErrorDialog` + `PipelineWorker.pipeline_failed` |
| REQ-006 | `FrequencyDisambiguationDialog` + `frequency_resolver_callback` closure |
| REQ-007 | `ReportViewer` + `MainWindow` slot `on_pipeline_finished` |
| REQ-008 | `MainWindow.cancel()` + `cancel_event` + cleanup de `.tmp` |
| REQ-009 | Todos los strings con `tr()`; QTranslator en `app.py` |
| REQ-010 | `i18n/tempify_es.ts`, `tempify_es_CL.ts`; build genera `.qm` |
| REQ-011 | `MainWindow` `QShortcut(Ctrl+O/Ctrl+S/F1/Esc)` |
| REQ-012 | `app.main()` chequea `QGuiApplication.platformName()`; lanza `NoDisplayError`, exit 4 |
| REQ-013 | Toggle "Modo experto" en `MainWindow`; revela widgets adicionales en `MethodSelector` |
| REQ-014 | `ReportViewer/MarkdownReportRenderer` basado en `QTextBrowser`; test AST sin `QWebEngineView` |
| REQ-015 | `MethodSelector.update_for_profile` + `ForceMethodConfirmationDialog` |
| REQ-016 | `PipelineWorker(QThread)` + `ProgressCallbackBridge` con `Qt.QueuedConnection` |
| NFR-001 | Hook `tr()`; test `test_gui_all_strings_spanish` |
| NFR-002 | `QThread` worker; test `test_gui_ui_responsive_during_processing` |
| NFR-003 | Escritura `.tmp` + `os.replace`; test `test_gui_cancel_no_partial_output` |
| NFR-004 | CI Windows obligatorio; Linux/macOS informativos |
| NFR-005 | Configuración `pytest-qt` + `--cov=tempify.gui --cov-fail-under=70` |
| NFR-006 | `setTabOrder` explícito en `MainWindow`; test `test_gui_keyboard_navigation` |
| NFR-007 | `ErrorDialog` con código + mensaje en español |
| NFR-008 | Hook pre-commit `check_i18n_strings.py` con `pyside6-lupdate --no-obsolete` |

## 11. Referencias

- ADR-0004 — Política de precipitación (override `--force-method`)
- ADR-0005 — PySide6 como framework GUI
- ADR-0006 — PyInstaller + Inno Setup (consumidor del bundle GUI)
- ADR-0010 — Contrato de `frequency_resolver_callback`
- ADR-0014 — Naming `TempifyPipeline`
- `specs/pipeline/requirements.md` — contrato `TempifyPipeline.run`, `ProgressCallback`, 7 fases canónicas
- `specs/packaging/requirements.md` — target del bundle
- PySide6 docs: https://doc.qt.io/qtforpython-6/
- Qt Threading Basics: https://doc.qt.io/qt-6/thread-basics.html
- pytest-qt: https://pytest-qt.readthedocs.io/
