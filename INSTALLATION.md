# Installation

## From ZIP (recommended)

1. Download the latest release ZIP from [GitHub Releases](https://github.com/lapig-ufg/cbers-explorer/releases).
2. Open QGIS.
3. Go to **Plugins > Manage and Install Plugins... > Install from ZIP**.
4. Select the downloaded `cbers_explorer.zip` file.
5. Click **Install Plugin**.
6. Enable **CBERS Explorer** in the plugin list if it is not already active.

## From Source (development)

### Prerequisites

- QGIS 3.22+
- Git
- `make` (Linux/macOS) or manual copy (Windows)
- `lrelease` (for compiling translations — included with Qt)

### Clone and Deploy

```bash
git clone https://github.com/lapig-ufg/cbers-explorer.git
cd cbers-explorer
```

**Linux / macOS:**

```bash
make transcompile
make deploy
```

This compiles `.ts` translation files to `.qm` and copies all plugin files to:

```
~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/cbers_explorer/
```

**Windows (manual copy):**

Copy the entire `cbers_explorer/` directory to:

```
%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\cbers_explorer\
```

### Restart QGIS

After deploying, restart QGIS and enable the plugin via **Plugins > Manage and Install Plugins...**.

## Build Commands

All commands run from the plugin root directory:

| Command | Description |
|---------|-------------|
| `make` | Show available targets |
| `make compile` | Compile Qt resources (`.qrc` to `.py`) |
| `make transcompile` | Compile translations (`.ts` to `.qm`) |
| `make deploy` | Deploy plugin to QGIS plugins directory |
| `make zip` | Create distributable `.zip` bundle |
| `make clean` | Remove `.pyc`, `__pycache__`, and `.qm` files |
| `make derase` | Remove deployed plugin entirely |
| `make test` | Run test suite |
| `make pylint` | Run linting checks |

## Plugin Structure

```
cbers_explorer/
├── __init__.py              # classFactory entry point
├── plugin.py                # Plugin lifecycle and dependency wiring
├── resources.py             # Compiled Qt resources
├── style.py                 # Raster layer styling
├── metadata.txt             # Plugin metadata (v2.0.0)
├── icon.png                 # Toolbar icon
│
├── domain/                  # Pure models (no QGIS imports)
│   ├── models.py            # StacAsset, StacItem, StacCollection, SearchParams, SearchResult
│   └── stac_parser.py       # JSON-to-model parse functions
│
├── infra/                   # Infrastructure adapters
│   ├── config/
│   │   ├── settings.py      # Constants and defaults
│   │   └── repository.py    # QgsSettings wrapper
│   ├── http/
│   │   ├── client.py        # QgsNetworkAccessManager async wrapper
│   │   └── errors.py        # HTTP error normalization
│   └── tasks/
│       ├── base_task.py     # QgsTask base class with signals
│       ├── search_task.py   # STAC search in worker thread
│       └── download_task.py # File download with progress
│
├── app/                     # Application layer
│   ├── state/
│   │   └── store.py         # AppState (reactive pyqtSignals)
│   └── controllers/
│       ├── search_controller.py   # Search orchestration
│       ├── download_controller.py # Download queue management
│       └── layer_controller.py    # COG/VRT/file layer loading
│
├── ui/                      # User interface
│   ├── dock.py              # DockWidget with ActivityBar + QStackedWidget
│   ├── theme.py             # Centralized stylesheets
│   └── widgets/
│       ├── activity_bar.py         # SVG icon navigation bar
│       ├── quick_search_panel.py   # Canvas bbox + fixed collection
│       ├── advanced_search_panel.py # Flexible ROI + dynamic collections
│       ├── results_panel.py        # QTableView + pagination
│       ├── item_details_panel.py   # Metadata + thumbnail + assets
│       └── downloads_panel.py      # Download queue with progress bars
│
├── assets/icons/            # SVG navigation icons (Feather style)
├── i18n/                    # Translations (en, pt-BR)
├── test/                    # Test suite
└── help/                    # Sphinx documentation
```

## Troubleshooting

**Plugin does not appear after install:**
Restart QGIS. Go to **Plugins > Manage and Install Plugins...** and make sure CBERS Explorer is checked.

**"No module named" errors:**
Verify the plugin directory structure is correct. All subdirectories (`domain/`, `infra/`, `app/`, `ui/`, `assets/`) must include their `__init__.py` files.

**Translations not working:**
Run `make transcompile` to regenerate `.qm` files from `.ts` sources. The compiled files must be in the `i18n/` directory.

**COG layers load slowly or fail:**
COG streaming depends on network access to `data.inpe.br`. Check your internet connection and proxy settings in **Settings > Options > Network**.
