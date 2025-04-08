import contextlib

from PyQt5.QtWidgets import QAction, QToolButton
from qgis._gui import QgisInterface
from qgis.core import QgsApplication

from .processing_provider.csmap_provider import CSMapProcessingProvider

with contextlib.suppress(ImportError):
    from processing import execAlgorithmDialog


class CSMapPlugin:
    def __init__(self, iface: QgisInterface):
        self.iface = iface

    def initGui(self):
        self.provider = CSMapProcessingProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

        if self.iface:
            self.setup_algorithms_tool_button()

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)

    def setup_algorithms_tool_button(self):
        tool_button = QToolButton()
        icon = self.provider.icon()
        default_action = QAction(
            icon, "CS立体図を作成（CS 3D-Map）", self.iface.mainWindow()
        )
        default_action.triggered.connect(
            lambda: execAlgorithmDialog("csmap:dem_to_csmap", {})
        )
        tool_button.setDefaultAction(default_action)

        self.toolButtonAction = self.iface.addToolBarWidget(tool_button)
