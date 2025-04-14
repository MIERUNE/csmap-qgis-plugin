import os
import sys

from qgis._gui import QgisInterface

from .plugin import CSMapPlugin

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "csmap_py"))


def classFactory(iface: QgisInterface):
    """
    Entrypoint for QGIS plugin.
    """

    return CSMapPlugin(iface)
