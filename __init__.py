# -*- coding: utf-8 -*-
"""
CBERS Explorer - QGIS Plugin
Search and retrieve CBERS-4A satellite imagery from BDC STAC.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load CbersExplorerPlugin class.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .plugin import CbersExplorerPlugin
    return CbersExplorerPlugin(iface)
