import os
import unittest

from qgis.core import QgsProject

from dem_to_csmap import DemToCsMap

from .utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestMenu(unittest.TestCase):
    def test_menu(self):
        menu = DemToCsMap()

        assert menu.isVisible() is False
        menu.show()
        assert menu.isVisible() is True
        menu.hide()
        assert menu.isVisible() is False

        menu.mQgsFileWidget_input.setFilePath(
            os.path.join(os.path.dirname(__file__), "fixture", "12ke35_1mdem.tif")
        )
        menu.mQgsFileWidget_output.setFilePath(
            os.path.join(os.path.dirname(__file__), "_result.tif")
        )
        menu.pushButton_run.click()  # run process

        assert (
            os.path.exists(os.path.join(os.path.dirname(__file__), "_result.tif"))
            is True
        )
        assert len(QgsProject.instance().mapLayersByName("_result.tif")) == 1


if __name__ == "__main__":
    unittest.main()
