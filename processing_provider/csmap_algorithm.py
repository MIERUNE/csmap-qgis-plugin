import multiprocessing
import os
import tempfile

from osgeo import gdal
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
    QgsRectangle,
)
from qgis.PyQt.QtCore import QCoreApplication

from ..csmap_py.csmap import process


class CSMapProcessingAlgorithm(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    PROCESSING_MODE = "PROCESSING_MODE"
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
            QgsProcessingParameterEnum(
                name=self.PROCESSING_MODE,
                description=self.tr("処理モード（本処理／プレビュー）"),
                options=[
                    self.tr("本処理"),
                    self.tr("プレビュー"),
                ],
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr("出力レイヤ"),
                optional=False,
            )
        )

        gf_size_param = QgsProcessingParameterNumber(
            name=self.GF_SIZE,
            description="Gaussian Filter Size",
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=12,
            minValue=1,
            maxValue=100,
        )
        gf_size_param.setFlags(
            gf_size_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(gf_size_param)

        gf_sigma_param = QgsProcessingParameterNumber(
            name=self.GF_SIGMA,
            description="Gaussian Filter Sigma",
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=3,
            minValue=1,
            maxValue=100,
        )
        gf_sigma_param.setFlags(
            gf_sigma_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(gf_sigma_param)

        curvature_size_param = QgsProcessingParameterNumber(
            name=self.CURVATURE_SIZE,
            description="Curvature Filter Size",
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=1,
            minValue=1,
            maxValue=100,
        )
        curvature_size_param.setFlags(
            curvature_size_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(curvature_size_param)

        height_scale_min_param = QgsProcessingParameterNumber(
            name=self.HEIGHT_SCALE_MIN,
            description="Height Scale Min",
            type=QgsProcessingParameterNumber.Double,
            defaultValue=0.0,
        )
        height_scale_min_param.setFlags(
            height_scale_min_param.flags()
            | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(height_scale_min_param)

        height_scale_max_param = QgsProcessingParameterNumber(
            name=self.HEIGHT_SCALE_MAX,
            description="Height Scale Max",
            type=QgsProcessingParameterNumber.Double,
            defaultValue=1000.0,
        )
        height_scale_max_param.setFlags(
            height_scale_max_param.flags()
            | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(height_scale_max_param)

        slope_scale_min_param = QgsProcessingParameterNumber(
            name=self.SLOPE_SCALE_MIN,
            description="Slope Scale Min",
            type=QgsProcessingParameterNumber.Double,
            defaultValue=0.0,
            minValue=0.0,
            maxValue=100.0,
        )
        slope_scale_min_param.setFlags(
            slope_scale_min_param.flags()
            | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(slope_scale_min_param)

        slope_scale_max_param = QgsProcessingParameterNumber(
            name=self.SLOPE_SCALE_MAX,
            description="Slope Scale Max",
            type=QgsProcessingParameterNumber.Double,
            defaultValue=1.5,
            minValue=0.0,
            maxValue=100.0,
        )
        slope_scale_max_param.setFlags(
            slope_scale_max_param.flags()
            | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(slope_scale_max_param)

        curvature_scale_min_param = QgsProcessingParameterNumber(
            name=self.CURVATURE_SCALE_MIN,
            description="Curvature Scale Min",
            type=QgsProcessingParameterNumber.Double,
            defaultValue=-0.1,
            minValue=-1.0,
            maxValue=1.0,
        )
        curvature_scale_min_param.setFlags(
            curvature_scale_min_param.flags()
            | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(curvature_scale_min_param)

        curvature_scale_max_param = QgsProcessingParameterNumber(
            name=self.CURVATURE_SCALE_MAX,
            description="Curvature Scale Max",
            type=QgsProcessingParameterNumber.Double,
            defaultValue=0.1,
            minValue=-1.0,
            maxValue=1.0,
        )
        curvature_scale_max_param.setFlags(
            curvature_scale_max_param.flags()
            | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(curvature_scale_max_param)

        chunk_size_param = QgsProcessingParameterNumber(
            name=self.CHUNK_SIZE,
            description="Chunk Size",
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=1024,
            minValue=256,
            maxValue=8192,
        )
        chunk_size_param.setFlags(
            chunk_size_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(chunk_size_param)

        max_workers_param = QgsProcessingParameterNumber(
            name=self.MAX_WORKERS,
            description="Max Workers",
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=multiprocessing.cpu_count(),
            minValue=1,
            maxValue=64,
        )
        max_workers_param.setFlags(
            max_workers_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(max_workers_param)

    def processAlgorithm(self, parameters, context, feedback):
        input_layer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        processing_mode = self.parameterAsEnum(
            parameters, self.PROCESSING_MODE, context
        )

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

        # processing mode
        if processing_mode == 1:  # preview mode
            return self.process_preview(
                input_layer, output_path, params, chunk_size, max_workers, feedback
            )
        else:
            return self.process_full(
                input_layer, output_path, params, chunk_size, max_workers, feedback
            )

    def process_preview(
        self, input_layer, output_path, params, chunk_size, max_workers, feedback
    ):
        """Process a part of the input image."""
        feedback.pushInfo(self.tr("プレビューを生成中です..."))

        try:
            temp_input = self.create_preview_input(input_layer, feedback)

            preview_chunk_size = min(chunk_size, 256)
            preview_max_workers = min(max_workers, 2)

            process.process(
                temp_input,
                output_path,
                chunk_size=preview_chunk_size,
                params=params,
                max_workers=preview_max_workers,
            )

            if os.path.exists(temp_input):
                os.remove(temp_input)

            feedback.pushInfo(self.tr("プレビューの生成が完了しました"))

        except Exception as e:
            feedback.reportError(
                self.tr(f"プレビューの生成中にエラーが発生しました: {str(e)}")
            )
            return {}

        return {self.OUTPUT: output_path}

    def process_full(
        self, input_layer, output_path, params, chunk_size, max_workers, feedback
    ):
        """Process the full input image."""
        feedback.pushInfo(self.tr("DEMを処理中です..."))

        try:
            process.process(
                input_layer.source(),
                output_path,
                chunk_size=chunk_size,
                params=params,
                max_workers=max_workers,
            )

            feedback.pushInfo(self.tr("処理が正常に完了しました"))

        except Exception as e:
            feedback.reportError(self.tr(f"処理中にエラーが発生しました: {str(e)}"))
            return {}

        return {self.OUTPUT: output_path}

    def create_preview_input(self, input_layer, feedback):
        """Extract the central portion of the input DEM to create a small preview area, approximately 5% of the total."""
        extent = input_layer.extent()

        center_x = extent.center().x()
        center_y = extent.center().y()
        preview_ratio = 0.05
        width = extent.width() * preview_ratio
        height = extent.height() * preview_ratio

        preview_extent = QgsRectangle(
            center_x - width / 2,
            center_y - height / 2,
            center_x + width / 2,
            center_y + height / 2,
        )

        temp_file = tempfile.NamedTemporaryFile(suffix=".tif", delete=False)
        temp_path = temp_file.name
        temp_file.close()

        ds = gdal.Open(input_layer.source())
        if ds is None:
            raise Exception(self.tr("入力DEMを開けませんでした"))

        geotransform = ds.GetGeoTransform()
        x_min = preview_extent.xMinimum()
        y_max = preview_extent.yMaximum()
        x_max = preview_extent.xMaximum()
        y_min = preview_extent.yMinimum()

        pixel_x_min = int((x_min - geotransform[0]) / geotransform[1])
        pixel_y_min = int((y_max - geotransform[3]) / geotransform[5])
        pixel_x_max = int((x_max - geotransform[0]) / geotransform[1])
        pixel_y_max = int((y_min - geotransform[3]) / geotransform[5])

        width_pixels = pixel_x_max - pixel_x_min
        height_pixels = pixel_y_max - pixel_y_min

        if width_pixels <= 0 or height_pixels <= 0:
            raise Exception(self.tr("プレビュー範囲が無効です"))

        gdal.Translate(
            temp_path,
            ds,
            srcWin=[pixel_x_min, pixel_y_min, width_pixels, height_pixels],
            format="GTiff",
        )

        ds = None

        return temp_path

    def tr(self, string):
        return QCoreApplication.translate("CSMapProcessingAlgorithm", string)

    def createInstance(self):
        return CSMapProcessingAlgorithm()

    def name(self):
        return "dem_to_csmap"

    def displayName(self):
        return self.tr("DEMをCS立体図に変換")

    def shortHelpString(self):
        return self.tr("入力のDEMをGeoTIFF形式のCS立体図に変換します。")
