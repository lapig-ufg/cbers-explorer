from qgis.PyQt.QtCore import Qt, QModelIndex, QAbstractTableModel, pyqtSignal, QCoreApplication
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableView, QHeaderView, QApplication,
    QAbstractItemView,
)
from qgis.utils import iface

from ..theme import (
    TABLE_STYLESHEET, PRESET_BUTTON_STYLESHEET,
    TITLE_STYLESHEET, DESC_STYLESHEET,
)
from .item_metadata_dialog import ItemMetadataDialog


class StacItemTableModel(QAbstractTableModel):

    COL_ID = 0
    COL_DATE = 1
    COL_ACTIONS = 2

    COLUMNS = ["ID", "Data", ""]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []

    def set_items(self, items):
        self.beginResetModel()
        self._items = list(items)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def columnCount(self, parent=QModelIndex()):
        return len(self.COLUMNS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._items):
            return None

        item = self._items[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == self.COL_ID:
                return item.id
            elif col == self.COL_DATE:
                dt = item.datetime
                if dt and len(dt) >= 10:
                    return dt[:10]
                return dt or ""

        if role == Qt.UserRole:
            return item

        if role == Qt.ToolTipRole and col == self.COL_ID:
            return item.id

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section < len(self.COLUMNS):
                return self.COLUMNS[section]
        return None

    def item_at(self, row):
        if 0 <= row < len(self._items):
            return self._items[row]
        return None


class ResultsPanel(QWidget):
    item_selected = pyqtSignal(object)
    add_to_map_requested = pyqtSignal(object)

    def __init__(self, state, search_controller, layer_controller, config_repo, parent=None):
        super().__init__(parent)
        self._state = state
        self._search_controller = search_controller
        self._layer_controller = layer_controller
        self._config = config_repo

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Header
        header_layout = QHBoxLayout()
        self._title_label = QLabel(self.tr("Resultados"))
        self._title_label.setStyleSheet(TITLE_STYLESHEET)
        header_layout.addWidget(self._title_label)
        header_layout.addStretch()
        self._count_label = QLabel("")
        self._count_label.setStyleSheet(DESC_STYLESHEET)
        header_layout.addWidget(self._count_label)
        layout.addLayout(header_layout)

        # Table
        self._model = StacItemTableModel(self)
        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setStyleSheet(TABLE_STYLESHEET)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(
            StacItemTableModel.COL_ID, QHeaderView.Stretch
        )
        self._table.horizontalHeader().setSectionResizeMode(
            StacItemTableModel.COL_DATE, QHeaderView.ResizeToContents
        )
        self._table.horizontalHeader().setSectionResizeMode(
            StacItemTableModel.COL_ACTIONS, QHeaderView.ResizeToContents
        )
        self._table.doubleClicked.connect(self._on_row_double_clicked)
        self._table.clicked.connect(self._on_row_clicked)
        layout.addWidget(self._table)

        # Action buttons row
        action_layout = QHBoxLayout()
        self._add_map_btn = QPushButton(self.tr("Adicionar ao Mapa"))
        self._add_map_btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
        self._add_map_btn.clicked.connect(self._on_add_to_map)
        self._add_map_btn.setEnabled(False)
        action_layout.addWidget(self._add_map_btn)

        self._copy_url_btn = QPushButton(self.tr("Copiar URL"))
        self._copy_url_btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
        self._copy_url_btn.clicked.connect(self._on_copy_url)
        self._copy_url_btn.setEnabled(False)
        action_layout.addWidget(self._copy_url_btn)

        action_layout.addStretch()
        layout.addLayout(action_layout)

        # Pagination
        pag_layout = QHBoxLayout()
        self._prev_btn = QPushButton("<")
        self._prev_btn.setFixedWidth(30)
        self._prev_btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
        self._prev_btn.clicked.connect(self._on_prev_page)
        self._prev_btn.setEnabled(False)
        pag_layout.addWidget(self._prev_btn)

        self._page_label = QLabel("")
        self._page_label.setAlignment(Qt.AlignCenter)
        pag_layout.addWidget(self._page_label)

        self._next_btn = QPushButton(">")
        self._next_btn.setFixedWidth(30)
        self._next_btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
        self._next_btn.clicked.connect(self._on_next_page)
        self._next_btn.setEnabled(False)
        pag_layout.addWidget(self._next_btn)

        pag_layout.addStretch()

        self._total_label = QLabel("")
        self._total_label.setStyleSheet(DESC_STYLESHEET)
        pag_layout.addWidget(self._total_label)
        layout.addLayout(pag_layout)

    def _connect_signals(self):
        self._state.search_results_changed.connect(self._on_state_results_changed)
        self._state.loading_changed.connect(self._on_loading_changed)

    def _on_state_results_changed(self, result):
        if not result:
            return
        self._model.set_items(result.items)
        self._populate_action_buttons(result.items)
        self._update_pagination(result)
        self._add_map_btn.setEnabled(False)
        self._copy_url_btn.setEnabled(False)

    def _populate_action_buttons(self, items):
        preferred = self._config.get("preferred_asset")
        for row, item in enumerate(items):
            actions_idx = self._model.index(row, StacItemTableModel.COL_ACTIONS)

            container = QWidget()
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(2, 0, 2, 0)
            h_layout.setSpacing(4)

            # + Mapa button
            asset = item.preferred_asset(preferred)
            map_btn = QPushButton(self.tr("+ Mapa"))
            map_btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
            if asset:
                map_btn.clicked.connect(
                    lambda _, r=row: self._on_add_row_to_map(r)
                )
            else:
                map_btn.setEnabled(False)
                map_btn.setToolTip(
                    self.tr("Nenhum asset COG disponivel para este item.")
                )
            h_layout.addWidget(map_btn)

            # Info button
            info_btn = QPushButton(self.tr("Info"))
            info_btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
            info_btn.setToolTip(
                self.tr("Ver metadados completos do item")
            )
            info_btn.clicked.connect(
                lambda _, r=row: self._on_show_item_metadata(r)
            )
            h_layout.addWidget(info_btn)

            self._table.setIndexWidget(actions_idx, container)

    def _on_show_item_metadata(self, row):
        item = self._model.item_at(row)
        if item:
            dlg = ItemMetadataDialog(item, parent=self)
            dlg.exec_()

    def _on_add_row_to_map(self, row):
        item = self._model.item_at(row)
        if not item:
            return
        preferred = self._config.get("preferred_asset")
        asset = item.preferred_asset(preferred)
        if asset:
            self._layer_controller.add_cog_to_map(item.id, asset.href)

    def _update_pagination(self, result):
        params = self._state.current_search_params
        current_page = params.page if params else 1
        limit = params.limit if params else 10

        total_pages = max(1, (result.matched + limit - 1) // limit) if result.matched > 0 else 1
        self._page_label.setText(
            self.tr("Pag {current} / {total}").format(current=current_page, total=total_pages)
        )
        self._total_label.setText(
            self.tr("{count} resultados").format(count=result.matched)
        )
        self._count_label.setText(
            self.tr("({count} exibidos)").format(count=result.returned)
        )

        self._prev_btn.setEnabled(result.prev_page is not None or current_page > 1)
        self._next_btn.setEnabled(result.next_page is not None)

    def _on_row_clicked(self, index):
        item = self._model.item_at(index.row())
        if item:
            self._add_map_btn.setEnabled(True)
            self._copy_url_btn.setEnabled(True)

    def _on_row_double_clicked(self, index):
        item = self._model.item_at(index.row())
        if item:
            self._state.selected_item = item

    def _on_add_to_map(self):
        indexes = self._table.selectionModel().selectedRows()
        if not indexes:
            return
        item = self._model.item_at(indexes[0].row())
        if item:
            preferred = self._config.get("preferred_asset")
            asset = item.preferred_asset(preferred)
            if asset:
                self._layer_controller.add_cog_to_map(item.id, asset.href)
            else:
                iface.messageBar().pushWarning(
                    "CBERS Explorer",
                    self.tr("Nenhum asset COG disponivel para este item."),
                )

    def _on_copy_url(self):
        indexes = self._table.selectionModel().selectedRows()
        if not indexes:
            return
        item = self._model.item_at(indexes[0].row())
        if item:
            preferred = self._config.get("preferred_asset")
            asset = item.preferred_asset(preferred)
            if asset:
                QApplication.clipboard().setText(asset.href)
                iface.messageBar().pushInfo(
                    "CBERS Explorer", self.tr("URL copiada!")
                )

    def _on_prev_page(self):
        result = self._state.search_result
        params = self._state.current_search_params
        if result and result.prev_page:
            self._search_controller.prev_page()
        elif params and params.page > 1:
            params.page -= 1
            self._search_controller.search(params)

    def _on_next_page(self):
        self._search_controller.next_page()

    def _on_loading_changed(self, operation, is_loading):
        if operation == "search":
            self._table.setEnabled(not is_loading)
            if is_loading:
                self._title_label.setText(self.tr("Resultados (buscando...)"))
            else:
                self._title_label.setText(self.tr("Resultados"))
