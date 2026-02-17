import json

from qgis.PyQt.QtCore import QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import QgsBlockingNetworkRequest

from .base_task import CbersTask
from ...domain.stac_parser import parse_search_result


class SearchTask(CbersTask):

    result_ready = pyqtSignal(object)

    def __init__(self, search_params, base_url):
        super().__init__("CBERS STAC Search")
        self._params = search_params
        self._base_url = base_url
        self._result = None

    def run(self):
        try:
            self.signals.status_message.emit("Buscando imagens STAC...")

            query = self._params.to_query_params()
            parts = []
            for k, v in query.items():
                parts.append(f"{k}={v}")
            url = f"{self._base_url}/search?{'&'.join(parts)}"

            request = QNetworkRequest(QUrl(url))
            request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

            blocker = QgsBlockingNetworkRequest()
            err = blocker.get(request)

            if self.isCanceled():
                return False

            if err != QgsBlockingNetworkRequest.NoError:
                self._exception = Exception(
                    f"Erro na requisicao STAC: {blocker.errorMessage()}"
                )
                return False

            reply = blocker.reply()
            raw = bytes(reply.content())
            data = json.loads(raw.decode("utf-8"))

            self._result = parse_search_result(data)

            self.signals.status_message.emit(
                f"{self._result.matched} imagens encontradas"
            )
            return True

        except Exception as e:
            self._exception = e
            return False

    def finished(self, result):
        if result and self._result:
            self.result_ready.emit(self._result)
        super().finished(result)
