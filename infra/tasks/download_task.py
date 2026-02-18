import os

from qgis.PyQt.QtCore import QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import QgsBlockingNetworkRequest

from .base_task import CbersTask


class DownloadTask(CbersTask):

    file_ready = pyqtSignal(str, str)

    def __init__(self, url, dest_path, item_id):
        super().__init__(f"Download {item_id}")
        self._url = url
        self._dest_path = dest_path
        self._item_id = item_id

    MIN_VALID_SIZE = 1024  # bytes — any real asset is larger than 1KB

    def run(self):
        try:
            self.signals.status_message.emit(f"Baixando {self._item_id}...")

            dest_dir = os.path.dirname(self._dest_path)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)

            request = QNetworkRequest(QUrl(self._url))
            blocker = QgsBlockingNetworkRequest()
            err = blocker.get(request)

            if self.isCanceled():
                return False

            if err != QgsBlockingNetworkRequest.NoError:
                self._exception = Exception(
                    f"Erro no download: {blocker.errorMessage()}"
                )
                return False

            reply = blocker.reply()
            content = bytes(reply.content())

            # Validate: reject empty or suspiciously small responses
            if len(content) < self.MIN_VALID_SIZE:
                self._exception = Exception(
                    f"Conteudo invalido ({len(content)} bytes)"
                )
                return False

            # Validate: detect HTML error pages saved as binary files
            header = content[:512].lstrip()
            if header[:1] in (b"<",) and (
                b"<html" in header.lower() or b"<!doctype" in header.lower()
            ):
                self._exception = Exception(
                    "Servidor retornou pagina HTML em vez do arquivo"
                )
                return False

            with open(self._dest_path, "wb") as f:
                f.write(content)

            self.signals.progress_changed.emit(100)
            self.signals.status_message.emit(f"Download concluido: {self._item_id}")
            return True

        except Exception as e:
            self._exception = e
            return False

    def finished(self, result):
        if result:
            self.file_ready.emit(self._dest_path, self._item_id)
        super().finished(result)
