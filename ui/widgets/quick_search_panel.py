from qgis.PyQt.QtCore import Qt, QDate
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QDateEdit, QFrame,
)
from qgis.core import (
    QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject,
)
from qgis.utils import iface

from ...domain.models import SearchParams
from ...infra.config.settings import DEFAULT_COLLECTION
from ..theme import SEARCH_BUTTON_STYLESHEET, PRESET_BUTTON_STYLESHEET, SECTION_LABEL_STYLESHEET


class QuickSearchPanel(QWidget):

    def __init__(self, state, search_controller, config_repo, parent=None):
        super().__init__(parent)
        self._state = state
        self._controller = search_controller
        self._config = config_repo
        self._current_bbox = None

        self._build_ui()
        self._connect_signals()
        self._update_bbox()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Title
        title = QLabel(self.tr("Busca Rapida"))
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        desc = QLabel(self.tr("Busca por bbox do canvas com colecao fixa"))
        desc.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Bbox section
        bbox_label = QLabel(self.tr("BOUNDING BOX"))
        bbox_label.setStyleSheet(SECTION_LABEL_STYLESHEET)
        layout.addWidget(bbox_label)

        self._bbox_display = QLabel(self.tr("Nao definido"))
        self._bbox_display.setWordWrap(True)
        self._bbox_display.setStyleSheet(
            "background-color: #f8f9fa; padding: 6px; border-radius: 3px; font-size: 11px;"
        )
        layout.addWidget(self._bbox_display)

        self._update_bbox_btn = QPushButton(self.tr("Atualizar Bbox"))
        self._update_bbox_btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
        self._update_bbox_btn.clicked.connect(self._update_bbox)
        layout.addWidget(self._update_bbox_btn)

        # Dates section
        date_label = QLabel(self.tr("PERIODO"))
        date_label.setStyleSheet(SECTION_LABEL_STYLESHEET)
        layout.addWidget(date_label)

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel(self.tr("De:")))
        self._start_date = QDateEdit()
        self._start_date.setCalendarPopup(True)
        self._start_date.setDate(QDate.currentDate().addYears(-1))
        self._start_date.setDisplayFormat("dd/MM/yyyy")
        date_layout.addWidget(self._start_date)

        date_layout.addWidget(QLabel(self.tr("Ate:")))
        self._end_date = QDateEdit()
        self._end_date.setCalendarPopup(True)
        self._end_date.setDate(QDate.currentDate())
        self._end_date.setDisplayFormat("dd/MM/yyyy")
        date_layout.addWidget(self._end_date)
        layout.addLayout(date_layout)

        # Presets
        preset_layout = QHBoxLayout()
        for label, days in [
            (self.tr("7 dias"), 7),
            (self.tr("30 dias"), 30),
            (self.tr("1 ano"), 365),
        ]:
            btn = QPushButton(label)
            btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
            btn.clicked.connect(lambda _, d=days: self._apply_preset(d))
            preset_layout.addWidget(btn)
        layout.addLayout(preset_layout)

        # Collection (fixed)
        col_label = QLabel(self.tr("COLECAO"))
        col_label.setStyleSheet(SECTION_LABEL_STYLESHEET)
        layout.addWidget(col_label)

        col_value = QLabel(DEFAULT_COLLECTION)
        col_value.setStyleSheet(
            "background-color: #eaf2f8; padding: 6px; border-radius: 3px; "
            "font-weight: bold; color: #2980b9;"
        )
        layout.addWidget(col_value)

        layout.addStretch()

        # Search button
        self._search_btn = QPushButton(self.tr("Buscar"))
        self._search_btn.setStyleSheet(SEARCH_BUTTON_STYLESHEET)
        self._search_btn.setMinimumHeight(36)
        self._search_btn.clicked.connect(self._on_search_clicked)
        layout.addWidget(self._search_btn)

    def _connect_signals(self):
        self._state.loading_changed.connect(self._on_loading_changed)

    def _update_bbox(self):
        try:
            canvas = iface.mapCanvas()
            extent = canvas.extent()

            crs_dest = QgsCoordinateReferenceSystem("EPSG:4326")
            crs_src = canvas.mapSettings().destinationCrs()
            transform = QgsCoordinateTransform(crs_src, crs_dest, QgsProject.instance())
            extent_transformed = transform.transformBoundingBox(extent)

            self._current_bbox = [
                round(extent_transformed.xMinimum(), 6),
                round(extent_transformed.yMinimum(), 6),
                round(extent_transformed.xMaximum(), 6),
                round(extent_transformed.yMaximum(), 6),
            ]
            self._bbox_display.setText(
                f"[{self._current_bbox[0]}, {self._current_bbox[1]}, "
                f"{self._current_bbox[2]}, {self._current_bbox[3]}]"
            )
        except Exception:
            self._current_bbox = None
            self._bbox_display.setText(self.tr("Erro ao obter bbox do canvas"))

    def _apply_preset(self, days):
        self._end_date.setDate(QDate.currentDate())
        self._start_date.setDate(QDate.currentDate().addDays(-days))

    def _on_search_clicked(self):
        if not self._current_bbox:
            self._update_bbox()
        if not self._current_bbox:
            return

        params = SearchParams(
            bbox=self._current_bbox,
            datetime_start=self._start_date.date().toString("yyyy-MM-ddT00:00:00Z"),
            datetime_end=self._end_date.date().toString("yyyy-MM-ddT23:59:59Z"),
            collections=[DEFAULT_COLLECTION],
            limit=self._config.get("items_per_page"),
        )
        self._controller.search(params)

    def _on_loading_changed(self, operation, is_loading):
        if operation == "search":
            self._search_btn.setEnabled(not is_loading)
            self._search_btn.setText(
                self.tr("Buscando...") if is_loading else self.tr("Buscar")
            )
