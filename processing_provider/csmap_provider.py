from pathlib import Path

from PyQt5.QtGui import QIcon
from qgis.core import QgsProcessingProvider

from .csmap_algorithm import CSMapProcessingAlgorithm


class CSMapProcessingProvider(QgsProcessingProvider):
    def loadAlgorithms(self, *args, **kwargs):
        self.addAlgorithm(CSMapProcessingAlgorithm())

    def id(self, *args, **kwargs):
        return "csmap"

    def name(self, *args, **kwargs):
        return self.tr("CSMap Plugin")

    def icon(self):
        path = (Path(__file__).parent / "icon.png").resolve()
        return QIcon(str(path))
