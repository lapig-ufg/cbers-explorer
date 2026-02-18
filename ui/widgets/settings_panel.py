from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSpinBox, QCheckBox,
    QFileDialog, QMessageBox,
)

from ..theme import (
    TITLE_STYLESHEET, DESC_STYLESHEET,
    SECTION_LABEL_STYLESHEET, SEARCH_BUTTON_STYLESHEET,
    PRESET_BUTTON_STYLESHEET,
)
from ...infra.config.settings import DEFAULTS


class SettingsPanel(QWidget):

    _SETTING_KEYS = [
        "download_dir", "stac_base_url", "items_per_page",
        "preferred_asset", "auto_add_on_download",
    ]

    def __init__(self, config_repo, parent=None):
        super().__init__(parent)
        self._config_repo = config_repo
        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header
        title = QLabel(self.tr("Configuracoes"))
        title.setStyleSheet(TITLE_STYLESHEET)
        layout.addWidget(title)

        desc = QLabel(self.tr("Configuracao do plugin"))
        desc.setStyleSheet(DESC_STYLESHEET)
        layout.addWidget(desc)

        # Separator
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: palette(mid);")
        layout.addWidget(sep)

        # --- WORKSPACE ---
        ws_label = QLabel(self.tr("WORKSPACE"))
        ws_label.setStyleSheet(SECTION_LABEL_STYLESHEET)
        layout.addWidget(ws_label)

        ws_row = QHBoxLayout()
        self._workspace_edit = QLineEdit()
        self._workspace_edit.setPlaceholderText(
            self.tr("Diretorio de downloads")
        )
        ws_row.addWidget(self._workspace_edit)

        browse_btn = QPushButton(self.tr("Procurar..."))
        browse_btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
        browse_btn.clicked.connect(self._on_browse_workspace)
        ws_row.addWidget(browse_btn)
        layout.addLayout(ws_row)

        # --- STAC API ---
        stac_label = QLabel(self.tr("STAC API"))
        stac_label.setStyleSheet(SECTION_LABEL_STYLESHEET)
        layout.addWidget(stac_label)

        self._stac_url_edit = QLineEdit()
        self._stac_url_edit.setPlaceholderText("https://...")
        layout.addWidget(self._stac_url_edit)

        # --- SEARCH ---
        search_label = QLabel(self.tr("BUSCA"))
        search_label.setStyleSheet(SECTION_LABEL_STYLESHEET)
        layout.addWidget(search_label)

        items_row = QHBoxLayout()
        items_lbl = QLabel(self.tr("Itens por pagina:"))
        items_row.addWidget(items_lbl)
        self._items_per_page_spin = QSpinBox()
        self._items_per_page_spin.setRange(1, 100)
        items_row.addWidget(self._items_per_page_spin)
        items_row.addStretch()
        layout.addLayout(items_row)

        asset_row = QHBoxLayout()
        asset_lbl = QLabel(self.tr("Asset preferido:"))
        asset_row.addWidget(asset_lbl)
        self._preferred_asset_edit = QLineEdit()
        self._preferred_asset_edit.setPlaceholderText(
            self.tr("ex: tci, BAND15")
        )
        asset_row.addWidget(self._preferred_asset_edit)
        layout.addLayout(asset_row)

        # --- DOWNLOADS ---
        dl_label = QLabel(self.tr("DOWNLOADS"))
        dl_label.setStyleSheet(SECTION_LABEL_STYLESHEET)
        layout.addWidget(dl_label)

        self._auto_add_check = QCheckBox(
            self.tr("Adicionar ao mapa ao concluir download")
        )
        layout.addWidget(self._auto_add_check)

        # Stretch
        layout.addStretch()

        # Action buttons
        btn_row = QHBoxLayout()
        self._save_btn = QPushButton(self.tr("Salvar"))
        self._save_btn.setStyleSheet(SEARCH_BUTTON_STYLESHEET)
        self._save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(self._save_btn)

        self._restore_btn = QPushButton(self.tr("Restaurar Padroes"))
        self._restore_btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
        self._restore_btn.clicked.connect(self._on_restore_defaults)
        btn_row.addWidget(self._restore_btn)
        layout.addLayout(btn_row)

    def _load_settings(self):
        self._workspace_edit.setText(
            self._config_repo.get("download_dir") or ""
        )
        self._stac_url_edit.setText(
            self._config_repo.get("stac_base_url") or ""
        )
        self._items_per_page_spin.setValue(
            self._config_repo.get("items_per_page")
        )
        self._preferred_asset_edit.setText(
            self._config_repo.get("preferred_asset") or ""
        )
        self._auto_add_check.setChecked(
            self._config_repo.get("auto_add_on_download")
        )

    def _on_save(self):
        self._config_repo.set(
            "download_dir", self._workspace_edit.text().strip()
        )
        self._config_repo.set(
            "stac_base_url", self._stac_url_edit.text().strip()
        )
        self._config_repo.set(
            "items_per_page", self._items_per_page_spin.value()
        )
        self._config_repo.set(
            "preferred_asset", self._preferred_asset_edit.text().strip()
        )
        self._config_repo.set(
            "auto_add_on_download", self._auto_add_check.isChecked()
        )
        QMessageBox.information(
            self, self.tr("Configuracoes"),
            self.tr("Configuracoes salvas com sucesso."),
        )

    def _on_restore_defaults(self):
        for key in self._SETTING_KEYS:
            self._config_repo.remove(key)
        self._load_settings()

    def _on_browse_workspace(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            self.tr("Selecionar diretorio de workspace"),
            self._workspace_edit.text(),
        )
        if directory:
            self._workspace_edit.setText(directory)
