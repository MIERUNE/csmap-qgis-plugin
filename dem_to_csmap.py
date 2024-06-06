import os

from PyQt5.QtWidgets import QDialog, QMessageBox
from qgis.PyQt import uic

from csmap_py.csmap import process


class DemToCsMap(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "dem_to_csmap.ui"), self
        )

        self.ui.pushButton_run.clicked.connect(self.get_and_show_input_text)
        self.ui.pushButton_cancel.clicked.connect(self.close)

    def get_and_show_input_text(self):
        # テキストボックス値取得
        text_value = self.ui.lineEdit.text()
        # テキストボックス値をメッセージ表示
        QMessageBox.information(None, "ウィンドウ名", text_value)

        # 試しにCSMapの処理を実行：ちゃんと入力・出力をUIから参照しよう
        params = process.CsmapParams()
        input_path = "/Users/kanahiro/Downloads/dem.tif"
        output_path = "/Users/kanahiro/Downloads/out.tif"
        process.process(
            input_path,
            output_path,
            256,
            params=params,
        )
