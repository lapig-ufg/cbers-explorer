import json
import uuid

from qgis.PyQt.QtCore import QObject, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import QgsNetworkAccessManager


class HttpClient(QObject):
    request_finished = pyqtSignal(str, object)
    request_error = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._manager = QgsNetworkAccessManager.instance()
        self._pending = {}

    def get(self, url):
        request_id = str(uuid.uuid4())
        request = QNetworkRequest(QUrl(url))
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        reply = self._manager.get(request)
        self._pending[request_id] = reply

        reply.finished.connect(lambda: self._on_reply_finished(request_id, reply))
        return request_id

    def post_json(self, url, payload):
        request_id = str(uuid.uuid4())
        request = QNetworkRequest(QUrl(url))
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        data = json.dumps(payload).encode("utf-8")
        reply = self._manager.post(request, data)
        self._pending[request_id] = reply

        reply.finished.connect(lambda: self._on_reply_finished(request_id, reply))
        return request_id

    def _on_reply_finished(self, request_id, reply):
        self._pending.pop(request_id, None)

        error = reply.error()
        if error != reply.NoError:
            status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) or 0
            error_msg = reply.errorString()
            from .errors import normalize_error
            friendly = normalize_error(status_code, error_msg)
            self.request_error.emit(request_id, friendly)
            reply.deleteLater()
            return

        raw = bytes(reply.readAll())
        try:
            data = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            data = raw

        self.request_finished.emit(request_id, data)
        reply.deleteLater()
