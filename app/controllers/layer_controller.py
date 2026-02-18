import tempfile

from qgis.PyQt.QtCore import QObject, QCoreApplication
from qgis.core import QgsRasterLayer, QgsProject
from osgeo import gdal


class LayerController(QObject):

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self._iface = iface

    def tr(self, message):
        return QCoreApplication.translate("LayerController", message)

    def add_cog_to_map(self, item_id, cog_url, layer_name=None):
        uri = f"/vsicurl/{cog_url}"
        name = layer_name or item_id
        layer = QgsRasterLayer(uri, name, "gdal")
        if layer.isValid():
            QgsProject.instance().addMapLayer(layer)
            self._iface.messageBar().pushSuccess(
                "CBERS Explorer",
                self.tr("Camada adicionada: {name}").format(name=name),
            )
            return layer
        else:
            self._iface.messageBar().pushWarning(
                "CBERS Explorer",
                self.tr("Falha ao carregar: {name}").format(name=name),
            )
            return None

    def add_mosaic_to_map(self, urls, label):
        vrt_path = tempfile.mktemp(suffix=".vrt")
        vsicurl_urls = [f"/vsicurl/{u}" for u in urls]
        gdal.BuildVRT(
            vrt_path, vsicurl_urls, options=gdal.BuildVRTOptions(separate=False)
        )
        layer = QgsRasterLayer(vrt_path, label, "gdal")
        if layer.isValid():
            QgsProject.instance().addMapLayer(layer)
            self._iface.messageBar().pushSuccess(
                "CBERS Explorer",
                self.tr("Mosaico adicionado: {label}").format(label=label),
            )
            return layer
        else:
            self._iface.messageBar().pushWarning(
                "CBERS Explorer",
                self.tr("Falha ao criar mosaico: {label}").format(label=label),
            )
            return None

    def add_downloaded_to_map(self, file_path, layer_name):
        import os
        if not os.path.isfile(file_path) or os.path.getsize(file_path) < 1024:
            self._iface.messageBar().pushWarning(
                "CBERS Explorer",
                self.tr("Falha ao carregar arquivo: {name}").format(name=layer_name),
            )
            return None
        layer = QgsRasterLayer(file_path, layer_name, "gdal")
        if layer.isValid():
            QgsProject.instance().addMapLayer(layer)
            self._iface.messageBar().pushSuccess(
                "CBERS Explorer",
                self.tr("Arquivo adicionado: {name}").format(name=layer_name),
            )
            return layer
        else:
            self._iface.messageBar().pushWarning(
                "CBERS Explorer",
                self.tr("Falha ao carregar arquivo: {name}").format(name=layer_name),
            )
            return None
