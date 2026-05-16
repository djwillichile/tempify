# Requirements — gui

**Estado:** Draft
**Owner:** Guillermo Fuentes-Jaque
**Fecha creación:** 2026-05-16
**Última actualización:** 2026-05-16

## 1. Propósito

Proveer una interfaz gráfica de escritorio en español que permita a usuarios sin conocimientos de Python invocar las conversiones de densificación temporal del pipeline de tempify mediante drag&drop, selección visual del método de interpolación y visualización del reporte. La GUI es una capa cliente equivalente al CLI: NO contiene lógica de negocio y delega toda operación en `tempify.pipeline.tempifyPipeline.run()`.

## 2. Alcance

### In-scope

- Ventana principal (`MainWindow`) con área central de drag&drop para archivos y carpetas.
- Tres operaciones expuestas con paridad funcional con la CLI: convertir, inspeccionar, validar.
- Selector visual de método de interpolación (`Lineal`, `PCHIP`, `PCHIP+Rymes-Myers`, `Fourier`) con descripción contextual y advertencias (ej: precipitación bloquea métodos suaves).
- Vista previa de detección (`DetectionPreviewPanel`) que muestra modo de estructura (A/B/C), frecuencia temporal inferida y perfil de variable antes de procesar.
- Selector de carpeta y formato de salida (NetCDF, GeoTIFF colección, GeoTIFF multibanda, Zarr).
- Barra de progreso (`ProgressPanel`) conectada al callback del pipeline mediante señales Qt (`pyqtSignal`/`Signal`).
- Botón "Cancelar" funcional durante el procesamiento.
- Panel inferior de log (`LogPanel`) con streaming de eventos del pipeline.
- Visor del reporte final (`ReportViewer`) con Markdown renderizado.
- Diálogos modales en español para prompts interactivos (frecuencia ambigua, ambigüedades de perfil de variable, confirmación de cancelación).
- Diálogos modales de error con código referenciable (compatible con la taxonomía de errores del pipeline).
- Archivos de traducción `.ts` (Qt Linguist) versionados en `tempify/gui/i18n/` para soporte futuro de i18n.

### Out-of-scope

- Lógica de negocio (detección, validación, interpolación, I/O): pertenece a las capas inferiores invocadas vía `tempify.pipeline`.
- Visualización del ráster como mapa o renderizado geoespacial (no es un GIS).
- Comparación entre métodos de interpolación en tiempo real (diferido a una versión futura).
- Editor de perfiles de variable personalizados (diferido).
- Empaquetado del ejecutable Windows standalone (cubierto por la spec `packaging`).
- Telemetría, actualizaciones automáticas, ni servicios de red.

## 3. Actores y casos de uso

### Actor 1: Investigador no-programador

> Como investigadora junior en climatología aplicada, quiero una interfaz gráfica en español para convertir mis stacks WorldClim mensuales a series diarias, sin tener que aprender Python ni línea de comandos.

**Caso de uso típico:** La usuaria abre tempify, arrastra una carpeta con 12 GeoTIFFs WorldClim mensuales al área central; la GUI muestra el panel de detección con "Estructura: B (colección de monocapas)", "Frecuencia: mensual", "Variable: tas (temperatura media)". Selecciona el método `PCHIP+Rymes-Myers` en el desplegable, elige una carpeta de salida y formato NetCDF, presiona "Procesar". Observa la barra de progreso, ve mensajes del log; al finalizar, se abre el visor del reporte renderizado.

### Actor 2: Técnico ambiental en consultoría

> Como técnico que prepara inputs climáticos para un EIA, quiero validar un archivo NetCDF antes de procesarlo y obtener un reporte que pueda anexar a documentación oficial.

**Caso de uso típico:** El técnico abre la GUI, selecciona la pestaña "Validar", arrastra un NetCDF, la GUI invoca `tempifyPipeline` en modo `validate`. Si la validación falla, aparece un diálogo modal con el código de error (ej: `GEO-003`) y la descripción en español. Si pasa, el reporte se muestra en el visor y se ofrece la opción "Guardar reporte como…".

## 4. Requisitos funcionales (formato EARS)

### REQ-001 (Ubiquitous)

THE SYSTEM SHALL expose three primary operations equivalent to the CLI subcommands: `convert`, `inspect`, and `validate`, each accessible from the main window via tabs or explicit action buttons.

### REQ-002 (Ubiquitous)

THE SYSTEM SHALL invoke business logic exclusively through `tempify.pipeline.tempifyPipeline.run()` and SHALL NOT duplicate or reimplement detection, validation, interpolation, or I/O logic.

### REQ-003 (Event-driven)

WHEN the user drops a file or directory onto the drag&drop area, THE SYSTEM SHALL invoke detection-only mode and display a `DetectionPreviewPanel` showing structure mode, inferred temporal frequency, variable profile, and file count, without triggering processing.

### REQ-004 (State-driven)

WHILE a `convert` operation is running, THE SYSTEM SHALL display a non-blocking progress bar with the current percentage (e.g., `"Procesando: 42%"`), stream pipeline events to the log panel, and present an active "Cancelar" button.

### REQ-005 (Event-driven)

WHEN a pre-processing validation fails (geospatial coherence, method/variable incompatibility), THE SYSTEM SHALL show a modal dialog containing the referenceable error code (e.g., `GEO-003`), the localized Spanish message, and an "Aceptar" button that returns control to the main window without altering state.

### REQ-006 (Event-driven)

WHEN the pipeline cannot resolve temporal frequency automatically, THE SYSTEM SHALL show a modal dialog `FrequencyResolutionDialog` presenting the candidate frequencies in Spanish (e.g., `"Mensual"`, `"Climatológica"`, `"Diaria"`) and SHALL forward the user selection back to the pipeline callback.

### REQ-007 (Event-driven)

WHEN the `convert` operation completes successfully, THE SYSTEM SHALL automatically open the `ReportViewer` with the Markdown report rendered, and SHALL offer a "Guardar reporte como…" action.

### REQ-008 (Event-driven)

WHEN the user clicks "Cancelar" during processing, THE SYSTEM SHALL request cooperative cancellation of the pipeline thread, display the confirmation dialog `"¿Desea cancelar la operación?"`, and on confirmation SHALL ensure no partial output files remain in the user-selected output directory.

### REQ-009 (Ubiquitous)

THE SYSTEM SHALL display all user-facing labels, messages, buttons, dialogs, and tooltips in Spanish by default, using strings extracted via Qt's `tr()` mechanism so they can be re-translated.

### REQ-010 (Ubiquitous)

THE SYSTEM SHALL version Qt Linguist translation source files (`.ts`) under `tempify/gui/i18n/` for at least the default `es_CL` locale, and SHALL compile them to `.qm` at build time.

### REQ-011 (Ubiquitous)

THE SYSTEM SHALL support the following keyboard shortcuts: `Ctrl+O` (abrir archivo/carpeta), `Ctrl+S` (guardar configuración de sesión), `F1` (ayuda), `Esc` (cerrar diálogo modal activo).

### REQ-012 (Unwanted condition)

IF the GUI is launched in an environment without a graphical display (no `DISPLAY`, no Wayland, no Windows session), THEN THE SYSTEM SHALL fail with a typed exception `NoDisplayError` carrying a Spanish message instructing the user to use the CLI instead, and SHALL exit with status code 4.

### REQ-013 (Optional feature)

WHERE the user enables the "Modo experto" toggle in the settings dialog, THE SYSTEM SHALL display additional parameters (chunk size, número de armónicos de Fourier, iteraciones de Rymes-Myers) that are normally hidden behind defaults.

## 5. Requisitos no funcionales

| ID | Categoría | Requisito | Criterio verificable |
|---|---|---|---|
| NFR-001 | Usability | Toda la interfaz por defecto en español validado por inspección automática | Test `test_gui_all_strings_spanish` verifica que no haya strings inglesas en widgets visibles |
| NFR-002 | Performance | La UI nunca bloquea: el pipeline corre en `QThread`/`QRunnable` separado del hilo de UI | Test `test_gui_ui_responsive_during_processing` mide latencia de respuesta a eventos < 100 ms mientras un job dummy procesa |
| NFR-003 | Reliability | La cancelación nunca deja outputs corruptos: escritura a archivos temporales con rename atómico al final | Test `test_gui_cancel_no_partial_output` confirma que tras cancelar no quedan archivos en el directorio de salida |
| NFR-004 | Portability | Soporte primario Windows 10/11; soporte best-effort Linux (X11/Wayland) y macOS | CI ejecuta tests en Windows obligatorio, Linux como job adicional |
| NFR-005 | Maintainability | Cobertura del módulo `tempify.gui` >= 70% con `pytest-qt` | Reporte de cobertura en CI |
| NFR-006 | Accessibility | Atajos de teclado funcionales y todos los widgets interactivos alcanzables vía `Tab` | Test `test_gui_keyboard_navigation` recorre el orden de tabulación |
| NFR-007 | Usability | Mensajes de error muestran código referenciable y descripción en español | Test `test_gui_error_dialog_format` |
| NFR-008 | Maintainability | Strings de UI extraíbles vía `pyside6-lupdate` sin warnings | Hook pre-commit `check_i18n_strings.py` |

## 6. Criterios de aceptación

Lista verificable que define cuándo esta spec está completamente implementada:

- [ ] REQ-001 cubierto por test `test_gui_three_operations_available`
- [ ] REQ-002 cubierto por test `test_gui_invokes_pipeline_only` (mock del pipeline, verifica que no se importan módulos de detection/io/interpolation directamente)
- [ ] REQ-003 cubierto por test `test_gui_drop_shows_detection_preview`
- [ ] REQ-004 cubierto por test `test_gui_progress_bar_and_log_during_run`
- [ ] REQ-005 cubierto por test `test_gui_prevalidation_error_dialog`
- [ ] REQ-006 cubierto por test `test_gui_frequency_resolution_dialog`
- [ ] REQ-007 cubierto por test `test_gui_report_viewer_opens_on_success`
- [ ] REQ-008 cubierto por test `test_gui_cancel_no_partial_output`
- [ ] REQ-009 cubierto por test `test_gui_all_strings_spanish`
- [ ] REQ-010 cubierto por test `test_gui_ts_files_present_and_compilable`
- [ ] REQ-011 cubierto por test `test_gui_keyboard_shortcuts`
- [ ] REQ-012 cubierto por test `test_gui_no_display_raises_NoDisplayError`
- [ ] REQ-013 cubierto por test `test_gui_expert_mode_reveals_advanced_params`
- [ ] NFR-002 medido por `test_gui_ui_responsive_during_processing`
- [ ] NFR-005 cobertura `tempify.gui` >= 70% en reporte de CI
- [ ] Smoke test de integración `test_gui_full_workflow_with_fixture` (drop carpeta fixture WorldClim sintética, método PCHIP+RM, output a `tmp_path`, verifica reporte y NetCDF generado)
- [ ] Documentación de usuario actualizada en `docs/tutorials/gui_quickstart.md`
- [ ] CHANGELOG actualizado

## 7. Dependencias y supuestos

### Specs relacionadas

- Bloqueada por: [pipeline](../pipeline/requirements.md) (depende del contrato de `tempifyPipeline.run()` y de su callback de progreso compatible con señales Qt).
- Bloqueada por: [cli](../cli/requirements.md) (paridad de operaciones, taxonomía de códigos de error, mensajería en español).
- Bloquea: `packaging` (el empaquetado PyInstaller del ejecutable Windows requiere esta GUI como entry point).

### Supuestos

- El entorno de ejecución dispone de un display gráfico (sesión Windows interactiva, X11/Wayland en Linux, Quartz en macOS).
- `PySide6>=6.6` está instalado como dependencia opcional vía el extra `gui` en `pyproject.toml` (`pip install tempify[gui]`).
- El callback de progreso del pipeline emite eventos estructurados (porcentaje, mensaje, fase) compatibles con ser envueltos en `Signal(int, str, str)` de Qt.
- Las traducciones se versionan en `tempify/gui/i18n/tempify_es_CL.ts` con compilación a `.qm` en build.
- El framework GUI es **PySide6** (decisión locked, ADR-0005 pendiente).

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| PySide6 en PyInstaller produce binarios pesados (>200 MB) | Alta | Medio | Usar `--onedir` y `--exclude-module` para plugins Qt no usados (sql, multimedia, webengine); documentar tamaño esperado en spec `packaging` |
| Drift entre strings en código y archivos `.ts` traducidos | Media | Medio | Hook pre-commit que ejecuta `pyside6-lupdate --no-obsolete` y falla si hay strings sin traducir |
| Cancelación cooperativa no atómica deja outputs parciales | Media | Alto | Escribir siempre a archivos temporales (`.tmp` en mismo filesystem) y hacer `os.replace` al final; en cancelación, borrar los `.tmp` |
| Bloqueo del hilo de UI por operaciones I/O pesadas | Media | Alto | Toda operación pipeline en `QThread` separado; tests `pytest-qt` que verifican responsividad |
| Diferencias de comportamiento Qt entre Windows y Linux | Baja | Bajo | CI con jobs paralelos en ambos sistemas; documentar limitaciones macOS como best-effort |
| Conflictos entre threading de Dask y QThread | Media | Medio | Usar `QRunnable`/`QThreadPool` para el job principal; configurar Dask con scheduler síncrono dentro del worker o `concurrent.futures` aislado |

## 8. Referencias

- PySide6 documentation: https://doc.qt.io/qtforpython-6/
- pytest-qt: https://pytest-qt.readthedocs.io/
- Qt Linguist Manual: https://doc.qt.io/qt-6/qtlinguist-index.html
- Qt Threading Basics: https://doc.qt.io/qt-6/thread-basics.html
- CF Conventions: https://cfconventions.org/
- EARS notation: https://alistairmavin.com/ears/
- spec [cli](../cli/requirements.md) (paridad funcional)
- spec [pipeline](../pipeline/requirements.md) (contrato de invocación)
