"""Stylesheets centralizados usando palette() para compatibilidade com temas claro/escuro.

Regras de contraste:
- Texto principal: palette(window-text) sobre palette(window)
- Texto em inputs: palette(text) sobre palette(base)
- Accent/destaque: palette(highlighted-text) sobre palette(highlight)
- Botoes: palette(button-text) sobre palette(button)
- Nunca usar palette(dark) ou palette(bright-text) para texto — sem contraste
  garantido em temas escuros/claros.
"""

DOCK_STYLESHEET = """
QDockWidget {
    font-family: 'Segoe UI', 'Roboto', sans-serif;
}

QDockWidget::title {
    background-color: palette(highlight);
    color: palette(highlighted-text);
    padding: 8px;
    font-size: 13px;
    font-weight: bold;
}
"""

SEARCH_BUTTON_STYLESHEET = """
QPushButton {
    background-color: palette(highlight);
    color: palette(highlighted-text);
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 12px;
}
QPushButton:hover {
    background-color: palette(link);
    color: palette(highlighted-text);
}
QPushButton:pressed {
    background-color: palette(mid);
    color: palette(window-text);
}
QPushButton:disabled {
    background-color: palette(mid);
    color: palette(midlight);
}
"""

PRESET_BUTTON_STYLESHEET = """
QPushButton {
    background-color: palette(button);
    border: 1px solid palette(mid);
    border-radius: 3px;
    padding: 4px 8px;
    font-size: 11px;
    color: palette(button-text);
}
QPushButton:hover {
    background-color: palette(mid);
    border-color: palette(highlight);
    color: palette(window-text);
}
"""

TABLE_STYLESHEET = """
QTableView {
    border: 1px solid palette(mid);
    gridline-color: palette(midlight);
    selection-background-color: palette(highlight);
    selection-color: palette(highlighted-text);
    background-color: palette(base);
    alternate-background-color: palette(alternate-base);
    color: palette(text);
    font-size: 11px;
}
QTableView::item {
    padding: 4px;
}
QHeaderView::section {
    background-color: palette(button);
    color: palette(button-text);
    border: 1px solid palette(mid);
    padding: 4px 8px;
    font-weight: bold;
    font-size: 11px;
}
"""

TREE_STYLESHEET = """
QTreeWidget {
    border: 1px solid palette(mid);
    background-color: palette(base);
    alternate-background-color: palette(alternate-base);
    color: palette(text);
    font-size: 11px;
}
QTreeWidget::item {
    padding: 3px 4px;
}
QTreeWidget::item:selected {
    background-color: palette(highlight);
    color: palette(highlighted-text);
}
QHeaderView::section {
    background-color: palette(button);
    color: palette(button-text);
    border: 1px solid palette(mid);
    padding: 4px 8px;
    font-weight: bold;
    font-size: 11px;
}
"""

PAGINATION_STYLESHEET = """
QWidget#PaginationBar {
    background-color: palette(alternate-base);
    border-top: 1px solid palette(mid);
    padding: 4px;
}
"""

HEADER_STYLESHEET = """
QLabel#HeaderLabel {
    color: palette(window-text);
    font-size: 14px;
    font-weight: bold;
    padding: 8px;
}
"""

SECTION_LABEL_STYLESHEET = """
QLabel {
    color: palette(highlight);
    font-size: 11px;
    font-weight: bold;
}
"""

TITLE_STYLESHEET = (
    "font-size: 14px; font-weight: bold; "
    "color: palette(highlighted-text); "
    "background-color: palette(highlight); "
    "padding: 6px 10px; border-radius: 3px;"
)

DESC_STYLESHEET = "color: palette(window-text); font-size: 11px;"

INFO_BOX_STYLESHEET = (
    "background-color: palette(alternate-base); "
    "padding: 6px; border-radius: 3px; font-size: 11px; "
    "color: palette(text);"
)

HIGHLIGHT_BOX_STYLESHEET = (
    "background-color: palette(highlight); "
    "padding: 6px; border-radius: 3px; "
    "font-weight: bold; color: palette(highlighted-text);"
)

EMPTY_STATE_STYLESHEET = "color: palette(window-text); font-size: 12px; padding: 20px;"

THUMBNAIL_STYLESHEET = "background-color: palette(alternate-base); border-radius: 4px;"
