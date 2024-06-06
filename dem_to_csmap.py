import os

from PyQt5.QtWidgets import QDialog
from qgis.PyQt import uic

from csmap_py.csmap import process


class DemToCsMap(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "dem_to_csmap.ui"), self
        )

        # ウィンドウタイトル
        self.setWindowTitle("CSMap Plugin")
        # ラスタデータのみ選択（現状tifのみにしています）
        self.ui.mQgsFileWidget.setFilter('*.tif')
        # 出力先をフォルダに指定
        self.ui.mQgsFileWidget_.setStorageMode(1)

        self.ui.pushButton_run.clicked.connect(self.get_and_show_input_text)
        self.ui.pushButton_cancel.clicked.connect(self.close)

    def get_and_show_input_text(self):
        params = process.CsmapParams()

        # 入力・出力をUIで操作
        input_path = self.ui.mQgsFileWidget.filePath()
        output_path = self.ui.mQgsFileWidget_.filePath()
        process.process(
            input_path,
            output_path=os.path.join(output_path, 'csmap.tif'),
            chunk_size=256,
            params=params,
        )
