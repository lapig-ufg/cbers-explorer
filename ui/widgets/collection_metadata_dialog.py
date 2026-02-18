import json

from qgis.PyQt.QtCore import Qt, QCoreApplication
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTreeWidget, QTreeWidgetItem,
    QApplication, QHeaderView, QFrame,
)

from ..theme import (
    TITLE_STYLESHEET, DESC_STYLESHEET, PRESET_BUTTON_STYLESHEET,
    SEARCH_BUTTON_STYLESHEET, TREE_STYLESHEET, INFO_BOX_STYLESHEET,
    SECTION_LABEL_STYLESHEET,
)


class CollectionMetadataDialog(QDialog):

    # Keys shown first, in this order, at the top of the tree
    _TOP_KEYS = [
        "id", "type", "title", "description", "license",
        "keywords", "extent", "providers", "summaries",
        "item_assets", "links",
    ]

    def __init__(self, collection, parent=None):
        super().__init__(parent)
        self._collection = collection
        self._raw = collection.raw_data or {}

        self.setWindowTitle(
            self.tr("Metadados da Colecao: {id}").format(id=collection.id)
        )
        self.setMinimumSize(560, 480)
        self.resize(640, 580)

        self._build_ui()

    def tr(self, message):
        return QCoreApplication.translate("CollectionMetadataDialog", message)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Header
        title = QLabel(self._collection.title or self._collection.id)
        title.setStyleSheet(TITLE_STYLESHEET)
        title.setWordWrap(True)
        layout.addWidget(title)

        if self._collection.description:
            desc = QLabel(self._collection.description)
            desc.setStyleSheet(DESC_STYLESHEET)
            desc.setWordWrap(True)
            desc.setMaximumHeight(60)
            layout.addWidget(desc)

        # Summary bar
        summary = self._build_summary()
        if summary:
            summary_label = QLabel(summary)
            summary_label.setStyleSheet(INFO_BOX_STYLESHEET)
            summary_label.setWordWrap(True)
            layout.addWidget(summary_label)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Section label
        tree_label = QLabel(self.tr("PROPRIEDADES"))
        tree_label.setStyleSheet(SECTION_LABEL_STYLESHEET)
        layout.addWidget(tree_label)

        # Tree
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels([self.tr("Propriedade"), self.tr("Valor")])
        self._tree.setAlternatingRowColors(True)
        self._tree.setStyleSheet(TREE_STYLESHEET)
        self._tree.header().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self._tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tree.header().setMinimumSectionSize(120)
        layout.addWidget(self._tree)

        self._populate_tree()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        copy_btn = QPushButton(self.tr("Copiar JSON"))
        copy_btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
        copy_btn.clicked.connect(self._on_copy_json)
        btn_layout.addWidget(copy_btn)

        close_btn = QPushButton(self.tr("Fechar"))
        close_btn.setStyleSheet(SEARCH_BUTTON_STYLESHEET)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _build_summary(self):
        parts = []
        license_val = self._raw.get("license")
        if license_val:
            parts.append(f"License: {license_val}")

        temporal = self._collection.temporal_extent
        if temporal and len(temporal) >= 2:
            start = temporal[0] or "..."
            end = temporal[1] or self.tr("presente")
            parts.append(f"Temporal: {start} / {end}")

        spatial = self._collection.spatial_extent
        if spatial and len(spatial) >= 4:
            bbox_str = ", ".join(f"{v:.2f}" for v in spatial[:4])
            parts.append(f"Bbox: [{bbox_str}]")

        return "  |  ".join(parts) if parts else None

    def _populate_tree(self):
        data = self._raw
        if not data:
            return

        # Ordered: top keys first, then remaining alphabetically
        ordered_keys = [k for k in self._TOP_KEYS if k in data]
        remaining = sorted(k for k in data if k not in self._TOP_KEYS)
        ordered_keys.extend(remaining)

        for key in ordered_keys:
            self._add_node(self._tree, key, data[key])

        self._tree.expandToDepth(0)

    def _add_node(self, parent, key, value):
        if isinstance(value, dict):
            node = self._make_item(parent, str(key), "", bold=True)
            for k in value:
                self._add_node(node, k, value[k])
        elif isinstance(value, list):
            node = self._make_item(
                parent, str(key),
                self.tr("[{n} itens]").format(n=len(value)),
                bold=True,
            )
            for i, item in enumerate(value):
                self._add_node(node, str(i), item)
        else:
            display = self._format_value(value)
            self._make_item(parent, str(key), display)

    @staticmethod
    def _make_item(parent, key, value, bold=False):
        item = QTreeWidgetItem(parent)
        item.setText(0, key)
        item.setText(1, str(value))
        item.setToolTip(0, key)
        item.setToolTip(1, str(value))
        if bold:
            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)
        return item

    @staticmethod
    def _format_value(value):
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def _on_copy_json(self):
        text = json.dumps(self._raw, indent=2, ensure_ascii=False)
        QApplication.clipboard().setText(text)
