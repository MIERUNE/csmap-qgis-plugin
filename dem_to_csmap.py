import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from qgis.core import Qgis, QgsProject, QgsRasterLayer
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

        # ウィンドウを常に全面に表示する
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # 入力データの制限
        self.ui.mQgsFileWidget_input.setFilter("*")

        # 出力データの設定
        self.ui.mQgsFileWidget_output.setFilter("*.tif")
        self.ui.mQgsFileWidget_output.setStorageMode(QgsFileWidget.StorageMode.SaveFile)

        # ボタンのクリックイベント
        self.ui.pushButton_run.clicked.connect(self.convert_dem_to_csmap)
        self.ui.pushButton_cancel.clicked.connect(self.close)

    def convert_dem_to_csmap(self):
        # パラメータの設定
        params = process.CsmapParams(
            gf_size=self.ui.spinBoxGfSize.value(),
            gf_sigma=self.ui.spinBoxGfSigma.value(),
            curvature_size=self.ui.spinBoxCurvatureSize.value(),
            height_scale=(
                self.ui.spinBoxHeightScaleMin.value(),
                self.ui.spinBoxHeightScaleMax.value(),
            ),
            slope_scale=(
                self.ui.doubleSpinBoxSlopeScaleMin.value(),
                self.ui.doubleSpinBoxSlopeScaleMax.value(),
            ),
            curvature_scale=(
                self.ui.doubleSpinBoxCurvatureScaleMin.value(),
                self.ui.doubleSpinBoxCurvatureScaleMax.value(),
            ),  # 曲率
        )

        # 入力・出力をUIで操作
        input_path = self.ui.mQgsFileWidget_input.filePath()
        output_path = self.ui.mQgsFileWidget_output.filePath()

        try:
            process.process(
                input_path,
                output_path,
                chunk_size=self.ui.spinBoxChunkSize.value(),
                params=params,
                max_workers=self.ui.spinBoxMaxWorkers.value(),
            )
        except Exception as e:
            iface.messageBar().pushMessage(
                "CSMap Plugin",
                f"DEMデータの処理中に問題が発生しました.: {e}",
                level=Qgis.Critical,
            )
            return

        # 出力結果をQGISに追加・マップキャンバスの中心に表示
        rlayer = QgsRasterLayer(output_path, os.path.basename(output_path))
        QgsProject.instance().addMapLayer(rlayer)
        iface.setActiveLayer(rlayer)
        iface.zoomToActiveLayer()

        iface.messageBar().pushMessage(
            "CSMap Plugin",
            f"変換が完了しました: {output_path}",
            level=Qgis.Info,
        )

        # 処理終了後にウィンドウを閉じるオプション
        if self.ui.checkBox_closeAfterProcessing.isChecked():
            self.close()
