from dataclasses import dataclass
from threading import Lock
from concurrent import futures

import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.transform import Affine

from csmap import calc
from csmap import color


@dataclass
class CsmapParams:
    gf_size: int = 12
    gf_sigma: int = 3
    curvature_size: int = 1
    height_scale: (float, float) = (0.0, 1000.0)
    slope_scale: (float, float) = (0.0, 1.5)
    curvature_scale: (float, float) = (-0.1, 0.1)


def csmap(dem: np.ndarray, params: CsmapParams) -> np.ndarray:
    """DEMからCS立体図を作成する"""
    # calclucate elements
    slope = calc.slope(dem)
    g = calc.gaussianfilter(dem, params.gf_size, params.gf_sigma)
    curvature = calc.curvature(g, params.curvature_size)

    # rgbify
    dem_rgb = color.rgbify(dem, color.height_blackwhite, scale=params.height_scale)
    slope_red = color.rgbify(slope, color.slope_red, scale=params.slope_scale)
    slope_bw = color.rgbify(slope, color.slope_blackwhite, scale=params.slope_scale)
    curvature_blue = color.rgbify(
        curvature, color.curvature_blue, scale=params.curvature_scale
    )
    curvature_ryb = color.rgbify(
        curvature, color.curvature_redyellowblue, scale=params.curvature_scale
    )

    dem_rgb = dem_rgb[:, 1:-1, 1:-1]  # remove padding

    # blend all rgb
    blend = color.blend(
        dem_rgb,
        slope_red,
        slope_bw,
        curvature_blue,
        curvature_ryb,
    )

    return blend


def _process_chunk(
    chunk: np.ndarray,
    dst: rasterio.io.DatasetWriter,
    x: int,
    y: int,
    write_size_x: int,
    write_size_y: int,
    params: CsmapParams,
    lock: Lock = None,
) -> np.ndarray:
    """チャンクごとの処理"""
    csmap_chunk = csmap(chunk, params)
    csmap_chunk_margin_removed = csmap_chunk[
        :,
        (params.gf_size + params.gf_sigma)
        // 2 : -((params.gf_size + params.gf_sigma) // 2),
        (params.gf_size + params.gf_sigma)
        // 2 : -((params.gf_size + params.gf_sigma) // 2),
    ]  # shape = (4, chunk_size - margin, chunk_size - margin)

    if lock is None:
        dst.write(
            csmap_chunk_margin_removed,
            window=Window(x, y, write_size_x, write_size_y),
        )
    else:
        with lock:
            dst.write(
                csmap_chunk_margin_removed,
                window=Window(x, y, write_size_x, write_size_y),
            )


def process(
    input_dem_path: str,
    output_path: str,
    chunk_size: int,
    params: CsmapParams,
    max_workers: int = 1,
):
    with rasterio.open(input_dem_path) as dem:
        margin = params.gf_size + params.gf_sigma  # ガウシアンフィルタのサイズ+シグマ
        # チャンクごとの処理結果には「淵=margin」が生じるのでこの部分を除外する必要がある
        margin_to_removed = margin // 2  # 整数値に切り捨てた値*両端

        # マージンを考慮したtransform
        transform = Affine(
            dem.transform.a,
            dem.transform.b,
            dem.transform.c + (1 + margin // 2) * dem.transform.a,  # 左端の座標をマージン分ずらす
            dem.transform.d,
            dem.transform.e,
            dem.transform.f + (1 + margin // 2) * dem.transform.e,  # 上端の座標をマージン分ずらす
            0.0,
            0.0,
            1.0,
        )

        # 生成されるCS立体図のサイズ
        out_width = dem.shape[1] - margin_to_removed * 2 - 2
        out_height = dem.shape[0] - margin_to_removed * 2 - 2

        with rasterio.open(
            output_path,
            "w",
            driver="GTiff",
            dtype=rasterio.uint8,
            count=4,
            width=out_width,
            height=out_height,
            crs=dem.crs,
            transform=transform,
            compress="LZW",
        ) as dst:
            # chunkごとに処理
            chunk_csmap_size = chunk_size - margin_to_removed * 2 - 2

            # 並列処理しない場合とする場合で処理を分ける
            if max_workers == 1:
                for y in range(0, dem.shape[0], chunk_csmap_size):
                    for x in range(0, dem.shape[1], chunk_csmap_size):
                        # csmpのどの部分を出力用配列に入れるかを計算
                        write_size_x = chunk_csmap_size
                        write_size_y = chunk_csmap_size
                        if x + chunk_csmap_size > out_width:
                            write_size_x = out_width - x
                        if y + chunk_csmap_size > out_height:
                            write_size_y = out_height - y

                        chunk = dem.read(1, window=Window(x, y, chunk_size, chunk_size))
                        _process_chunk(
                            chunk,
                            dst,
                            x,
                            y,
                            write_size_x,
                            write_size_y,
                            params,
                        )
            else:  # 並列処理する場合=ThreadPoolExecutorを使用する
                lock = Lock()  # 並列処理のロック
                with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # chunkごとに処理
                    for y in range(0, dem.shape[0], chunk_csmap_size):
                        for x in range(0, dem.shape[1], chunk_csmap_size):
                            # csmpのどの部分を出力用配列に入れるかを計算
                            write_size_x = chunk_csmap_size
                            write_size_y = chunk_csmap_size
                            if x + chunk_csmap_size > out_width:
                                write_size_x = out_width - x
                            if y + chunk_csmap_size > out_height:
                                write_size_y = out_height - y

                            chunk = dem.read(
                                1, window=Window(x, y, chunk_size, chunk_size)
                            )
                            executor.submit(
                                _process_chunk,
                                chunk,
                                dst,
                                x,
                                y,
                                write_size_x,
                                write_size_y,
                                params,
                                lock,
                            )
