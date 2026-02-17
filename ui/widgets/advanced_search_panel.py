import json

from qgis.PyQt.QtCore import Qt, QDate
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QDateEdit, QComboBox, QSpinBox,
    QFrame, QGroupBox,
)
from qgis.core import (
    QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject,
)
from qgis.utils import iface

from ...domain.models import SearchParams
from ..theme import SEARCH_BUTTON_STYLESHEET, PRESET_BUTTON_STYLESHEET, SECTION_LABEL_STYLESHEET


class AdvancedSearchPanel(QWidget):

    def __init__(self, state, search_controller, config_repo, parent=None):
        super().__init__(parent)
        self._state = state
        self._controller = search_controller
        self._config = config_repo
        self._current_bbox = None
        self._drawn_geometry = None

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Title
        title = QLabel(self.tr("Busca Avancada"))
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        desc = QLabel(self.tr("ROI flexivel, colecao dinamica e filtros"))
        desc.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # ROI section
        roi_label = QLabel(self.tr("REGIAO DE INTERESSE"))
        roi_label.setStyleSheet(SECTION_LABEL_STYLESHEET)
        layout.addWidget(roi_label)

        roi_layout = QHBoxLayout()
        self._roi_combo = QComboBox()
        self._roi_combo.addItem(self.tr("Extent do canvas"), "canvas")
        self._roi_combo.addItem(self.tr("Extent de camada"), "layer")
        self._roi_combo.addItem(self.tr("Feicoes selecionadas"), "features")
        roi_layout.addWidget(self._roi_combo)

        self._capture_btn = QPushButton(self.tr("Capturar"))
        self._capture_btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
        self._capture_btn.clicked.connect(self._capture_roi)
        roi_layout.addWidget(self._capture_btn)
        layout.addLayout(roi_layout)

        self._roi_display = QLabel(self.tr("Nao definido"))
        self._roi_display.setWordWrap(True)
        self._roi_display.setStyleSheet(
            "background-color: #f8f9fa; padding: 6px; border-radius: 3px; font-size: 11px;"
        )
        layout.addWidget(self._roi_display)

        # Layer selector (for "layer" mode)
        self._layer_combo = QComboBox()
        self._layer_combo.setVisible(False)
        layout.addWidget(self._layer_combo)

        self._roi_combo.currentIndexChanged.connect(self._on_roi_mode_changed)

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

        # Collection section
        col_label = QLabel(self.tr("COLECAO"))
        col_label.setStyleSheet(SECTION_LABEL_STYLESHEET)
        layout.addWidget(col_label)

        self._collection_combo = QComboBox()
        self._collection_combo.setMinimumHeight(28)
        layout.addWidget(self._collection_combo)

        # Limit
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel(self.tr("Itens por pagina:")))
        self._limit_spin = QSpinBox()
        self._limit_spin.setRange(1, 100)
        self._limit_spin.setValue(self._config.get("items_per_page"))
        limit_layout.addWidget(self._limit_spin)
        limit_layout.addStretch()
        layout.addLayout(limit_layout)

        layout.addStretch()

        # Search button
        self._search_btn = QPushButton(self.tr("Buscar"))
        self._search_btn.setStyleSheet(SEARCH_BUTTON_STYLESHEET)
        self._search_btn.setMinimumHeight(36)
        self._search_btn.clicked.connect(self._on_search_clicked)
        layout.addWidget(self._search_btn)

    def _connect_signals(self):
        self._state.collections_changed.connect(self._on_collections_loaded)
        self._state.loading_changed.connect(self._on_loading_changed)

    def _on_collections_loaded(self, collections):
        self._collection_combo.clear()
        for c in collections:
            display = c.title if c.title else c.id
            self._collection_combo.addItem(display, c.id)

        last = self._config.get("last_collection")
        if last:
            idx = self._collection_combo.findData(last)
            if idx >= 0:
                self._collection_combo.setCurrentIndex(idx)

    def _on_roi_mode_changed(self, index):
        mode = self._roi_combo.currentData()
        self._layer_combo.setVisible(mode == "layer")
        if mode == "layer":
            self._populate_layers()

    def _populate_layers(self):
        self._layer_combo.clear()
        for layer_id, layer in QgsProject.instance().mapLayers().items():
            self._layer_combo.addItem(layer.name(), layer_id)

    def _capture_roi(self):
        mode = self._roi_combo.currentData()
        if mode == "canvas":
            self._current_bbox = self._get_canvas_bbox()
            self._drawn_geometry = None
            if self._current_bbox:
                self._roi_display.setText(
                    f"Bbox: [{self._current_bbox[0]}, {self._current_bbox[1]}, "
                    f"{self._current_bbox[2]}, {self._current_bbox[3]}]"
                )
        elif mode == "layer":
            self._current_bbox = self._get_layer_bbox()
            self._drawn_geometry = None
            if self._current_bbox:
                self._roi_display.setText(
                    f"Bbox: [{self._current_bbox[0]}, {self._current_bbox[1]}, "
                    f"{self._current_bbox[2]}, {self._current_bbox[3]}]"
                )
        elif mode == "features":
            geojson = self._get_selected_features_geojson()
            if geojson:
                self._drawn_geometry = geojson
                self._current_bbox = None
                self._roi_display.setText(
                    self.tr("Geometria das feicoes selecionadas")
                )
            else:
                self._roi_display.setText(self.tr("Nenhuma feicao selecionada"))

    def _get_canvas_bbox(self):
        try:
            canvas = iface.mapCanvas()
            extent = canvas.extent()
            crs_dest = QgsCoordinateReferenceSystem("EPSG:4326")
            crs_src = canvas.mapSettings().destinationCrs()
            transform = QgsCoordinateTransform(crs_src, crs_dest, QgsProject.instance())
            ext = transform.transformBoundingBox(extent)
            return [
                round(ext.xMinimum(), 6),
                round(ext.yMinimum(), 6),
                round(ext.xMaximum(), 6),
                round(ext.yMaximum(), 6),
            ]
        except Exception:
            return None

    def _get_layer_bbox(self):
        try:
            layer_id = self._layer_combo.currentData()
            if not layer_id:
                return None
            layer = QgsProject.instance().mapLayer(layer_id)
            if not layer:
                return None
            extent = layer.extent()
            crs_dest = QgsCoordinateReferenceSystem("EPSG:4326")
            crs_src = layer.crs()
            transform = QgsCoordinateTransform(crs_src, crs_dest, QgsProject.instance())
            ext = transform.transformBoundingBox(extent)
            return [
                round(ext.xMinimum(), 6),
                round(ext.yMinimum(), 6),
                round(ext.xMaximum(), 6),
                round(ext.yMaximum(), 6),
            ]
        except Exception:
            return None

    def _get_selected_features_geojson(self):
        try:
            layer = iface.activeLayer()
            if not layer or not hasattr(layer, "selectedFeatures"):
                return None
            features = layer.selectedFeatures()
            if not features:
                return None

            crs_dest = QgsCoordinateReferenceSystem("EPSG:4326")
            crs_src = layer.crs()
            transform = QgsCoordinateTransform(crs_src, crs_dest, QgsProject.instance())

            # Use the first selected feature's geometry
            geom = features[0].geometry()
            geom.transform(transform)
            return json.loads(geom.asJson())
        except Exception:
            return None

    def _apply_preset(self, days):
        self._end_date.setDate(QDate.currentDate())
        self._start_date.setDate(QDate.currentDate().addDays(-days))

    def _on_search_clicked(self):
        collection_id = self._collection_combo.currentData()
        if not collection_id:
            return

        bbox = self._current_bbox
        intersects = self._drawn_geometry

        if not bbox and not intersects:
            bbox = self._get_canvas_bbox()

        self._config.set("last_collection", collection_id)

        params = SearchParams(
            bbox=bbox,
            intersects=intersects,
            datetime_start=self._start_date.date().toString("yyyy-MM-ddT00:00:00Z"),
            datetime_end=self._end_date.date().toString("yyyy-MM-ddT23:59:59Z"),
            collections=[collection_id],
            limit=self._limit_spin.value(),
        )
        self._controller.search(params)

    def _on_loading_changed(self, operation, is_loading):
        if operation == "search":
            self._search_btn.setEnabled(not is_loading)
            self._search_btn.setText(
                self.tr("Buscando...") if is_loading else self.tr("Buscar")
            )
        elif operation == "collections":
            self._collection_combo.setEnabled(not is_loading)
