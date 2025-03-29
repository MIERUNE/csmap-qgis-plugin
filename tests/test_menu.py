import os
import sys
import unittest

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from processing.core.Processing import Processing
from qgis.core import QgsProcessingFeedback, QgsProject, QgsRasterLayer
from qgis.PyQt.QtCore import QCoreApplication

from processing_provider import CSMapProcessingAlgorithm

from .utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestDemToCsMapAlgorithm(unittest.TestCase):
    def setUp(self):
        self.feedback = QgsProcessingFeedback()

        Processing.initialize()

        self.alg = CSMapProcessingAlgorithm()

        self.test_dem_path = os.path.join(
            os.path.dirname(__file__), "fixture", "12ke35_1mdem.tif"
        )

        self.output_path = os.path.join(os.path.dirname(__file__), "_result.tif")

    def test_algorithm(self):
        params = {"INPUT": self.test_dem_path, "OUTPUT": self.output_path}

        result = self.alg.processAlgorithm(params, self.feedback)
        self.assertEqual(result["OUTPUT"], self.output_path)

        self.assertTrue(os.path.exists(self.output_path))

        layer = QgsRasterLayer(self.output_path, "_result")
        self.assertTrue(layer.isValid())

        QgsProject.instance().addMapLayer(layer)

        self.assertEqual(len(QgsProject.instance().mapLayersByName("_result")), 1)

    def tearDown(self):
        if os.path.exists(self.output_path):
            QgsProject.instance().removeMapLayer(
                QgsProject.instance().mapLayersByName("_result")[0].id()
            )

            QCoreApplication.processEvents()
            try:
                os.remove(self.output_path)
            except OSError:
                pass


if __name__ == "__main__":
    unittest.main()
