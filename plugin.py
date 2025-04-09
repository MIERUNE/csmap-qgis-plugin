import contextlib

from PyQt5.QtWidgets import QAction, QToolButton
from qgis._gui import QgisInterface
from qgis.core import QgsApplication

from .processing_provider.csmap_provider import CSMapProcessingProvider

with contextlib.suppress(ImportError):
    from qgis.processing import execAlgorithmDialog


class CSMapPlugin:
    def __init__(self, iface: QgisInterface):
        self.iface = iface

    def initGui(self):
        self.provider = CSMapProcessingProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

        if self.iface:
            self.setup_algorithm_tool_button()

    def unload(self):
        self.teardown_algorithm_tool_button()
        QgsApplication.processingRegistry().removeProvider(self.provider)

    def setup_algorithm_tool_button(self):
        if hasattr(self, "toolButtonAction") and self.toolButtonAction:
            return

        tool_button = QToolButton()
        icon = self.provider.icon()
        default_action = QAction(
            icon, self.tr("CS立体図を作成"), self.iface.mainWindow()
        )
        default_action.triggered.connect(
            lambda: execAlgorithmDialog("csmap:dem_to_csmap", {})
        )
        tool_button.setDefaultAction(default_action)

        self.toolButtonAction = self.iface.addToolBarWidget(tool_button)

    def teardown_algorithm_tool_button(self):
        if hasattr(self, "toolButtonAction"):
            self.iface.removeToolBarIcon(self.toolButtonAction)
            del self.toolButtonAction

    def tr(self, message):
        return QgsApplication.translate("CS 3D-Map", message)
