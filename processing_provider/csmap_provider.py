from pathlib import Path

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from .csmap_algorithm import CSMapProcessingAlgorithm


class CSMapProcessingProvider(QgsProcessingProvider):
    def loadAlgorithms(self, *args, **kwargs):
        self.addAlgorithm(CSMapProcessingAlgorithm())

    def id(self, *args, **kwargs):
        return "csmap"

    def name(self, *args, **kwargs):
        return self.tr("CSMap Plugin")

    def icon(self):
        path = (Path(__file__).parent.parent / "imgs" / "icon.png").resolve()
        return QIcon(str(path))
