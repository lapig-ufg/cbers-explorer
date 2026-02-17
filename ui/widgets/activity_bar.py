"""Activity Bar — navegacao lateral com icones SVG (estilo VS Code).

Cores derivadas da QPalette do sistema para compatibilidade com temas claro/escuro.
"""

import os

from qgis.PyQt.QtCore import Qt, QSize, QRect, pyqtSignal
from qgis.PyQt.QtGui import QIcon, QPainter, QColor, QFont, QPen, QPalette
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QButtonGroup, QSizePolicy,
)


_ICONS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "assets", "icons",
)

# Cores de accent (intencionais, nao variam com tema)
_ACCENT = QColor("#1976D2")
_BADGE_BG = QColor("#FF9800")
_BADGE_TEXT = QColor("#FFFFFF")


class NavButton(QPushButton):
    """Botao de navegacao com icone SVG, badge e indicador accent."""

    def __init__(self, icon_path, tooltip, page_index, parent=None):
        super().__init__(parent)
        self._page_index = page_index
        self._badge_count = 0
        self._icon_path = icon_path
        self._hovered = False

        self.setFixedSize(40, 40)
        self.setCheckable(True)
        self.setToolTip(tooltip)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("border: none; background: transparent;")

        if os.path.exists(icon_path):
            self._icon = QIcon(icon_path)
        else:
            self._icon = QIcon()

    @property
    def page_index(self):
        return self._page_index

    def set_badge(self, count):
        self._badge_count = max(0, count)
        self.update()

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pal = self.palette()
        w, h = self.width(), self.height()

        # Background (hover/active)
        if self.isChecked() or self._hovered:
            painter.fillRect(0, 0, w, h, pal.color(QPalette.Mid))

        # Barra accent a esquerda (quando ativo)
        if self.isChecked():
            painter.fillRect(0, 0, 3, h, _ACCENT)

        # Icone centralizado
        icon_size = 20
        x = (w - icon_size) // 2
        y = (h - icon_size) // 2
        if not self._icon.isNull():
            pixmap = self._icon.pixmap(QSize(icon_size, icon_size))
            painter.drawPixmap(x, y, pixmap)

        # Badge
        if self._badge_count > 0:
            badge_size = 14
            bx = w - badge_size - 2
            by = 2
            painter.setPen(Qt.NoPen)
            painter.setBrush(_BADGE_BG)
            painter.drawEllipse(bx, by, badge_size, badge_size)

            painter.setPen(_BADGE_TEXT)
            font = QFont()
            font.setPixelSize(9)
            font.setBold(True)
            painter.setFont(font)
            text = str(self._badge_count) if self._badge_count < 100 else "99+"
            painter.drawText(
                QRect(bx, by, badge_size, badge_size), Qt.AlignCenter, text
            )

        painter.end()


class ActivityBar(QWidget):
    """Barra lateral de navegacao com icones verticais."""

    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(40)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setAutoFillBackground(True)

        # Fundo usa QPalette.Dark
        pal = self.palette()
        pal.setColor(QPalette.Window, pal.color(QPalette.Dark))
        self.setPalette(pal)

        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.setLayout(self._layout)

        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        self._button_group.buttonClicked.connect(self._on_button_clicked)

        self._buttons = []

    def add_button(self, icon_name, tooltip, page_index):
        """Adiciona botao de navegacao. icon_name e o nome do SVG (sem extensao)."""
        icon_path = os.path.join(_ICONS_DIR, f"{icon_name}.svg")
        btn = NavButton(icon_path, tooltip, page_index, self)
        self._button_group.addButton(btn)
        self._layout.addWidget(btn)
        self._buttons.append(btn)

        if len(self._buttons) == 1:
            btn.setChecked(True)

        return btn

    def add_stretch(self):
        self._layout.addStretch()

    def add_separator(self):
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: palette(mid);")
        self._layout.addWidget(sep)

    def button_at(self, index):
        if 0 <= index < len(self._buttons):
            return self._buttons[index]
        return None

    def select_page(self, page_index):
        for btn in self._buttons:
            if btn.page_index == page_index:
                btn.setChecked(True)
                self.page_changed.emit(page_index)
                return

    def _on_button_clicked(self, button):
        self.page_changed.emit(button.page_index)
