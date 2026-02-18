import json

from qgis.PyQt.QtCore import Qt, QCoreApplication
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


class ItemMetadataDialog(QDialog):

    _TOP_KEYS = [
        "id", "type", "collection", "datetime", "bbox",
        "geometry", "properties", "assets", "links",
    ]

    def __init__(self, item, parent=None):
        super().__init__(parent)
        self._item = item
        self._raw = item.raw_data or {}

        self.setWindowTitle(
            self.tr("Metadados do Item: {id}").format(id=item.id)
        )
        self.setMinimumSize(560, 480)
        self.resize(640, 580)

        self._build_ui()

    def tr(self, message):
        return QCoreApplication.translate("ItemMetadataDialog", message)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Header
        title = QLabel(self._item.id)
        title.setStyleSheet(TITLE_STYLESHEET)
        title.setWordWrap(True)
        title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(title)

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
        parts.append(f"Collection: {self._item.collection}")

        dt = self._item.datetime
        if dt:
            parts.append(f"Date: {dt[:10]}")

        cc = self._item.cloud_cover
        if cc is not None:
            parts.append(f"Cloud: {cc:.1f}%")

        bbox = self._item.bbox
        if bbox and len(bbox) >= 4:
            bbox_str = ", ".join(f"{v:.2f}" for v in bbox[:4])
            parts.append(f"Bbox: [{bbox_str}]")

        return "  |  ".join(parts)

    def _populate_tree(self):
        data = self._raw
        if not data:
            return

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
            for i, v in enumerate(value):
                self._add_node(node, str(i), v)
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
