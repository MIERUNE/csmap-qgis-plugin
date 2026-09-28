"""Processing アルゴリズム経由で DEM → CS 立体図の変換が実際に回ることのテスト。

processAlgorithm は例外を握りつぶして reportError するだけなので、
run() の戻り値だけでなく feedback のエラーと出力ラスタの中身を検証する。
"""

import numpy as np
import pytest
from osgeo import gdal, osr
from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback

ALGORITHM_ID = "csmap:dem_to_csmap"

DEM_SIZE = 600  # CHUNK_SIZE の最小値 (256) より大きくして複数チャンクに分割させる
PIXEL_SIZE = 10.0
ORIGIN_X, ORIGIN_Y = -3000.0, 3000.0
EPSG = 6677
NODATA = -9999.0
NODATA_SLICE = slice(100, 150)  # 入力 DEM の NoData 領域 (行・列とも)

GF_SIZE, GF_SIGMA = 12, 3
# フィルタの影響で出力は入力よりも周囲が (gf_size + gf_sigma) // 2 + 1 画素ずつ小さくなる
MARGIN = (GF_SIZE + GF_SIGMA) // 2 + 1
OUT_SIZE = DEM_SIZE - MARGIN * 2


class _Feedback(QgsProcessingFeedback):
    def __init__(self):
        super().__init__()
        self.errors = []

    def reportError(self, error, fatalError=False):
        self.errors.append(error)
        super().reportError(error, fatalError)


@pytest.fixture(scope="module")
def dem_path(tmp_path_factory):
    """丘と起伏のある DEM (NoData 領域つき) を作る"""
    y, x = np.mgrid[0:DEM_SIZE, 0:DEM_SIZE].astype(np.float32)
    center = DEM_SIZE / 2
    dem = (
        800 * np.exp(-((x - center) ** 2 + (y - center) ** 2) / (2 * 120**2))
        + 20 * np.sin(x / 15) * np.cos(y / 20)
        + 0.2 * x
    ).astype(np.float32)
    dem[NODATA_SLICE, NODATA_SLICE] = NODATA

    path = str(tmp_path_factory.mktemp("dem") / "dem.tif")
    ds = gdal.GetDriverByName("GTiff").Create(
        path, DEM_SIZE, DEM_SIZE, 1, gdal.GDT_Float32
    )
    ds.SetGeoTransform((ORIGIN_X, PIXEL_SIZE, 0, ORIGIN_Y, 0, -PIXEL_SIZE))
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(EPSG)
    ds.SetProjection(srs.ExportToWkt())
    band = ds.GetRasterBand(1)
    band.SetNoDataValue(NODATA)
    band.WriteArray(dem)
    ds = None
    return path


@pytest.fixture(scope="module")
def registry(qgis_app):
    from plugin_dir.processing_provider.csmap_provider import CSMapProcessingProvider

    provider = CSMapProcessingProvider()
    registry = QgsApplication.processingRegistry()
    assert registry.addProvider(provider)
    yield registry
    registry.removeProvider(provider)


def _run(registry, dem_path, output_path, **params):
    alg = registry.createAlgorithmById(ALGORITHM_ID)
    assert alg is not None

    parameters = {
        "INPUT": dem_path,
        "OUTPUT": str(output_path),
        "PROCESSING_MODE": 0,
        "GF_SIZE": GF_SIZE,
        "GF_SIGMA": GF_SIGMA,
        "CHUNK_SIZE": 256,
        "MAX_WORKERS": 1,
    }
    parameters.update(params)

    feedback = _Feedback()
    results, ok = alg.run(parameters, QgsProcessingContext(), feedback)
    assert ok
    assert feedback.errors == []
    assert results == {"OUTPUT": str(output_path)}
    assert output_path.exists()
    return output_path


def _read(path):
    ds = gdal.Open(str(path))
    assert ds is not None
    return ds, ds.ReadAsArray()


def test_main_process(registry, dem_path, tmp_path):
    output = _run(registry, dem_path, tmp_path / "csmap.tif")
    ds, arr = _read(output)

    # RGBA の uint8 で、フィルタのマージン分だけ小さくなる
    assert ds.RasterCount == 4
    assert ds.GetRasterBand(1).DataType == gdal.GDT_Byte
    assert (ds.RasterXSize, ds.RasterYSize) == (OUT_SIZE, OUT_SIZE)

    # 座標系は入力を引き継ぎ、原点はマージン分ずれる
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(EPSG)
    assert srs.IsSame(osr.SpatialReference(ds.GetProjection()))
    assert ds.GetGeoTransform() == pytest.approx(
        (
            ORIGIN_X + MARGIN * PIXEL_SIZE,
            PIXEL_SIZE,
            0,
            ORIGIN_Y - MARGIN * PIXEL_SIZE,
            0,
            -PIXEL_SIZE,
        )
    )

    rgb, alpha = arr[:3], arr[3]
    nodata_center = (NODATA_SLICE.start + NODATA_SLICE.stop) // 2 - MARGIN

    # 入力の NoData は透過になる
    assert alpha[nodata_center, nodata_center] == 0
    assert (rgb[:, nodata_center, nodata_center] == 0).all()

    # NoData 以外は不透明で、地形に応じた色が付いている (単色になっていない)
    valid = alpha == 255
    assert valid.sum() > OUT_SIZE * OUT_SIZE * 0.9
    assert all(rgb[band][valid].std() > 1 for band in range(3))


def test_parallel_matches_sequential(registry, dem_path, tmp_path):
    sequential = _run(registry, dem_path, tmp_path / "seq.tif", MAX_WORKERS=1)
    parallel = _run(registry, dem_path, tmp_path / "par.tif", MAX_WORKERS=4)

    np.testing.assert_array_equal(_read(sequential)[1], _read(parallel)[1])


def test_preview(registry, dem_path, tmp_path):
    output = _run(registry, dem_path, tmp_path / "preview.tif", PROCESSING_MODE=1)
    ds, arr = _read(output)

    # 中心付近の約 5% だけを処理する
    assert ds.RasterCount == 4
    assert 0 < ds.RasterXSize < OUT_SIZE
    assert 0 < ds.RasterYSize < OUT_SIZE
    assert (arr[3] == 255).all()
