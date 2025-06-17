import contextlib
import os

from qgis._gui import QgisInterface
from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator
from qgis.PyQt.QtWidgets import QAction, QToolButton

from .processing_provider.csmap_provider import CSMapProcessingProvider

with contextlib.suppress(ImportError):
    from processing import execAlgorithmDialog


class CSMapPlugin:
    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.translator = None
        self.initTranslator()

    def initTranslator(self):
        locale = QSettings().value("locale/userLocale")
        if locale:
            locale = locale[0:2]
        else:
            locale = "en"

        locale_path = os.path.join(
            os.path.dirname(__file__), "i18n", f"csmap_algorithm_{locale}.qm"
        )

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            if self.translator.load(locale_path):
                QCoreApplication.installTranslator(self.translator)

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

    def tr(self, string):
        return QgsApplication.translate("CSMapProcessingAlgorithm", string)
