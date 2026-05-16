# Tasks — gui

**Estado:** Approved
**Design doc:** [design.md](design.md)
**Requirements doc:** [requirements.md](requirements.md)
**Última actualización:** 2026-05-16

## Reglas para tasks

Cada task debe ser:

- **Atómica:** completable en una sesión, un commit, ≤ 4h.
- **Verificable:** criterio de done observable (test verde, archivo creado, comando exitoso).
- **TDD:** salvo scaffolding/chore, cada `impl` está precedido por un `test` que falla.
- **Headless-safe:** todos los tests Qt usan `qtbot` y `QT_QPA_PLATFORM=offscreen` en CI.

Convenciones:

- Tests Qt bajo `tests/unit/gui/` y `tests/integration/gui/`.
- Código bajo `src/tempify/gui/` siguiendo el árbol declarado en `design.md §2`.
- Cobertura mínima del módulo: 70% (NFR-005, excepción ADR-0005).

## Fase 1: Fundamentos

### task-1.1: Scaffolding del paquete `tempify.gui`

**Tipo:** chore
**Estimación:** 1h
**Bloquea:** task-1.2, task-1.3, task-1.4
**Bloqueada por:** —

**Descripción:** Crear el árbol vacío del paquete con módulos placeholder (solo docstrings) según `design.md §2`.

**Criterio de done:**
- [ ] Existen los siguientes módulos como paquetes vacíos (`__init__.py`):
      `src/tempify/gui/__init__.py`,
      `src/tempify/gui/app.py`,
      `src/tempify/gui/signals.py`,
      `src/tempify/gui/workers/__init__.py`,
      `src/tempify/gui/widgets/__init__.py`,
      `src/tempify/gui/dialogs/__init__.py`,
      `src/tempify/gui/windows/__init__.py`,
      `src/tempify/gui/i18n/__init__.py`,
      `src/tempify/gui/resources/__init__.py`.
- [ ] `python -c "import tempify.gui"` sin error.
- [ ] `ruff check src/tempify/gui` pasa.

**Archivos:**
- `src/tempify/gui/**/__init__.py`
- `src/tempify/gui/app.py`
- `src/tempify/gui/signals.py`

### task-1.2: Extra opcional `tempify[gui]` y dev `pytest-qt`

**Tipo:** chore
**Estimación:** 1h
**Bloquea:** task-1.3, task-1.7
**Bloqueada por:** task-1.1

**Descripción:** Añadir en `pyproject.toml` el extra `gui = ["PySide6>=6.6,<7"]` y la dev-dep `pytest-qt>=4.3`. Documentar en README la instalación opcional.

**Criterio de done:**
- [ ] `pip install -e .[gui]` instala PySide6.
- [ ] `pip install -e .[dev]` instala `pytest-qt`.
- [ ] `python -c "import PySide6; import pytestqt"` exit 0 en venv dev.
- [ ] Tabla de extras actualizada en README.

**Archivos:**
- `pyproject.toml`
- `README.md`

### task-1.3: Entry point `tempify-gui`

**Tipo:** chore
**Estimación:** 0.5h
**Bloquea:** task-1.4
**Bloqueada por:** task-1.2

**Descripción:** Añadir un `console_scripts` adicional `tempify-gui = tempify.gui.app:main` en `pyproject.toml`. En Windows produce `tempify-gui.exe`.

**Criterio de done:**
- [ ] `pip install -e .[gui]` instala el ejecutable `tempify-gui` en el venv.
- [ ] El ejecutable invoca `tempify.gui.app:main` (verificable con `--version`/`-h` placeholder).

**Archivos:**
- `pyproject.toml`

### task-1.4: Test `qtbot` setup + `QT_QPA_PLATFORM=offscreen` en CI

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-1.5
**Bloqueada por:** task-1.3

**Descripción:** Configurar fixture `qapp` y `qtbot` globales y `conftest.py` que fuerza `QT_QPA_PLATFORM=offscreen` cuando no hay display. Escribir un smoke `test_qtbot_can_create_qmainwindow` que sirve de canario del setup.

**Criterio de done:**
- [ ] `tests/unit/gui/conftest.py` exporta fixtures `qapp` y `qtbot` (re-export de `pytest-qt`).
- [ ] `pytest tests/unit/gui/test_smoke_qtbot.py` pasa en CI Windows y en local sin display.
- [ ] CI workflow Windows fija `QT_QPA_PLATFORM=offscreen` para el job de tests GUI.

**Archivos:**
- `tests/unit/gui/__init__.py`
- `tests/unit/gui/conftest.py`
- `tests/unit/gui/test_smoke_qtbot.py`
- `.github/workflows/ci.yml` (o equivalente)

### task-1.5: `app.py` con `QApplication`, locale `es_CL`/`es`, UTF-8

**Tipo:** test+impl
**Estimación:** 2.5h
**Bloquea:** task-1.6, task-1.8
**Bloqueada por:** task-1.4

**Descripción:** Implementar `tempify.gui.app.main()` (REQ-012, REQ-009/010). Test primero:
`test_app_main_installs_es_locale_translator`,
`test_app_main_returns_0_on_clean_exit`,
`test_app_main_uses_utf8` (envoltura `sys.stdout.reconfigure(encoding="utf-8")` o equivalente en Windows).

**Criterio de done:**
- [ ] Tests rojos antes de implementar.
- [ ] `main(argv: list[str] | None = None) -> int` implementado con docstring NumPy y type hints.
- [ ] Instala `QTranslator` para `tempify_es_CL` con fallback `tempify_es`.
- [ ] `mypy --strict` pasa sobre `tempify.gui.app`.

**Archivos:**
- `src/tempify/gui/app.py`
- `tests/unit/gui/test_app.py`

### task-1.6: `NoDisplayError` y exit code 4 (REQ-012)

**Tipo:** test+impl
**Estimación:** 1.5h
**Bloquea:** task-1.8
**Bloqueada por:** task-1.5

**Descripción:** Definir `NoDisplayError(TempifyError)` con `code = "GUI-001"` y mensaje en español. En `main()`, si `QGuiApplication.platformName() in {"", "minimal"}` y no hay `DISPLAY`/Wayland/Windows session, levantar la excepción, capturarla, imprimir el mensaje y retornar 4. Test: `test_main_returns_4_when_no_display` (monkeypatch del platformName).

**Criterio de done:**
- [ ] Test rojo antes de implementar.
- [ ] `NoDisplayError` extiende `TempifyError`; mensaje en español; código `GUI-001`.
- [ ] `main()` retorna exactamente `4` ante ausencia de display.
- [ ] Mensaje sugiere usar la CLI.

**Archivos:**
- `src/tempify/gui/app.py`
- `tests/unit/gui/test_app_no_display.py`

### task-1.7: `GuiSessionState` frozen dataclass + `gui_session.yaml`

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.10
**Bloqueada por:** task-1.2

**Descripción:** Implementar `GuiSessionState` (dataclass `frozen=True`) según `design.md §4` y un módulo `session_store.py` que carga/persiste a `QStandardPaths.AppConfigLocation/tempify/gui_session.yaml`. Tests: roundtrip YAML, valores por defecto, locale persistido.

**Criterio de done:**
- [ ] Tests rojos antes de implementar.
- [ ] Schema YAML mínimo: `last_output_dir`, `last_method`, `expert_mode`, `locale`.
- [ ] Roundtrip exacto (`load(save(x)) == x`).
- [ ] mypy --strict pasa.

**Archivos:**
- `src/tempify/gui/session_state.py`
- `src/tempify/gui/session_store.py`
- `tests/unit/gui/test_session_state.py`

### task-1.8: `MainWindow` esqueleto con layout principal

**Tipo:** test+impl
**Estimación:** 2.5h
**Bloquea:** task-2.1, task-2.11
**Bloqueada por:** task-1.5

**Descripción:** Crear `MainWindow(QMainWindow)` con tres tabs vacías (`convert`, `inspect`, `validate`) y placeholders para `FileDropArea`, `MethodSelector`, `DetectionPreview`, `ProgressPanel`, `ReportViewer`, `LogPanel`. Test: `test_main_window_has_three_tabs` y `test_main_window_title_in_spanish` (REQ-001, REQ-009).

**Criterio de done:**
- [ ] Tests rojos antes de implementar.
- [ ] `MainWindow` instancia OK en `qtbot`.
- [ ] Tres tabs presentes con títulos en español.
- [ ] Strings envueltos con `self.tr(...)`.

**Archivos:**
- `src/tempify/gui/windows/main_window.py`
- `tests/unit/gui/test_main_window_skeleton.py`

### task-1.9: `ProgressCallbackBridge` con `Qt.QueuedConnection`

**Tipo:** test+impl
**Estimación:** 2.5h
**Bloquea:** task-2.10
**Bloqueada por:** task-1.5

**Descripción:** Implementar `ProgressCallbackBridge(QObject)` que adapta el `ProgressCallback` Protocol (`specs/pipeline/requirements.md` REQ-003, 7 fases canónicas) a `Signal(str)` y `Signal(float, str)`. Tests:
- `test_bridge_emits_signal_on_call` desde el thread principal.
- `test_bridge_uses_queued_connection_when_called_from_worker_thread` (verifica `Qt.ConnectionType.QueuedConnection` en el slot conectado).

**Criterio de done:**
- [ ] Tests rojos antes de implementar.
- [ ] El bridge satisface el `ProgressCallback` Protocol (verificable con `isinstance` + `typing.runtime_checkable`).
- [ ] Las 7 fases canónicas son aceptadas (`Literal[...]`).
- [ ] mypy --strict pasa.

**Archivos:**
- `src/tempify/gui/workers/progress_bridge.py`
- `src/tempify/gui/signals.py`
- `tests/unit/gui/test_progress_bridge.py`

## Fase 2: Construcción incremental

### task-2.1: `FileDropArea` widget (REQ-003)

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.11
**Bloqueada por:** task-1.8

**Descripción:** Tests primero:
- `test_drag_enter_accepts_urls` con `QDragEnterEvent` sintético.
- `test_drop_event_emits_paths_dropped` con `QDropEvent` que contiene `file://` URLs.
Implementar widget con `acceptDrops(True)` y signal `paths_dropped: Signal(list[Path])`.

**Criterio de done:**
- [ ] Tests rojos antes de implementar.
- [ ] Widget acepta archivos y carpetas.
- [ ] Signal emite `list[Path]` (no `list[str]`).
- [ ] Tooltip y label en español.

**Archivos:**
- `src/tempify/gui/widgets/file_drop_area.py`
- `tests/unit/gui/test_file_drop_area.py`

### task-2.2: `MethodSelector` widget + bloqueo precipitación (REQ-015, REQ-013)

**Tipo:** test+impl
**Estimación:** 3h
**Bloquea:** task-2.11
**Bloqueada por:** task-1.8

**Descripción:** Tests:
- `test_method_selector_lists_four_methods` (lineal, pchip, pchip_mp, fourier).
- `test_method_selector_disables_smooth_for_precipitation` (perfil `precipitation` deshabilita los 4 métodos suaves y muestra tooltip ADR-0004).
- `test_method_selector_expert_mode_reveals_force_checkbox` (REQ-013).
Implementar `MethodSelector(QWidget)` con `QComboBox` + `update_for_profile(profile: VariableProfile)` + toggle "Modo experto" + checkbox "Forzar método".

**Criterio de done:**
- [ ] Tests rojos antes de implementar.
- [ ] El tooltip referencia textualmente `docs/adr/0004-precipitation-policy.md`.
- [ ] El checkbox "Forzar método" está oculto salvo `expert_mode=True`.
- [ ] Sin "Modo experto", los 4 métodos suaves quedan `setEnabled(False)` para precipitación.

**Archivos:**
- `src/tempify/gui/widgets/method_selector.py`
- `tests/unit/gui/test_method_selector.py`

### task-2.3: `DetectionPreview` widget (REQ-003)

**Tipo:** test+impl
**Estimación:** 1.5h
**Bloquea:** task-2.11
**Bloqueada por:** task-1.8

**Descripción:** Widget que recibe `DetectionResult` y lo renderiza en labels (estructura A/B/C, frecuencia, perfil, count). Test: `test_detection_preview_renders_detection_result` con DTO fake.

**Criterio de done:**
- [ ] Test rojo antes de implementar.
- [ ] Labels mostrados en español (Estructura, Frecuencia, Variable, N° archivos).
- [ ] Estado inicial muestra placeholder "Sin datos".

**Archivos:**
- `src/tempify/gui/widgets/detection_preview.py`
- `tests/unit/gui/test_detection_preview.py`

### task-2.4: `ProgressPanel` widget (REQ-004)

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.11
**Bloqueada por:** task-1.9

**Descripción:** `QProgressBar` + label de fase + botón Cancelar. Slots conectados a los signals del `ProgressCallbackBridge`. Tests:
- `test_progress_panel_updates_on_progress_signal`.
- `test_progress_panel_shows_phase_label`.
- `test_progress_panel_emits_cancel_requested_on_click`.

**Criterio de done:**
- [ ] Tests rojos antes de implementar.
- [ ] Bar muestra "Procesando: 42%" (formato español).
- [ ] Botón Cancelar desactivado fuera de procesamiento.

**Archivos:**
- `src/tempify/gui/widgets/progress_panel.py`
- `tests/unit/gui/test_progress_panel.py`

### task-2.5: `ReportViewer` con `QTextBrowser` (REQ-014, REQ-007)

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.11, task-2.13
**Bloqueada por:** task-1.8

**Descripción:** Subclass `QTextBrowser`, métodos `render(markdown_text: str)` y `save_as(target: Path)`. Tests:
- `test_report_viewer_is_qtextbrowser` (NO `QWebEngineView`).
- `test_report_viewer_renders_markdown` (verifica `toPlainText()` no vacío tras `setMarkdown`).
- `test_report_viewer_save_as_writes_markdown_to_disk`.

**Criterio de done:**
- [ ] Tests rojos antes de implementar.
- [ ] `setOpenExternalLinks(True)`.
- [ ] Alias `MarkdownReportRenderer = ReportViewer` exportado.

**Archivos:**
- `src/tempify/gui/widgets/report_viewer.py`
- `tests/unit/gui/test_report_viewer.py`

### task-2.6: `LogPanel` widget

**Tipo:** test+impl
**Estimación:** 1h
**Bloquea:** task-2.11
**Bloqueada por:** task-1.8

**Descripción:** `QPlainTextEdit` read-only con slot `append_line(line: str)`. Tests: append concatena, mantiene scroll al final, no editable.

**Criterio de done:**
- [ ] Tests rojos antes de implementar.
- [ ] `isReadOnly() is True`.
- [ ] Append funciona desde thread UI vía slot.

**Archivos:**
- `src/tempify/gui/widgets/log_panel.py`
- `tests/unit/gui/test_log_panel.py`

### task-2.7: `FrequencyDisambiguationDialog` (REQ-006)

**Tipo:** test+impl
**Estimación:** 2h
**Bloquea:** task-2.10
**Bloqueada por:** task-1.8

**Descripción:** `QDialog` modal que recibe candidatos en español (`["Mensual", "Climatológica", "Diaria"]`) y retorna la elección. Test: `test_frequency_disambiguation_dialog_returns_choice` con `QTest.mouseClick`.

**Criterio de done:**
- [ ] Test rojo antes de implementar.
- [ ] Botón Aceptar deshabilitado hasta seleccionar opción.
- [ ] Cancelar retorna `None`.

**Archivos:**
- `src/tempify/gui/dialogs/frequency_disambiguation.py`
- `tests/unit/gui/test_frequency_disambiguation_dialog.py`

### task-2.8: `ErrorDialog` con código referenciable (REQ-005, NFR-007)

**Tipo:** test+impl
**Estimación:** 1.5h
**Bloquea:** task-2.11
**Bloqueada por:** task-1.8

**Descripción:** `QDialog` que muestra código (ej `GEO-003`) + mensaje en español + botón "Aceptar". Test: `test_error_dialog_shows_code_and_message`, `test_error_dialog_only_aceptar_button`.

**Criterio de done:**
- [ ] Tests rojos antes de implementar.
- [ ] Código de error monoespaciado y copiable.
- [ ] Cierra sin alterar estado de `MainWindow`.

**Archivos:**
- `src/tempify/gui/dialogs/error_dialog.py`
- `tests/unit/gui/test_error_dialog.py`

### task-2.9: `ForceMethodConfirmationDialog` con "si entiendo" (ADR-0004)

**Tipo:** test+impl
**Estimación:** 1.5h
**Bloquea:** task-2.10
**Bloqueada por:** task-1.8

**Descripción:** Campo de texto que solo autoriza si el usuario escribe literalmente `si entiendo` (case-insensitive, sin tildes). Tests:
- `test_force_method_dialog_rejects_other_text`.
- `test_force_method_dialog_accepts_si_entiendo_case_insensitive`.

**Criterio de done:**
- [ ] Tests rojos antes de implementar.
- [ ] Botón Confirmar deshabilitado hasta match exacto.
- [ ] Texto explicativo cita ADR-0004.

**Archivos:**
- `src/tempify/gui/dialogs/force_method_confirmation.py`
- `tests/unit/gui/test_force_method_confirmation_dialog.py`

### task-2.10: `PipelineWorker(QThread)` con signals tipados y cancel (REQ-016, REQ-008)

**Tipo:** test+impl
**Estimación:** 3.5h
**Bloquea:** task-2.11, task-2.12
**Bloqueada por:** task-1.9, task-2.7, task-2.9

**Descripción:** Implementar `PipelineWorker(QThread)` con los 5 signals declarados en `design.md §3` y un `cancel_event: threading.Event` inyectado. `run()` ejecuta `TempifyPipeline(config).run(source)` y emite `pipeline_finished` o `pipeline_failed`. Tests con `TempifyPipeline` mockeada:
- `test_pipeline_worker_emits_finished_on_success`.
- `test_pipeline_worker_emits_failed_on_exception`.
- `test_pipeline_worker_is_qthread_subclass`.
- `test_pipeline_worker_runs_in_different_thread_than_ui`.
- `test_pipeline_worker_sets_cancel_event_on_request`.

**Criterio de done:**
- [ ] Tests rojos antes de implementar.
- [ ] Worker NO propaga excepciones; las envuelve en `pipeline_failed`.
- [ ] El bridge se construye y conecta dentro de `__init__`.
- [ ] mypy --strict pasa.

**Archivos:**
- `src/tempify/gui/workers/pipeline_worker.py`
- `tests/unit/gui/test_pipeline_worker.py`

### task-2.11: `MainWindow.start_processing()` con worker mock (integration)

**Tipo:** test+impl
**Estimación:** 3h
**Bloquea:** task-2.12, task-3.2
**Bloqueada por:** task-2.1, task-2.2, task-2.3, task-2.4, task-2.5, task-2.6, task-2.8, task-2.10

**Descripción:** Cablear `MainWindow`: signal `paths_dropped` → `set_source` (dry_run worker) → poblar `DetectionPreview` → habilitar `MethodSelector` → botón "Procesar" → `start_processing()` lanza `PipelineWorker`, conecta signals a `ProgressPanel`/`LogPanel`/`ReportViewer`. Tests integración con `PipelineWorker` mock (sin `TempifyPipeline` real):
- `test_main_window_drop_shows_detection_preview` (REQ-003).
- `test_main_window_start_processing_emits_progress` (REQ-004).
- `test_main_window_opens_report_viewer_on_success` (REQ-007).
- `test_main_window_shows_error_dialog_on_failure` (REQ-005).

**Criterio de done:**
- [ ] Tests rojos antes de implementar.
- [ ] Controles deshabilitados durante el procesamiento.
- [ ] Botón Cancelar activo solo durante el procesamiento.

**Archivos:**
- `src/tempify/gui/windows/main_window.py`
- `tests/integration/gui/test_main_window_integration.py`

### task-2.12: `MainWindow.cancel()` con limpieza atómica de `.tmp` (REQ-008, NFR-003)

**Tipo:** test+impl
**Estimación:** 2.5h
**Bloquea:** task-3.2
**Bloqueada por:** task-2.10, task-2.11

**Descripción:** Implementar `cancel()`: dialog de confirmación, `cancel_event.set()`, recorrer `output_dir.glob("*.tmp")` y eliminar. Tests:
- `test_cancel_dialog_returns_to_main_window_on_no`.
- `test_cancel_event_is_set_on_confirm`.
- `test_cancel_deletes_tmp_files_from_output_dir`.
- `test_cancel_leaves_non_tmp_files_untouched`.

**Criterio de done:**
- [ ] Tests rojos antes de implementar.
- [ ] Confirmación modal en español.
- [ ] Nunca elimina archivos sin sufijo `.tmp`.

**Archivos:**
- `src/tempify/gui/windows/main_window.py`
- `tests/integration/gui/test_main_window_cancel.py`

### task-2.13: AST check `test_gui_invokes_pipeline_only` (REQ-002)

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-3.5
**Bloqueada por:** task-2.10

**Descripción:** Recorrer con `ast` todos los módulos de `tempify.gui` y verificar que NO importan `tempify.detection`, `tempify.validation`, `tempify.interpolation`, `tempify.io`. Solo se permite `tempify.pipeline` y tipos de DTOs públicos.

**Criterio de done:**
- [ ] Test falla si se inyecta artificialmente un import prohibido.
- [ ] Test pasa con la estructura actual del paquete.
- [ ] Documentado en docstring del test qué imports están whitelisted.

**Archivos:**
- `tests/unit/gui/test_architecture_imports.py`

### task-2.14: AST check `test_no_qwebengineview_imported` (REQ-014)

**Tipo:** test
**Estimación:** 0.5h
**Bloquea:** task-3.5
**Bloqueada por:** task-2.5

**Descripción:** Similar a 2.13 pero verifica que ningún módulo de `tempify.gui` importa `QtWebEngineWidgets` ni `QWebEngineView`. Adicional: `test_gui_no_network_imports` (Decisión 6, `design.md §6`): bloquea `urllib`, `requests`, `httpx`, `socket`.

**Criterio de done:**
- [ ] Test falla si se inyecta `from PySide6 import QtWebEngineWidgets`.
- [ ] Test falla si se inyecta `import requests` en cualquier módulo `tempify.gui.*`.

**Archivos:**
- `tests/unit/gui/test_architecture_imports.py`

### task-2.15: i18n: archivos `.ts` y compilación `.qm` en build (REQ-009/010)

**Tipo:** test+impl+chore
**Estimación:** 3h
**Bloquea:** task-3.5
**Bloqueada por:** task-2.11

**Descripción:**
- Crear `tempify/gui/i18n/tempify_es.ts` y `tempify_es_CL.ts` extraídos con `pyside6-lupdate`.
- Añadir un step de build (`scripts/build_i18n.py`) que ejecuta `pyside6-lrelease` y genera `.qm`.
- Hook pre-commit `check_i18n_strings.py` que falla si quedan strings sin traducir.
- Tests:
  - `test_gui_ts_files_present_and_compilable`.
  - `test_gui_all_strings_spanish` (recorre widgets visibles).

**Criterio de done:**
- [ ] Tests rojos antes de implementar.
- [ ] `.ts` versionados; `.qm` generados en build (no en repo).
- [ ] Hook pre-commit registrado en `.pre-commit-config.yaml`.

**Archivos:**
- `src/tempify/gui/i18n/tempify_es.ts`
- `src/tempify/gui/i18n/tempify_es_CL.ts`
- `scripts/build_i18n.py`
- `scripts/check_i18n_strings.py`
- `.pre-commit-config.yaml`
- `tests/unit/gui/test_i18n.py`

### task-2.16: Atajos de teclado mínimos (REQ-011)

**Tipo:** test+impl
**Estimación:** 1.5h
**Bloquea:** task-3.5
**Bloqueada por:** task-2.11

**Descripción:** Registrar `QShortcut` en `MainWindow` para `Ctrl+O` (abrir), `Ctrl+S` (guardar sesión), `F1` (ayuda), `Esc` (cerrar diálogo activo). Test `test_gui_keyboard_shortcuts` simula con `qtbot.keyClick`.

**Criterio de done:**
- [ ] Test rojo antes de implementar.
- [ ] Cada atajo invoca el slot correspondiente.
- [ ] Test `test_gui_keyboard_navigation` (NFR-006) verifica orden de Tab.

**Archivos:**
- `src/tempify/gui/windows/main_window.py`
- `tests/unit/gui/test_main_window_shortcuts.py`

## Fase 3: Documentación e integración

### task-3.1: Docstrings NumPy en API pública

**Tipo:** docs
**Estimación:** 2h
**Bloquea:** task-3.6
**Bloqueada por:** task-2.10, task-2.11

**Descripción:** Asegurar que `main`, `MainWindow.{__init__, set_source, start_processing, cancel}`, `PipelineWorker.{__init__, run}`, `ProgressCallbackBridge.__call__`, `MarkdownReportRenderer.{render, save_as}` y `NoEstateError` tengan docstring NumPy completo (Parameters, Returns, Raises, Notes, Examples cuando aplique). Ejecutar `pydocstyle` sobre `tempify.gui`.

**Criterio de done:**
- [ ] `pydocstyle src/tempify/gui` sin warnings (convención numpy).
- [ ] mypy --strict pasa sobre todo `tempify.gui`.

**Archivos:**
- `src/tempify/gui/**/*.py`

### task-3.2: Smoke test integral con fixture WorldClim sintética

**Tipo:** test
**Estimación:** 3.5h
**Bloquea:** task-3.6
**Bloqueada por:** task-2.11, task-2.12

**Descripción:** Generar en `tests/fixtures/worldclim_synthetic/` 12 GeoTIFFs mensuales 3×3 px (helper en `conftest.py` si no existe). Test `test_gui_full_workflow_with_fixture`: drop de la carpeta, método PCHIP+RM, output `tmp_path`, formato NetCDF. Verifica que aparece `ReportViewer` con Markdown y que existe el NetCDF resultante.

**Criterio de done:**
- [ ] Fixture reusable desde otros specs.
- [ ] Smoke test pasa en CI Windows (offscreen).
- [ ] Tiempo total del test < 30 s.

**Archivos:**
- `tests/integration/gui/test_full_workflow.py`
- `tests/fixtures/worldclim_synthetic/conftest.py` (o helper)

### task-3.3: Benchmark cold start GUI < 5 s

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-3.6
**Bloqueada por:** task-2.11

**Descripción:** `test_gui_cold_start_under_5s`: `time.perf_counter()` antes de `main(["--check-startup"])` (modo que crea `MainWindow` y sale inmediatamente). Marcado `@pytest.mark.benchmark` y opcional en CI.

**Criterio de done:**
- [ ] Test rojo si el arranque supera 5 s en Windows.
- [ ] Marcador `slow` documentado en `pyproject.toml`.

**Archivos:**
- `tests/integration/gui/test_cold_start_benchmark.py`
- `src/tempify/gui/app.py` (añadir flag `--check-startup`)

### task-3.4: Latencia UI < 100 ms durante procesamiento (NFR-002)

**Tipo:** test
**Estimación:** 1.5h
**Bloquea:** task-3.6
**Bloqueada por:** task-2.10

**Descripción:** `test_gui_ui_responsive_during_processing`: lanza `PipelineWorker` con job dummy (`time.sleep` en thread separado), simula click en un botón inerte y mide con `QTest.qWait` que la respuesta llega en < 100 ms.

**Criterio de done:**
- [ ] Test estable (sin flakiness) en 10 ejecuciones consecutivas.
- [ ] Documentado el margen de tolerancia para CI lento.

**Archivos:**
- `tests/integration/gui/test_ui_responsiveness.py`

### task-3.5: Manual test plan documentado

**Tipo:** docs
**Estimación:** 1.5h
**Bloquea:** task-3.6
**Bloqueada por:** task-2.13, task-2.14, task-2.15, task-2.16

**Descripción:** Crear `docs/tutorials/gui_quickstart.md` con plan de prueba manual: instalación, primer drag&drop, conversión completa, cancelación, validación, exportar reporte. Capturas opcionales.

**Criterio de done:**
- [ ] Documento incluye checklist manual de los 16 REQ.
- [ ] Enlazado desde el README.
- [ ] Lenguaje en español.

**Archivos:**
- `docs/tutorials/gui_quickstart.md`
- `README.md`

### task-3.6: CHANGELOG y cierre de spec

**Tipo:** docs
**Estimación:** 0.5h
**Bloquea:** —
**Bloqueada por:** task-3.1, task-3.2, task-3.3, task-3.4, task-3.5

**Descripción:** Añadir entrada `Unreleased` al CHANGELOG con resumen de la GUI v0.1 (REQ implementados, NFR cumplidos, deudas conocidas: cancelación cooperativa interna del pipeline, fallback `QWebEngineView`). Actualizar `impl-log.md` con el cierre. Mover estado de la spec a `Complete`.

**Criterio de done:**
- [ ] CHANGELOG referencia la spec `gui` y los ADRs 0004, 0005, 0014.
- [ ] `specs/gui/impl-log.md` cerrado con fecha y autor.
- [ ] `requirements.md` y `design.md` con estado `Complete`.

**Archivos:**
- `CHANGELOG.md`
- `specs/gui/impl-log.md`
- `specs/gui/requirements.md`
- `specs/gui/design.md`
- `specs/gui/tasks.md` (este archivo: estado `Complete`)

## Resumen

| Fase | # tasks | Estimación total |
|---|---|---|
| Fase 1 — Fundamentos | 9 | 17h |
| Fase 2 — Construcción incremental | 16 | 33.5h |
| Fase 3 — Documentación e integración | 6 | 10.5h |
| **Total** | **31** | **61h** |

## Trazabilidad tasks → requirements

| REQ / NFR | Task(s) |
|---|---|
| REQ-001 | task-1.8 |
| REQ-002 | task-2.10, task-2.13 |
| REQ-003 | task-2.1, task-2.3, task-2.11 |
| REQ-004 | task-2.4, task-2.11 |
| REQ-005 | task-2.8, task-2.11 |
| REQ-006 | task-2.7, task-2.11 |
| REQ-007 | task-2.5, task-2.11 |
| REQ-008 | task-2.12 |
| REQ-009 | task-1.5, task-2.15 |
| REQ-010 | task-2.15 |
| REQ-011 | task-2.16 |
| REQ-012 | task-1.6 |
| REQ-013 | task-2.2 |
| REQ-014 | task-2.5, task-2.14 |
| REQ-015 | task-2.2 |
| REQ-016 | task-2.10 |
| NFR-001 | task-2.15 |
| NFR-002 | task-3.4 |
| NFR-003 | task-2.12 |
| NFR-004 | task-1.4 |
| NFR-005 | task-3.6 (verificación final de cobertura) |
| NFR-006 | task-2.16 |
| NFR-007 | task-2.8 |
| NFR-008 | task-2.15 |
