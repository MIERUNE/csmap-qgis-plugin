import os
import unittest

from qgis.core import QgsProject

from csmap_py import DemToCsMap

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

        filename = "_result.tif"
        output_path = os.path.join(os.path.dirname(__file__), filename)
        menu.mQgsFileWidget_output.setFilePath(output_path)

        menu.pushButton_run.click()  # run process

        assert os.path.exists(output_path) is True
        assert len(QgsProject.instance().mapLayersByName(filename)) == 1


if __name__ == "__main__":
    unittest.main()
