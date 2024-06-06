import numpy as np


def rgbify(arr: np.ndarray, method, scale: (float, float) = None) -> np.ndarray:
    """ndarrayをRGBに変換する
    - arrは変更しない
    - ndarrayのshapeは、(4, height, width) 4はRGBA
    """

    _min = arr.min() if scale is None else scale[0]
    _max = arr.max() if scale is None else scale[1]

    # -x ~ x を 0 ~ 1 に正規化
    arr = (arr - _min) / (_max - _min)
    # clamp
    arr = np.where(arr < 0, 0, arr)
    arr = np.where(arr > 1, 1, arr)

    # 3次元に変換
    rgb = method(arr)
    return rgb


def slope_red(arr: np.ndarray) -> np.ndarray:
    rgb = np.zeros((4, arr.shape[0], arr.shape[1]), dtype=np.uint8)
    rgb[0, :, :] = 255 - arr * 155  # R: 255 -> 100
    rgb[1, :, :] = 245 - arr * 195  # G: 245 -> 50
    rgb[2, :, :] = 235 - arr * 215  # B: 235 -> 20
    rgb[3, :, :] = 255
    return rgb


def slope_blackwhite(arr: np.ndarray) -> np.ndarray:
    rgb = np.zeros((4, arr.shape[0], arr.shape[1]), dtype=np.uint8)
    rgb[0, :, :] = (1 - arr) * 255  # R
    rgb[1, :, :] = (1 - arr) * 255  # G
    rgb[2, :, :] = (1 - arr) * 255  # B
    rgb[3, :, :] = 255  # A
    return rgb


def curvature_blue(arr: np.ndarray) -> np.ndarray:
    rgb = np.zeros((4, arr.shape[0], arr.shape[1]), dtype=np.uint8)
    rgb[0, :, :] = 35 + arr * 190  # R: 35 -> 225
    rgb[1, :, :] = 80 + arr * 155  # G: 80 -> 235
    rgb[2, :, :] = 100 + arr * 145  # B: 100 -> 245
    rgb[3, :, :] = 255
    return rgb


def curvature_redyellowblue(arr: np.ndarray) -> np.ndarray:
    # value:0-1 to: red -> yellow -> blue
    # interpolate between red and yellow, and yellow and blue, by linear

    # 0-0.5: blue -> white
    rgb1 = np.zeros((4, arr.shape[0], arr.shape[1]), dtype=np.uint8)
    rgb1[0, :, :] = 75 + arr * 170 * 2  # R: 75 -> 245
    rgb1[1, :, :] = 100 + arr * 145 * 2  # G: 100 -> 245
    rgb1[2, :, :] = 165 + arr * 80 * 2  # B: 165 -> 245

    # 0.5-1: white -> red
    rgb2 = np.zeros((4, arr.shape[0], arr.shape[1]), dtype=np.uint8)
    rgb2[0, :, :] = 245 - (arr * 2 - 1) * 100  # R: 245 -> 145
    rgb2[1, :, :] = 245 - (arr * 2 - 1) * 190  # G: 245 -> 55
    rgb2[2, :, :] = 245 - (arr * 2 - 1) * 195  # B: 245 -> 50

    # blend
    rgb = np.where(arr < 0.5, rgb1, rgb2)
    rgb[3, :, :] = 255

    return rgb


def height_blackwhite(arr: np.ndarray) -> np.ndarray:
    rgb = np.zeros((4, arr.shape[0], arr.shape[1]), dtype=np.uint8)
    rgb[0, :, :] = (1 - arr) * 255  # R
    rgb[1, :, :] = (1 - arr) * 255  # G
    rgb[2, :, :] = (1 - arr) * 255  # B
    rgb[3, :, :] = 255
    return rgb


def blend(
    dem_bw: np.ndarray,
    slope_red: np.ndarray,
    slope_bw: np.ndarray,
    curvature_blue: np.ndarray,
    curvature_ryb: np.ndarray,
    blend_params: dict = {
        "slope_bw": 0.5,  # alpha blending based on the paper
        "curvature_ryb": 0.25,  # 0.5 / 2
        "slope_red": 0.125,  # 0.5 / 2 / 2
        "curvature_blue": 0.06125,  # 0.5 / 2 / 2 / 2
        "dem": 0.030625,  # 0.5 / 2 / 2 / 2 / 2
    },
) -> np.ndarray:
    """blend all rgb
    全てのndarrayは同じshapeであること
    DEMを用いて処理した他の要素は、DEMよりも1px内側にpaddingされているので
    あらかじめDEMのpaddingを除外しておく必要がある
    """
    _blend = np.zeros((4, dem_bw.shape[0], dem_bw.shape[1]), dtype=np.uint8)
    _blend = (
        dem_bw * blend_params["dem"]
        + slope_red * blend_params["slope_red"]
        + slope_bw * blend_params["slope_bw"]
        + curvature_blue * blend_params["curvature_blue"]
        + curvature_ryb * blend_params["curvature_ryb"]
    )
    _blend = _blend.astype(np.uint8)  # force uint8
    _blend[3, :, :] = 255  # alpha
    return _blend
