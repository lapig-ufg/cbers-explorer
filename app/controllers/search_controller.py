from qgis.PyQt.QtCore import QObject
from qgis.core import QgsApplication

from ...domain.models import SearchParams
from ...domain.stac_parser import parse_collections_response
from ...infra.tasks.search_task import SearchTask


class SearchController(QObject):

    def __init__(self, state, http_client, config_repo, parent=None):
        super().__init__(parent)
        self._state = state
        self._http = http_client
        self._config = config_repo
        self._current_task = None
        self._pending_collections_id = None

        self._http.request_finished.connect(self._on_http_finished)
        self._http.request_error.connect(self._on_http_error)

    def load_collections(self):
        base_url = self._config.get("stac_base_url")
        url = f"{base_url}/collections"
        self._state.set_loading("collections", True)
        self._pending_collections_id = self._http.get(url)

    def search(self, params):
        if self._current_task:
            self._current_task.cancel()

        self._state.current_search_params = params
        self._state.set_loading("search", True)
        self._state.search_started.emit()

        base_url = self._config.get("stac_base_url")
        task = SearchTask(params, base_url)
        task.result_ready.connect(self._on_search_result)
        task.signals.completed.connect(self._on_search_completed)
        self._current_task = task
        QgsApplication.taskManager().addTask(task)

    def next_page(self):
        params = self._state.current_search_params
        if not params:
            return
        result = self._state.search_result
        if result and result.next_page:
            params.page = result.next_page
            self.search(params)

    def prev_page(self):
        params = self._state.current_search_params
        if not params:
            return
        result = self._state.search_result
        if result and result.prev_page:
            params.page = result.prev_page
            self.search(params)

    def _on_search_result(self, result):
        self._state.search_result = result

    def _on_search_completed(self, success, message):
        self._state.set_loading("search", False)
        self._current_task = None
        if not success:
            self._state.set_error("search", message)

    def _on_http_finished(self, request_id, data):
        if request_id == self._pending_collections_id:
            self._pending_collections_id = None
            self._state.set_loading("collections", False)
            collections = parse_collections_response(data)
            self._state.collections = collections

    def _on_http_error(self, request_id, message):
        if request_id == self._pending_collections_id:
            self._pending_collections_id = None
            self._state.set_loading("collections", False)
            self._state.set_error("collections", message)
