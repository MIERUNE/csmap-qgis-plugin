import unittest

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


if __name__ == "__main__":
    unittest.main()
