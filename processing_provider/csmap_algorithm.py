import multiprocessing
import os

from PyQt5.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterLayer,
    QgsProject,
    QgsRasterLayer,
)

from ..csmap_py.csmap import process


class CSMapProcessingAlgorithm(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    GF_SIZE = "GF_SIZE"
    GF_SIGMA = "GF_SIGMA"
    CURVATURE_SIZE = "CURVATURE_SIZE"
    HEIGHT_SCALE_MIN = "HEIGHT_SCALE_MIN"
    HEIGHT_SCALE_MAX = "HEIGHT_SCALE_MAX"
    SLOPE_SCALE_MIN = "SLOPE_SCALE_MIN"
    SLOPE_SCALE_MAX = "SLOPE_SCALE_MAX"
    CURVATURE_SCALE_MIN = "CURVATURE_SCALE_MIN"
    CURVATURE_SCALE_MAX = "CURVATURE_SCALE_MAX"
    CHUNK_SIZE = "CHUNK_SIZE"
    MAX_WORKERS = "MAX_WORKERS"
    LOAD_RESULT = "LOAD_RESULT"

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr("入力レイヤ（DEM）"),
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr("出力レイヤ"),
                "GeoTIFF files(*.tif *.tiff *.TIF *.TIFF)",
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.GF_SIZE,
                "Gaussian Filter Size",
                QgsProcessingParameterNumber.Integer,
                12,
                minValue=1,
                maxValue=100,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.GF_SIGMA,
                "Gaussian Filter Sigma",
                QgsProcessingParameterNumber.Integer,
                3,
                minValue=1,
                maxValue=100,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.CURVATURE_SIZE,
                "Curvature Size",
                QgsProcessingParameterNumber.Integer,
                1,
                minValue=1,
                maxValue=100,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.HEIGHT_SCALE_MIN,
                "Height Scale Min",
                QgsProcessingParameterNumber.Double,
                0.0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.HEIGHT_SCALE_MAX,
                "Height Scale Max",
                QgsProcessingParameterNumber.Double,
                1000.0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SLOPE_SCALE_MIN,
                "Slope Scale Min",
                QgsProcessingParameterNumber.Double,
                0.0,
                minValue=0.0,
                maxValue=100.0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SLOPE_SCALE_MAX,
                "Slope Scale Max",
                QgsProcessingParameterNumber.Double,
                1.5,
                minValue=0.0,
                maxValue=100.0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.CURVATURE_SCALE_MIN,
                "Curvature Scale Min",
                QgsProcessingParameterNumber.Double,
                -0.1,
                minValue=-1.0,
                maxValue=1.0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.CURVATURE_SCALE_MAX,
                "Curvature Scale Max",
                QgsProcessingParameterNumber.Double,
                0.1,
                minValue=-1.0,
                maxValue=1.0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.CHUNK_SIZE,
                "Chunk Size",
                QgsProcessingParameterNumber.Integer,
                1024,
                minValue=256,
                maxValue=8192,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.MAX_WORKERS,
                "Max Workers",
                QgsProcessingParameterNumber.Integer,
                multiprocessing.cpu_count(),
                minValue=1,
                maxValue=64,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.LOAD_RESULT,
                "アルゴリズムの終了後に出力ファイルを開く",
                defaultValue=True,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        input_layer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        output_path = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        gf_size = self.parameterAsInt(parameters, self.GF_SIZE, context)
        gf_sigma = self.parameterAsInt(parameters, self.GF_SIGMA, context)
        curvature_size = self.parameterAsInt(parameters, self.CURVATURE_SIZE, context)

        height_scale_min = self.parameterAsDouble(
            parameters, self.HEIGHT_SCALE_MIN, context
        )
        height_scale_max = self.parameterAsDouble(
            parameters, self.HEIGHT_SCALE_MAX, context
        )

        slope_scale_min = self.parameterAsDouble(
            parameters, self.SLOPE_SCALE_MIN, context
        )
        slope_scale_max = self.parameterAsDouble(
            parameters, self.SLOPE_SCALE_MAX, context
        )

        curvature_scale_min = self.parameterAsDouble(
            parameters, self.CURVATURE_SCALE_MIN, context
        )
        curvature_scale_max = self.parameterAsDouble(
            parameters, self.CURVATURE_SCALE_MAX, context
        )

        chunk_size = self.parameterAsInt(parameters, self.CHUNK_SIZE, context)
        max_workers = self.parameterAsInt(parameters, self.MAX_WORKERS, context)

        load_result = self.parameterAsBool(parameters, self.LOAD_RESULT, context)

        params = process.CsmapParams(
            gf_size=gf_size,
            gf_sigma=gf_sigma,
            curvature_size=curvature_size,
            height_scale=(height_scale_min, height_scale_max),
            slope_scale=(slope_scale_min, slope_scale_max),
            curvature_scale=(curvature_scale_min, curvature_scale_max),
        )

        feedback.pushInfo("Processing DEM to CS Map...")

        try:
            process.process(
                input_layer.source(),
                output_path,
                chunk_size=chunk_size,
                params=params,
                max_workers=max_workers,
            )

            feedback.pushInfo("処理が正常に完了しました")

            if load_result and context.project() is not None:
                rlayer = QgsRasterLayer(output_path, os.path.basename(output_path))
                QgsProject.instance().addMapLayer(rlayer)

        except Exception as e:
            feedback.reportError(f"処理中にエラーが発生しました: {str(e)}")
            return {}

        return {self.OUTPUT: output_path}

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return CSMapProcessingAlgorithm()

    def name(self):
        return "dem_to_csmap"

    def displayName(self):
        return self.tr("CS立体図を作成（CS 3D-Map）")

    def shortHelpString(self):
        return self.tr("入力のDEMをGeoTIFF形式のCS立体図に変換します。")
