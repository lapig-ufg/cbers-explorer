from qgis.PyQt.QtCore import pyqtSignal, Qt
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QLabel, QSizePolicy,
)

from .theme import DOCK_STYLESHEET, HEADER_STYLESHEET
from .widgets.activity_bar import ActivityBar
from ..infra.config.settings import PLUGIN_VERSION


class CbersExplorerDock(QDockWidget):
    closed = pyqtSignal()

    PAGE_QUICK_SEARCH = 0
    PAGE_ADVANCED_SEARCH = 1
    PAGE_RESULTS = 2
    PAGE_DETAILS = 3
    PAGE_DOWNLOADS = 4
    PAGE_SETTINGS = 5

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self._state = state
        self.setWindowTitle(f"CBERS Explorer v{PLUGIN_VERSION}")
        self.setStyleSheet(DOCK_STYLESHEET)
        self.setMinimumWidth(380)

        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.setFont(font)

        self._build_ui()
        self._setup_nav_buttons()

    @property
    def activity_bar(self):
        return self._activity_bar

    def _build_ui(self):
        container = QWidget()
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Activity bar (left)
        self._activity_bar = ActivityBar()
        main_layout.addWidget(self._activity_bar)

        # Content area (right)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Stacked widget for pages
        self._stack = QStackedWidget()
        content_layout.addWidget(self._stack)

        # Placeholders for 6 pages
        for i in range(6):
            placeholder = QWidget()
            layout = QVBoxLayout(placeholder)
            label = QLabel(self.tr("Pagina {index}").format(index=i))
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            self._stack.addWidget(placeholder)

        main_layout.addWidget(content_widget)

        self.setWidget(container)

        # Connect activity bar
        self._activity_bar.page_changed.connect(self._on_page_changed)

    def _setup_nav_buttons(self):
        # Top group: search modes
        self._activity_bar.add_button("nav_quick_search", self.tr("Busca Rapida"), self.PAGE_QUICK_SEARCH)
        self._activity_bar.add_button("nav_advanced_search", self.tr("Busca Avancada"), self.PAGE_ADVANCED_SEARCH)
        self._activity_bar.add_button("nav_results", self.tr("Resultados"), self.PAGE_RESULTS)

        # Stretch separator
        self._activity_bar.add_stretch()

        # Bottom group: details and downloads
        self._activity_bar.add_button("nav_details", self.tr("Detalhes"), self.PAGE_DETAILS)
        self._activity_bar.add_button("nav_downloads", self.tr("Downloads"), self.PAGE_DOWNLOADS)
        self._activity_bar.add_button("nav_settings", self.tr("Configuracoes"), self.PAGE_SETTINGS)

    def set_page_widget(self, page_index, widget):
        old = self._stack.widget(page_index)
        self._stack.removeWidget(old)
        old.deleteLater()
        self._stack.insertWidget(page_index, widget)

    def navigate_to(self, page_index):
        self._activity_bar.select_page(page_index)
        self._stack.setCurrentIndex(page_index)

    def _on_page_changed(self, page_index):
        self._stack.setCurrentIndex(page_index)

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
