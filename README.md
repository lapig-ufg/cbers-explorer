# CBERS Explorer

A QGIS plugin to search, preview, and load CBERS-4A satellite imagery directly from the [Brazil Data Cube (BDC) STAC catalog](https://data.inpe.br/bdc/stac/v1/).

Built for researchers, analysts, and GIS professionals who need fast access to high-resolution Earth observation data within their QGIS workflow.

![QGIS](https://img.shields.io/badge/QGIS-%3E%3D3.22-green) ![Version](https://img.shields.io/badge/version-2.0.0-blue) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## What It Does

CBERS Explorer connects QGIS to Brazil's STAC imagery catalog. You can search for satellite scenes by area and date, browse results in a paginated table, inspect item details with thumbnails, load Cloud-Optimized GeoTIFFs (COG) straight onto the map canvas, and download assets locally.

## Features

- **Quick Search** — One-click search using the current canvas extent, date range presets (7 days, 30 days, 1 year), and a fixed high-resolution collection (CB4A-WPM-PCA-FUSED-1, 2m RGB PCA fusion).
- **Advanced Search** — Flexible region of interest (canvas extent, layer extent, or selected features), any STAC collection, and configurable result limits.
- **Paginated Results** — Browse large result sets page by page. Select items to add to the map, copy asset URLs, or open item details.
- **Item Details** — View metadata, bounding box, cloud cover, thumbnail preview, and a full list of assets per item.
- **COG Streaming** — Load remote COG imagery via `/vsicurl/` with no download required. Build VRT mosaics from multiple assets.
- **Download Manager** — Download assets with progress tracking. Optionally add downloaded files to the map automatically.
- **Internationalization** — Full i18n support for English and Portuguese (pt-BR).

## Supported Data

| Source | Endpoint |
|--------|----------|
| Brazil Data Cube STAC | `https://data.inpe.br/bdc/stac/v1/` |

Default collection for Quick Search: **CB4A-WPM-PCA-FUSED-1** (CBERS-4A WPM, 2m RGB, PCA fusion).

Advanced Search loads all available collections dynamically from the STAC catalog.

## Quick Start

1. Install the plugin (see [INSTALLATION.md](INSTALLATION.md)).
2. Click the **CBERS Explorer** button in the toolbar.
3. The dock panel opens on the right with five navigation tabs.
4. In **Quick Search**, click **Update Bbox**, pick a date range, and hit **Search**.
5. Results appear in the **Results** tab. Double-click an item to see its details.
6. Click **Add to Map** to stream the COG directly onto the canvas.

## Interface Overview

The plugin uses a vertical activity bar (left) with five panels:

| Icon | Panel | Purpose |
|------|-------|---------|
| ![bolt](assets/icons/nav_quick_search.svg) | Quick Search | Canvas bbox + dates + fixed collection |
| ![filter](assets/icons/nav_advanced_search.svg) | Advanced Search | Flexible ROI, dynamic collections, filters |
| ![list](assets/icons/nav_results.svg) | Results | Paginated table with actions |
| ![doc](assets/icons/nav_details.svg) | Details | Metadata, thumbnail, asset list |
| ![download](assets/icons/nav_downloads.svg) | Downloads | Progress tracking, auto-add to map |

Navigation is automatic: searching jumps to Results; selecting an item jumps to Details.

## Architecture

Version 2.0.0 follows a layered architecture:

```
domain/     Pure data models and STAC parsers (no QGIS dependency)
infra/      HTTP client, QgsSettings, QgsTask workers
app/        Reactive state (AppState), controllers (search, download, layer)
ui/         Dock, activity bar, widget panels
```

All HTTP uses native QGIS networking (`QgsNetworkAccessManager`, `QgsBlockingNetworkRequest`). Long operations run in `QgsTask` worker threads so the UI never blocks.

## Requirements

- QGIS 3.22 or later
- No external Python dependencies (no `requests`, no `pip install`)

## License

MIT License. See [LICENSE](LICENSE).

## Support

Issues and feature requests: [github.com/lapig-ufg/cbers-explorer/issues](https://github.com/lapig-ufg/cbers-explorer/issues)

Developed by **Tharles de Sousa Andrade** | [LAPIG/UFG](https://www.lapig.iesa.ufg.br/)
