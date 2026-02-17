import os

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QTimer
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .resources import *  # noqa: F401,F403
from .infra.config.repository import ConfigRepository
from .infra.http.client import HttpClient
from .app.state.store import AppState
from .app.controllers.search_controller import SearchController
from .app.controllers.download_controller import DownloadController
from .app.controllers.layer_controller import LayerController
from .ui.dock import CbersExplorerDock
from .ui.widgets.quick_search_panel import QuickSearchPanel
from .ui.widgets.advanced_search_panel import AdvancedSearchPanel
from .ui.widgets.results_panel import ResultsPanel
from .ui.widgets.item_details_panel import ItemDetailsPanel
from .ui.widgets.downloads_panel import DownloadsPanel


class CbersExplorerPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dock = None
        self.plugin_is_active = False
        self.actions = []
        self.menu = self.tr("&CBERS Explorer")

        # Locale / i18n
        locale = QSettings().value("locale/userLocale", "en")[0:2]
        locale_path = os.path.join(
            self.plugin_dir, "i18n", f"CbersExplorer_{locale}.qm"
        )
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Toolbar
        self.toolbar = self.iface.addToolBar("CbersExplorer")
        self.toolbar.setObjectName("CbersExplorer")

        # DI: shared objects
        self._config_repo = ConfigRepository()
        self._state = AppState()
        self._http_client = HttpClient()

        # Controllers
        self._search_controller = SearchController(
            self._state, self._http_client, self._config_repo
        )
        self._download_controller = DownloadController(
            self._state, self._config_repo
        )
        self._layer_controller = LayerController(iface)

        # Widget refs for cleanup
        self._panels = []

    def tr(self, message):
        return QCoreApplication.translate("CbersExplorerPlugin", message)

    def initGui(self):
        icon_path = ":/plugins/cbers_explorer/icon.png"
        icon = QIcon(icon_path)
        action = QAction(icon, self.tr("CBERS Explorer"), self.iface.mainWindow())
        action.triggered.connect(self.run)
        action.setEnabled(True)

        self.toolbar.addAction(action)
        self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)

        # Pre-load collections
        QTimer.singleShot(500, self._search_controller.load_collections)

    def run(self):
        if not self.plugin_is_active:
            self.plugin_is_active = True

            if self.dock is None:
                self.dock = CbersExplorerDock(
                    state=self._state,
                    parent=self.iface.mainWindow(),
                )
                self.dock.closed.connect(self._on_dock_closed)
                self._wire_controllers()

            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)
            self.dock.show()

    def _on_dock_closed(self):
        self.plugin_is_active = False

    def _wire_controllers(self):
        quick_search = QuickSearchPanel(
            self._state, self._search_controller, self._config_repo
        )
        advanced_search = AdvancedSearchPanel(
            self._state, self._search_controller, self._config_repo
        )
        results_panel = ResultsPanel(
            self._state, self._search_controller,
            self._layer_controller, self._config_repo,
        )
        details_panel = ItemDetailsPanel(
            self._state, self._layer_controller,
            self._download_controller, self._http_client,
        )
        downloads_panel = DownloadsPanel(
            self._state, self._download_controller
        )

        self._panels = [
            quick_search, advanced_search, results_panel,
            details_panel, downloads_panel,
        ]

        self.dock.set_page_widget(CbersExplorerDock.PAGE_QUICK_SEARCH, quick_search)
        self.dock.set_page_widget(CbersExplorerDock.PAGE_ADVANCED_SEARCH, advanced_search)
        self.dock.set_page_widget(CbersExplorerDock.PAGE_RESULTS, results_panel)
        self.dock.set_page_widget(CbersExplorerDock.PAGE_DETAILS, details_panel)
        self.dock.set_page_widget(CbersExplorerDock.PAGE_DOWNLOADS, downloads_panel)

        # Auto-navigation: search completed -> Results
        self._state.search_results_changed.connect(
            lambda _: self.dock.navigate_to(CbersExplorerDock.PAGE_RESULTS)
        )

        # Auto-navigation: item selected -> Details
        self._state.selected_item_changed.connect(
            lambda item: self.dock.navigate_to(CbersExplorerDock.PAGE_DETAILS) if item else None
        )

        # Badge: active downloads on Downloads button
        self._state.download_started.connect(lambda _: self._update_downloads_badge())
        self._state.download_completed.connect(self._on_download_completed)
        self._state.download_failed.connect(lambda *_: self._update_downloads_badge())

        # Error feedback via message bar
        self._state.error_occurred.connect(self._on_error)

        # Navigate to Quick Search on open
        self.dock.navigate_to(CbersExplorerDock.PAGE_QUICK_SEARCH)

    def _on_download_completed(self, item_id, file_path):
        self._update_downloads_badge()

        # Check if downloads panel has auto_add enabled
        downloads_panel = self._panels[4] if len(self._panels) > 4 else None
        auto_add = (
            downloads_panel.auto_add_on_download
            if downloads_panel
            else self._config_repo.get("auto_add_on_download")
        )
        if auto_add:
            self._layer_controller.add_downloaded_to_map(file_path, item_id)

    def _update_downloads_badge(self):
        active = len(self._download_controller.active_downloads)
        btn = self.dock.activity_bar.button_at(CbersExplorerDock.PAGE_DOWNLOADS)
        if btn:
            btn.set_badge(active)

    def _on_error(self, operation, message):
        self.iface.messageBar().pushWarning(
            "CBERS Explorer", f"[{operation}] {message}"
        )

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr("&CBERS Explorer"), action)
            self.iface.removeToolBarIcon(action)

        del self.toolbar

        if self.dock:
            self.iface.removeDockWidget(self.dock)
            self.dock.deleteLater()
            self.dock = None
