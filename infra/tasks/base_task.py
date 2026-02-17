from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.core import QgsTask


class TaskSignals(QObject):
    progress_changed = pyqtSignal(int)
    status_message = pyqtSignal(str)
    completed = pyqtSignal(bool, str)


class CbersTask(QgsTask):

    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)
        self.signals = TaskSignals()
        self._exception = None

    def finished(self, result):
        if result:
            self.signals.completed.emit(True, "")
        else:
            msg = str(self._exception) if self._exception else "Erro desconhecido"
            self.signals.completed.emit(False, msg)
