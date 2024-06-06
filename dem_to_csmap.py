import os

from PyQt5.QtWidgets import QDialog
from qgis.PyQt import uic
from qgis.utils import iface

from csmap_py.csmap import process


class DemToCsMap(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "dem_to_csmap.ui"), self
        )

        # ウィンドウタイトル
        self.setWindowTitle("CSMap Plugin")
        # QGISでサポートされているラスタデータのみ選択可能
        self.ui.mQgsFileWidget.setFilter('*.tif;;*.tiff;;*.dt0;;*.dt1;;*.dt2;;*.dem;;*.asc;;*.adf;;*.hgt;;*.bil;;*.nc;;*.img;;*.flt;;*.bt;;*.xyz;;*.grd;;*.ter')
        # 出力先をフォルダに指定
        self.ui.mQgsFileWidget_.setStorageMode(1)

        self.ui.pushButton_run.clicked.connect(self.convert_dem_to_csmap)
        self.ui.pushButton_cancel.clicked.connect(self.close)

    def convert_dem_to_csmap(self):
        params = process.CsmapParams()

        # 入力・出力をUIで操作
        input_path = self.ui.mQgsFileWidget.filePath()
        output_dir = self.ui.mQgsFileWidget_.filePath()
        output_path = os.path.join(output_dir, 'csmap.tif')

        process.process(
            input_path,
            output_path,
            chunk_size=256,
            params=params,
        )

        # csmap.tifをQGISに読み込む
        iface.addRasterLayer(output_path)

        self.close()
