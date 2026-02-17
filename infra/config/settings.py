PLUGIN_NAME = "CbersExplorer"
PLUGIN_VERSION = "2.0.0"
STAC_BASE_URL = "https://data.inpe.br/bdc/stac/v1"
SETTINGS_NAMESPACE = "CbersExplorer"
DEFAULT_COLLECTION = "CB4A-WPM-PCA-FUSED-1"

DEFAULTS = {
    "stac_base_url": STAC_BASE_URL,
    "last_collection": "",
    "download_dir": "",
    "items_per_page": 10,
    "last_start_date": "",
    "last_end_date": "",
    "auto_add_on_download": True,
    "preferred_asset": "",
}
