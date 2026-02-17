# Changelog

All notable changes to CBERS Explorer are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] — 2026-02-17

Complete architectural redesign. The monolithic single-file plugin has been replaced with a layered architecture (Domain, Infra, App, UI) with reactive state management and professional UX.

### Added

- **Quick Search panel** — search by canvas bounding box with date presets (7 days, 30 days, 1 year) and fixed collection (CB4A-WPM-PCA-FUSED-1).
- **Advanced Search panel** — flexible ROI (canvas extent, layer extent, selected features), dynamic collection loading from STAC catalog, configurable items per page.
- **Paginated results** — QTableView with StacItemTableModel, page navigation, result count display.
- **Item Details panel** — metadata properties, async thumbnail preview, full asset list with per-asset actions.
- **Download Manager panel** — download queue with progress bars, cancel all, auto-add to map on completion.
- **Activity Bar navigation** — vertical icon bar (SVG, Feather style) with 5 panels, accent indicator, hover states, badge counters.
- **COG streaming** — load remote Cloud-Optimized GeoTIFFs via `/vsicurl/` without downloading.
- **VRT mosaic support** — build virtual raster from multiple COG assets.
- **AppState** — reactive state store with `pyqtSignal` properties driving all UI updates.
- **Auto-navigation** — search completion jumps to Results; item selection jumps to Details.
- **ConfigRepository** — persistent settings via `QgsSettings` with namespaced keys.
- **HttpClient** — async HTTP via `QgsNetworkAccessManager` (collections loading).
- **SearchTask / DownloadTask** — non-blocking operations via `QgsTask` worker threads.
- **i18n support** — 109 translatable strings, English and Portuguese (pt-BR) translations compiled.
- **Error normalization** — friendly HTTP error messages for all common status codes.
- **Copy URL to clipboard** — from both Results and Details panels.
- **INSTALLATION.md** — technical setup and build instructions.
- **CHANGELOG.md** — this file.

### Changed

- **Entry point** — `classFactory` now loads `plugin.py` → `CbersExplorerPlugin` instead of `cbers_explorer.py` → `CbersExplorer`.
- **HTTP layer** — replaced `requests` library (forbidden in QGIS plugins) with native `QgsNetworkAccessManager` and `QgsBlockingNetworkRequest`.
- **UI architecture** — replaced single monolithic `QDockWidget` with `ActivityBar` + `QStackedWidget` hosting 5 independent panels.
- **Layer loading** — direct `QgsRasterLayer` with `/vsicurl/` URI instead of VRT-only approach.
- **Makefile** — updated `PY_FILES`, `EXTRA_DIRS`, `LOCALES`, `deploy` target for new directory structure.
- **pb_tool.cfg** — updated `python_files`, `extra_dirs`, `locales` for v2.0.0.
- **metadata.txt** — bumped to v2.0.0, updated description, added changelog, added tags, raised minimum QGIS to 3.22.
- **README.md** — rewritten for end users with feature overview, quick start, and interface guide.

### Removed

- `requests` Python dependency.
- `cbers_explorer_dockwidget_base.ui` — UI is now fully programmatic.
- Hardcoded single-collection limitation.
- `QMessageBox` popups — replaced with non-intrusive `iface.messageBar()`.

### Deprecated

- `cbers_explorer.py` and `cbers_explorer_dockwidget.py` — still present in the repository but no longer loaded. Will be removed in a future release.

---

## [1.0.0] — 2024-07-19

Initial release.

### Added

- Search CBERS-4A WPM imagery from BDC STAC (`CB4A-WPM-PCA-FUSED-1`).
- Bounding box from canvas extent with coordinate reprojection to EPSG:4326.
- Date range filter (start/end).
- Results table with image ID, creation date, modification date.
- Load selected image as COG via VRT on the map canvas.
- Copy COG URL to clipboard.
- English and Portuguese (pt-BR) translations.
- XML-based raster styling with RGB contrast enhancement.

---

[2.0.0]: https://github.com/lapig-ufg/cbers-explorer/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/lapig-ufg/cbers-explorer/releases/tag/v1.0.0
