import multiprocessing

from PyQt5.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
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

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr("入力レイヤ（DEM）"),
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr("出力レイヤ"),
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.GF_SIZE,
                description="Gaussian Filter Size",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=12,
                minValue=1,
                maxValue=100,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.GF_SIGMA,
                description="Gaussian Filter Sigma",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=3,
                minValue=1,
                maxValue=100,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.CURVATURE_SIZE,
                description="Curvature Filter Size",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=1,
                minValue=1,
                maxValue=100,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.HEIGHT_SCALE_MIN,
                description="Height Scale Min",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.HEIGHT_SCALE_MAX,
                description="Height Scale Max",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1000.0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.SLOPE_SCALE_MIN,
                description="Slope Scale Min",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.0,
                minValue=0.0,
                maxValue=100.0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.SLOPE_SCALE_MAX,
                description="Slope Scale Max",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1.5,
                minValue=0.0,
                maxValue=100.0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.CURVATURE_SCALE_MIN,
                description="Curvature Scale Min",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=-0.1,
                minValue=-1.0,
                maxValue=1.0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.CURVATURE_SCALE_MAX,
                description="Curvature Scale Max",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.1,
                minValue=-1.0,
                maxValue=1.0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.CHUNK_SIZE,
                description="Chunk Size",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=1024,
                minValue=256,
                maxValue=8192,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.MAX_WORKERS,
                description="Max Workers",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=multiprocessing.cpu_count(),
                minValue=1,
                maxValue=64,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_layer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        # parameters
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

        params = process.CsmapParams(
            gf_size=gf_size,
            gf_sigma=gf_sigma,
            curvature_size=curvature_size,
            height_scale=(height_scale_min, height_scale_max),
            slope_scale=(slope_scale_min, slope_scale_max),
            curvature_scale=(curvature_scale_min, curvature_scale_max),
        )

        feedback.pushInfo("DEMを処理中です...")

        try:
            process.process(
                input_layer.source(),
                output_path,
                chunk_size=chunk_size,
                params=params,
                max_workers=max_workers,
            )

            feedback.pushInfo("処理が正常に完了しました")

        except Exception as e:
            feedback.reportError(f"処理中にエラーが発生しました: {str(e)}")
            return {}

        return {self.OUTPUT: output_path}

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return CSMapProcessingAlgorithm()

    def name(self):
        return "dem_to_csmap"

    def displayName(self):
        return self.tr("CS立体図を作成（CS 3D-Map）")

    def shortHelpString(self):
        return self.tr("入力のDEMをGeoTIFF形式のCS立体図に変換します。")
