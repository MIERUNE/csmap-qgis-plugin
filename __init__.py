from qgis.gui import QgisInterface

from .plugin import CSMapPlugin


def classFactory(iface: QgisInterface):
    """
    Entrypoint for QGIS plugin.
    """

    return CSMapPlugin(iface)
