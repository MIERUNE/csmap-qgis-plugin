import os

from PyQt5.QtWidgets import QDialog
from qgis.core import Qgis
from qgis.gui import QgsFileWidget
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

        # 入力データの制限
        self.ui.mQgsFileWidget_input.setFilter("*")

        # 出力データの設定
        self.ui.mQgsFileWidget_output.setFilter("*.tif")
        self.ui.mQgsFileWidget_output.setStorageMode(QgsFileWidget.StorageMode.SaveFile)

        # ボタンのクリックイベント
        self.ui.pushButton_run.clicked.connect(self.convert_dem_to_csmap)
        self.ui.pushButton_cancel.clicked.connect(self.close)

    def convert_dem_to_csmap(self):
        params = process.CsmapParams()

        # 入力・出力をUIで操作
        input_path = self.ui.mQgsFileWidget_input.filePath()
        output_path = self.ui.mQgsFileWidget_output.filePath()

        # comment

        try:
            process.process(
                input_path,
                output_path,
                chunk_size=256,
                params=params,
            )
        except Exception as e:
            iface.messageBar().pushMessage(
                "ERROR", f"処理中に問題が発生しました.: {e}", level=Qgis.Critical
            )
            return

        # 出力結果をQGISに追加
        iface.addRasterLayer(output_path, os.path.basename(output_path))

        self.close()
