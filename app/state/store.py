from qgis.PyQt.QtCore import QObject, pyqtSignal


class AppState(QObject):
    # Colecoes
    collections_changed = pyqtSignal(object)

    # Busca
    search_started = pyqtSignal()
    search_results_changed = pyqtSignal(object)
    selected_item_changed = pyqtSignal(object)

    # Downloads
    download_started = pyqtSignal(str)
    download_progress = pyqtSignal(str, int)
    download_completed = pyqtSignal(str, str)
    download_failed = pyqtSignal(str, str)

    # UI feedback
    loading_changed = pyqtSignal(str, bool)
    error_occurred = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._collections = []
        self._search_result = None
        self._selected_item = None
        self._current_search_params = None

    @property
    def collections(self):
        return self._collections

    @collections.setter
    def collections(self, value):
        self._collections = value
        self.collections_changed.emit(value)

    @property
    def search_result(self):
        return self._search_result

    @search_result.setter
    def search_result(self, value):
        self._search_result = value
        self.search_results_changed.emit(value)

    @property
    def selected_item(self):
        return self._selected_item

    @selected_item.setter
    def selected_item(self, value):
        self._selected_item = value
        self.selected_item_changed.emit(value)

    @property
    def current_search_params(self):
        return self._current_search_params

    @current_search_params.setter
    def current_search_params(self, value):
        self._current_search_params = value

    def set_loading(self, operation, is_loading):
        self.loading_changed.emit(operation, is_loading)

    def set_error(self, operation, message):
        self.error_occurred.emit(operation, message)
