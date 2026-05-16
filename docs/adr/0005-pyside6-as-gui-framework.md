# ADR-0005: PySide6 como framework GUI

**Estado:** Accepted
**Fecha:** 2026-05-16
**Decision-makers:** Guillermo Fuentes-Jaque

## Contexto

tempify debe ofrecer una interfaz gráfica de escritorio en español dirigida a usuarios no programadores Windows (investigadores, consultores, técnicos ambientales) que no operan entornos Python. La spec [gui](../../specs/gui/requirements.md) establece requisitos concretos sobre la capa de presentación:

- Drag&drop nativo de archivos y carpetas al área central.
- Vista previa de detección antes de procesar (estructura, frecuencia, perfil de variable).
- Barra de progreso no-bloqueante con cancelación cooperativa durante operaciones largas.
- Panel de log con streaming de eventos del pipeline.
- Visor del reporte final en Markdown renderizado.
- Diálogos modales en español, con infraestructura para i18n a otros idiomas.
- Look nativo en Windows 10/11 (audiencia primaria) y soporte best-effort en Linux y macOS.

Adicionalmente, la spec [packaging](../../specs/packaging/requirements.md) impone que el framework elegido debe ser empaquetable vía PyInstaller en un instalador `.exe` self-contained menor a 300 MB (NFR-002), sin requerir Python en la máquina destino.

Existen varios frameworks GUI disponibles en el ecosistema Python:

1. **Tkinter** (stdlib)
2. **PyQt6**
3. **PySide6** (Qt for Python)
4. **Toga** (BeeWare)
5. **wxPython**
6. **Electron / Tauri** (web envuelta en webview)
7. **Streamlit / Gradio** (servidores web)

## Decisión

Usar **PySide6** (Qt for Python 6.x, distribución oficial de The Qt Company) como framework GUI de tempify, declarado como extra opcional `tempify[gui]` en `pyproject.toml`, con versión mínima `PySide6 >= 6.6`.

## Justificación

### Pros de PySide6

- **Licencia LGPL v3**, compatible con la licencia MIT del paquete y con el esquema híbrido MIT/AGPL del proyecto, sin obligación de relicenciar el código de tempify.
- **Look nativo** en Windows 10/11 vía el estilo `windowsvista` y `windows11` de Qt 6, satisfaciendo el requisito de usabilidad para audiencia no programadora.
- **Signals/slots maduros** que se integran directamente con el callback de progreso del pipeline (`Signal(int, str, str)` para porcentaje, mensaje y fase).
- **QThread y QRunnable/QThreadPool nativos** que permiten ejecutar el pipeline en hilo separado sin bloquear la UI (NFR-002 de la spec gui).
- **Drag&drop completo** vía `QDropEvent` y `QMimeData`, indispensable para REQ-003 de la spec gui.
- **Qt Linguist** para i18n con archivos `.ts` y `.qm`, alineado con REQ-009 y REQ-010 de la spec gui.
- **QWebEngineView** disponible (opcional) para el visor de Markdown si `QTextBrowser` resulta insuficiente.
- **pytest-qt** maduro para tests de UI, alineado con NFR-005 de la spec gui.
- **Ecosistema amplio**: documentación oficial, tooling (`pyside6-lupdate`, `pyside6-uic`, `pyside6-rcc`), comunidad activa.

### Contras de PySide6

- **Bundle pesado en PyInstaller**: el bundle Qt completo puede exceder 150 MB sin recorte. Mitigado mediante `--exclude-module` de plugins Qt no utilizados (sql, multimedia, declarative, webengine si no se usa) en `packaging/pyinstaller.spec` (cubierto por ADR-0006).
- **Curva de aprendizaje** para desarrolladores no familiarizados con Qt y el patrón signals/slots.
- **Cold start** ligeramente mayor que Tkinter (mitigado: NFR-001 packaging exige < 5 s, alcanzable con `--onedir`).

### Por qué no las alternativas

- **Tkinter (stdlib)**: look anticuado en Windows 11, sin equivalente maduro a signals/slots, drag&drop limitado (`tkinterdnd2` es de terceros y frágil), sin sistema de i18n integrado, ecosistema de widgets reducido. Descartado por experiencia de usuario insuficiente para audiencia no programadora.
- **PyQt6**: misma base técnica Qt 6, prácticamente equivalente a PySide6 en capacidad, pero licenciado bajo **GPL v3** con opción comercial de Riverbank. Incompatible con la licencia MIT del paquete y con la distribución como extra `tempify[gui]` sin obligar a los usuarios a respetar GPL. Descartado por restricción de licencia comercial.
- **Toga (BeeWare)**: framework joven, ecosistema y cobertura de widgets limitada en Windows, especialmente para drag&drop avanzado, threading y visores Markdown ricos. Descartado por madurez insuficiente para v0.1.0.
- **wxPython**: maduro pero con look anticuado en Windows 11, comunidad declinante, menos pulido visualmente. Descartado por experiencia de usuario y trayectoria del proyecto.
- **Electron / Tauri**: introducen un stack web (Node/Rust) ajeno al ecosistema Python, bundle aún más pesado que Qt (Electron) o requieren toolchain Rust (Tauri), complican empaquetado y testing. Descartado por overhead.
- **Streamlit / Gradio**: son servidores web, no aplicaciones de escritorio; requieren un host Python corriendo en el cliente, contradicen el requisito REQ-001 de la spec packaging (`.exe` self-contained sin Python). Descartados por categoría errónea.

## Consecuencias

### Positivas

- Look nativo en Windows 11, alineado con la expectativa de la audiencia objetivo.
- Licencia LGPL v3 compatible con MIT y AGPL, sin contaminación viral del código de tempify.
- Ecosistema maduro (signals/slots, QThread, Qt Linguist, pytest-qt) reduce trabajo de infraestructura.
- Threading y cancelación cooperativa quedan resueltos por primitivas nativas (QThread/QRunnable).
- i18n queda resuelto por Qt Linguist (`.ts` y `.qm`) con flujo de trabajo estándar.
- Tests de UI viables vía `pytest-qt` (NFR-005 de la spec gui).

### Negativas

- Bundle PyInstaller pesado por el peso de Qt. Mitigación: `--onedir` y exclusión de plugins Qt no utilizados (cubierto en ADR-0006).
- Dependencia opcional pesada (~80 MB instalada) cuando el usuario activa el extra `gui`. Usuarios CLI-only no se ven afectados.
- Costo de aprendizaje para nuevos contribuyentes no familiarizados con Qt.

### Riesgos

- **SmartScreen** marca el instalador no firmado como riesgoso (ver spec packaging, riesgo correspondiente). No es riesgo del framework sino del empaquetado; queda fuera de esta ADR.
- Conflictos entre el scheduler de Dask y QThread; se mitiga aislando el job pipeline en `QRunnable` con scheduler síncrono Dask o `concurrent.futures` aislado (cubierto por la spec gui, riesgo registrado).
- API de PySide6 evoluciona; pinear `>= 6.6, < 7` y revisar cambios mayores en upgrades.

## Notas de implementación

- **Versión mínima**: `PySide6 >= 6.6` declarada en `pyproject.toml`.
- **Distribución**: extra opcional `tempify[gui]`, instalable vía `pip install tempify[gui]`. El núcleo y el CLI no dependen de PySide6.
- **Threading**: el patrón concreto (QThread vs QRunnable + QThreadPool) se difiere a ADR-0011 y a `specs/gui/design.md`. Por defecto se preferirá `QRunnable` en `QThreadPool` para el job principal del pipeline.
- **Markdown rendering**: la elección entre `QTextBrowser` (más ligero, suficiente para Markdown básico) y `QWebEngineView` (más pesado, soporta HTML completo) se difiere a ADR-0012 y a `specs/gui/design.md`. Por defecto se preferirá `QTextBrowser` para mantener el bundle ligero.
- **i18n**: archivos `.ts` versionados en `tempify/gui/i18n/`, compilados a `.qm` en build. Locale por defecto `es` (con variante `es_CL`), infraestructura preparada para `en` y futuros idiomas.
- **Empaquetado**: ver ADR-0006 (PyInstaller + Inno Setup) para detalles de exclusión de plugins Qt y reducción de tamaño del bundle.
- **Testing**: tests de UI con `pytest-qt`, cobertura mínima del módulo `tempify.gui` >= 70% (NFR-005 de la spec gui).

## Referencias

- PySide6 (Qt for Python): https://doc.qt.io/qtforpython-6/
- Licencia LGPL v3: https://www.gnu.org/licenses/lgpl-3.0.html
- Qt Linguist Manual: https://doc.qt.io/qt-6/qtlinguist-index.html
- Qt Threading Basics: https://doc.qt.io/qt-6/thread-basics.html
- pytest-qt: https://pytest-qt.readthedocs.io/
- spec [gui](../../specs/gui/requirements.md)
- spec [packaging](../../specs/packaging/requirements.md)
- ADR-0006 (pendiente): PyInstaller + Inno Setup como cadena de empaquetado Windows.
