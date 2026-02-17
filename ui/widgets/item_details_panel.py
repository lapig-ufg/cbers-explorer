from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QApplication, QScrollArea,
)
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import QgsNetworkAccessManager
from qgis.utils import iface

from ..theme import SEARCH_BUTTON_STYLESHEET, PRESET_BUTTON_STYLESHEET


class ItemDetailsPanel(QWidget):

    def __init__(self, state, layer_controller, download_controller, http_client, parent=None):
        super().__init__(parent)
        self._state = state
        self._layer_controller = layer_controller
        self._download_controller = download_controller
        self._http = http_client
        self._current_item = None
        self._thumbnail_reply = None

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Title
        self._title_label = QLabel(self.tr("Detalhes"))
        self._title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(self._title_label)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(scroll.NoFrame)

        scroll_content = QWidget()
        self._content_layout = QVBoxLayout(scroll_content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(8)

        # Thumbnail
        self._thumbnail_label = QLabel()
        self._thumbnail_label.setAlignment(Qt.AlignCenter)
        self._thumbnail_label.setFixedHeight(180)
        self._thumbnail_label.setStyleSheet(
            "background-color: #f8f9fa; border-radius: 4px;"
        )
        self._thumbnail_label.setText(self.tr("Sem thumbnail"))
        self._content_layout.addWidget(self._thumbnail_label)

        # Properties form
        self._props_form = QFormLayout()
        self._props_form.setSpacing(4)

        self._id_label = QLabel("-")
        self._id_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._props_form.addRow(self.tr("ID:"), self._id_label)

        self._collection_label = QLabel("-")
        self._props_form.addRow(self.tr("Colecao:"), self._collection_label)

        self._datetime_label = QLabel("-")
        self._props_form.addRow(self.tr("Data:"), self._datetime_label)

        self._cloud_label = QLabel("-")
        self._props_form.addRow(self.tr("Cloud Cover:"), self._cloud_label)

        self._bbox_label = QLabel("-")
        self._bbox_label.setWordWrap(True)
        self._props_form.addRow(self.tr("Bbox:"), self._bbox_label)

        self._content_layout.addLayout(self._props_form)

        # Assets table
        assets_label = QLabel(self.tr("Assets"))
        assets_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 8px;")
        self._content_layout.addWidget(assets_label)

        self._assets_table = QTableWidget()
        self._assets_table.setColumnCount(4)
        self._assets_table.setHorizontalHeaderLabels([
            self.tr("Key"), self.tr("Tipo"), self.tr("COG"), self.tr("Acao"),
        ])
        self._assets_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._assets_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._assets_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._assets_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._assets_table.verticalHeader().setVisible(False)
        self._assets_table.setMaximumHeight(200)
        self._content_layout.addWidget(self._assets_table)

        self._content_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Action buttons
        btn_layout = QHBoxLayout()

        self._add_map_btn = QPushButton(self.tr("Adicionar ao Mapa"))
        self._add_map_btn.setStyleSheet(SEARCH_BUTTON_STYLESHEET)
        self._add_map_btn.clicked.connect(self._on_add_to_map)
        self._add_map_btn.setEnabled(False)
        btn_layout.addWidget(self._add_map_btn)

        self._download_btn = QPushButton(self.tr("Download"))
        self._download_btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
        self._download_btn.clicked.connect(self._on_download)
        self._download_btn.setEnabled(False)
        btn_layout.addWidget(self._download_btn)

        self._copy_btn = QPushButton(self.tr("Copiar URL"))
        self._copy_btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
        self._copy_btn.clicked.connect(self._on_copy_url)
        self._copy_btn.setEnabled(False)
        btn_layout.addWidget(self._copy_btn)

        layout.addLayout(btn_layout)

    def _connect_signals(self):
        self._state.selected_item_changed.connect(self._on_selected_item_changed)

    def _on_selected_item_changed(self, item):
        self._current_item = item
        if item is None:
            self._clear()
            return
        self._populate_properties(item)
        self._populate_assets(item)
        self._load_thumbnail(item)
        self._add_map_btn.setEnabled(True)
        self._download_btn.setEnabled(True)
        self._copy_btn.setEnabled(True)

    def _clear(self):
        self._title_label.setText(self.tr("Detalhes"))
        self._id_label.setText("-")
        self._collection_label.setText("-")
        self._datetime_label.setText("-")
        self._cloud_label.setText("-")
        self._bbox_label.setText("-")
        self._thumbnail_label.setPixmap(QPixmap())
        self._thumbnail_label.setText(self.tr("Sem thumbnail"))
        self._assets_table.setRowCount(0)
        self._add_map_btn.setEnabled(False)
        self._download_btn.setEnabled(False)
        self._copy_btn.setEnabled(False)
        self._current_item = None

    def _populate_properties(self, item):
        self._title_label.setText(
            self.tr("Detalhes: {item_id}").format(item_id=item.id)
        )
        self._id_label.setText(item.id)
        self._collection_label.setText(item.collection)
        self._datetime_label.setText(item.datetime[:10] if item.datetime else "-")
        cc = item.cloud_cover
        self._cloud_label.setText(f"{cc:.1f}%" if cc is not None else "N/A")
        if item.bbox:
            self._bbox_label.setText(
                f"[{item.bbox[0]:.4f}, {item.bbox[1]:.4f}, "
                f"{item.bbox[2]:.4f}, {item.bbox[3]:.4f}]"
            )
        else:
            self._bbox_label.setText("-")

    def _populate_assets(self, item):
        self._assets_table.setRowCount(0)
        for key, asset in item.assets.items():
            row = self._assets_table.rowCount()
            self._assets_table.insertRow(row)
            self._assets_table.setItem(row, 0, QTableWidgetItem(asset.title or key))
            self._assets_table.setItem(row, 1, QTableWidgetItem(
                asset.media_type.split(";")[0] if asset.media_type else ""
            ))
            self._assets_table.setItem(row, 2, QTableWidgetItem(
                self.tr("Sim") if asset.is_cog else self.tr("Nao")
            ))

            add_btn = QPushButton(self.tr("+ Mapa"))
            add_btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
            add_btn.clicked.connect(
                lambda _, k=key: self._on_add_asset_to_map(k)
            )
            if not asset.is_cog:
                add_btn.setEnabled(False)
            self._assets_table.setCellWidget(row, 3, add_btn)

    def _load_thumbnail(self, item):
        url = item.thumbnail_url
        if not url:
            self._thumbnail_label.setPixmap(QPixmap())
            self._thumbnail_label.setText(self.tr("Sem thumbnail"))
            return

        self._thumbnail_label.setText(self.tr("Carregando..."))
        request = QNetworkRequest(QUrl(url))
        manager = QgsNetworkAccessManager.instance()
        self._thumbnail_reply = manager.get(request)
        self._thumbnail_reply.finished.connect(self._on_thumbnail_loaded)

    def _on_thumbnail_loaded(self):
        reply = self._thumbnail_reply
        self._thumbnail_reply = None
        if not reply:
            return

        if reply.error() != reply.NoError:
            self._thumbnail_label.setText(self.tr("Erro ao carregar thumbnail"))
            reply.deleteLater()
            return

        data = bytes(reply.readAll())
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self._thumbnail_label.width(),
                self._thumbnail_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self._thumbnail_label.setPixmap(scaled)
        else:
            self._thumbnail_label.setText(self.tr("Thumbnail invalido"))

        reply.deleteLater()

    def _on_add_to_map(self):
        if not self._current_item:
            return
        asset = self._current_item.preferred_asset()
        if asset:
            self._layer_controller.add_cog_to_map(self._current_item.id, asset.href)
        else:
            iface.messageBar().pushWarning(
                "CBERS Explorer",
                self.tr("Nenhum asset COG disponivel."),
            )

    def _on_add_asset_to_map(self, asset_key):
        if not self._current_item:
            return
        asset = self._current_item.assets.get(asset_key)
        if asset and asset.is_cog:
            self._layer_controller.add_cog_to_map(
                f"{self._current_item.id}_{asset_key}", asset.href
            )

    def _on_download(self):
        if not self._current_item:
            return
        asset = self._current_item.preferred_asset()
        if asset:
            self._download_controller.download_asset(self._current_item, asset)
            iface.messageBar().pushInfo(
                "CBERS Explorer",
                self.tr("Download iniciado: {item_id}").format(
                    item_id=self._current_item.id
                ),
            )
        else:
            iface.messageBar().pushWarning(
                "CBERS Explorer",
                self.tr("Nenhum asset disponivel para download."),
            )

    def _on_copy_url(self):
        if not self._current_item:
            return
        asset = self._current_item.preferred_asset()
        if asset:
            QApplication.clipboard().setText(asset.href)
            iface.messageBar().pushInfo(
                "CBERS Explorer", self.tr("URL copiada!")
            )
