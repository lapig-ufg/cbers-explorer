import os

from qgis.PyQt.QtCore import QObject
from qgis.core import QgsApplication, QgsProject

from ...infra.tasks.download_task import DownloadTask


class DownloadController(QObject):

    def __init__(self, state, config_repo, parent=None):
        super().__init__(parent)
        self._state = state
        self._config = config_repo
        self._active_tasks = {}

    @property
    def active_downloads(self):
        return dict(self._active_tasks)

    def download_asset(self, item, asset):
        dest_dir = self._config.get("download_dir")
        if not dest_dir:
            dest_dir = QgsProject.instance().homePath()
        if not dest_dir:
            dest_dir = os.path.expanduser("~")

        ext = ".tif"
        if "png" in asset.media_type.lower():
            ext = ".png"
        elif "jpeg" in asset.media_type.lower() or "jpg" in asset.media_type.lower():
            ext = ".jpg"

        filename = f"{item.id}_{asset.key}{ext}"
        dest_path = os.path.join(dest_dir, filename)

        task = DownloadTask(asset.href, dest_path, item.id)
        task.signals.progress_changed.connect(
            lambda pct, iid=item.id: self._on_progress(iid, pct)
        )
        task.file_ready.connect(self._on_file_ready)
        task.signals.completed.connect(
            lambda ok, msg, iid=item.id: self._on_completed(iid, ok, msg)
        )

        self._active_tasks[item.id] = task
        self._state.download_started.emit(item.id)
        QgsApplication.taskManager().addTask(task)

    def cancel_download(self, item_id):
        task = self._active_tasks.get(item_id)
        if task:
            task.cancel()

    def cancel_all(self):
        for task in self._active_tasks.values():
            task.cancel()

    def _on_progress(self, item_id, percent):
        self._state.download_progress.emit(item_id, percent)

    def _on_file_ready(self, file_path, item_id):
        self._active_tasks.pop(item_id, None)
        self._state.download_completed.emit(item_id, file_path)

    def _on_completed(self, item_id, success, message):
        if not success:
            self._active_tasks.pop(item_id, None)
            self._state.download_failed.emit(item_id, message)
