from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar,
)

from ..theme import (
    PRESET_BUTTON_STYLESHEET, TITLE_STYLESHEET, EMPTY_STATE_STYLESHEET,
)


class DownloadsPanel(QWidget):

    def __init__(self, state, download_controller, parent=None):
        super().__init__(parent)
        self._state = state
        self._download_controller = download_controller
        self._rows = {}  # item_id -> row_index

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel(self.tr("Downloads"))
        title.setStyleSheet(TITLE_STYLESHEET)
        header_layout.addWidget(title)
        header_layout.addStretch()

        self._cancel_all_btn = QPushButton(self.tr("Cancelar Todos"))
        self._cancel_all_btn.setStyleSheet(PRESET_BUTTON_STYLESHEET)
        self._cancel_all_btn.clicked.connect(self._on_cancel_all)
        header_layout.addWidget(self._cancel_all_btn)
        layout.addLayout(header_layout)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels([
            self.tr("Item"),
            self.tr("Progresso"), self.tr("Status"),
        ])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

        # Empty state
        self._empty_label = QLabel(self.tr("Nenhum download em andamento"))
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setStyleSheet(EMPTY_STATE_STYLESHEET)
        layout.addWidget(self._empty_label)

    def _connect_signals(self):
        self._state.download_started.connect(self._on_download_started)
        self._state.download_progress.connect(self._on_download_progress)
        self._state.download_completed.connect(self._on_download_completed)
        self._state.download_failed.connect(self._on_download_failed)

    def _on_download_started(self, item_id):
        self._empty_label.setVisible(False)

        row = self._table.rowCount()
        self._table.insertRow(row)
        self._rows[item_id] = row

        self._table.setItem(row, 0, QTableWidgetItem(item_id))

        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(0)
        self._table.setCellWidget(row, 1, progress)

        self._table.setItem(row, 2, QTableWidgetItem(self.tr("Baixando...")))

    def _on_download_progress(self, item_id, percent):
        row = self._rows.get(item_id)
        if row is None:
            return
        progress = self._table.cellWidget(row, 1)
        if isinstance(progress, QProgressBar):
            progress.setValue(percent)

    def _on_download_completed(self, item_id, file_path):
        row = self._rows.get(item_id)
        if row is None:
            return
        progress = self._table.cellWidget(row, 1)
        if isinstance(progress, QProgressBar):
            progress.setValue(100)
        self._table.setItem(row, 2, QTableWidgetItem(self.tr("Concluido")))
        self._update_empty_state()

    def _on_download_failed(self, item_id, error):
        row = self._rows.get(item_id)
        if row is None:
            return
        self._table.setItem(
            row, 2, QTableWidgetItem(self.tr("Erro: {msg}").format(msg=error[:30]))
        )
        self._update_empty_state()

    def _on_cancel_all(self):
        self._download_controller.cancel_all()
        self._table.setRowCount(0)
        self._rows.clear()
        self._empty_label.setVisible(True)
