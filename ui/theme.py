DOCK_STYLESHEET = """
QDockWidget {
    font-family: 'Segoe UI', 'Roboto', sans-serif;
}

QDockWidget::title {
    background-color: #2c3e50;
    color: white;
    padding: 8px;
    font-size: 13px;
    font-weight: bold;
}
"""


SEARCH_BUTTON_STYLESHEET = """
QPushButton {
    background-color: #2980b9;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #3498db;
}
QPushButton:pressed {
    background-color: #2471a3;
}
QPushButton:disabled {
    background-color: #7f8c8d;
}
"""

PRESET_BUTTON_STYLESHEET = """
QPushButton {
    background-color: #ecf0f1;
    border: 1px solid #bdc3c7;
    border-radius: 3px;
    padding: 4px 8px;
    font-size: 11px;
}
QPushButton:hover {
    background-color: #d5dbdb;
    border-color: #95a5a6;
}
"""

TABLE_STYLESHEET = """
QTableView {
    border: 1px solid #d5dbdb;
    gridline-color: #ecf0f1;
    selection-background-color: #d6eaf8;
    selection-color: #2c3e50;
    font-size: 11px;
}
QTableView::item {
    padding: 4px;
}
QHeaderView::section {
    background-color: #ecf0f1;
    border: 1px solid #d5dbdb;
    padding: 4px 8px;
    font-weight: bold;
    font-size: 11px;
}
"""

PAGINATION_STYLESHEET = """
QWidget#PaginationBar {
    background-color: #f8f9fa;
    border-top: 1px solid #d5dbdb;
    padding: 4px;
}
"""

HEADER_STYLESHEET = """
QLabel#HeaderLabel {
    color: #2c3e50;
    font-size: 14px;
    font-weight: bold;
    padding: 8px;
}
"""

SECTION_LABEL_STYLESHEET = """
QLabel {
    color: #7f8c8d;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
}
"""
