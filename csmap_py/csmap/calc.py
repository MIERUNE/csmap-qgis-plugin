import numpy as np


def slope(dem: np.ndarray) -> np.ndarray:
    """傾斜率を求める
    出力のndarrayのshapeは、(dem.shape[0] - 2, dem.shape[1] - 2)
    """
    z2 = dem[1:-1, 0:-2]
    z4 = dem[0:-2, 1:-1]
    z6 = dem[2:, 1:-1]
    z8 = dem[1:-1, 2:]
    p = (z6 - z4) / 2
    q = (z8 - z2) / 2
    p2 = p * p
    q2 = q * q

    slope = np.arctan((p2 + q2) ** 0.5)
    return slope


def gaussianfilter(image: np.ndarray, size: int, sigma: int) -> np.ndarray:
    """ガウシアンフィルター"""
    size = int(size) // 2
    x, y = np.mgrid[-size : size + 1, -size : size + 1]
    g = np.exp(-(x**2 + y**2) / (2 * sigma**2))
    kernel = g / g.sum()

    # 画像を畳み込む
    k_h, k_w = kernel.shape
    i_h, i_w = image.shape

    # パディングサイズを計算
    pad_h, pad_w = k_h // 2, k_w // 2

    # 画像にパディングを適用
    padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode="constant")

    # einsumを使用して畳み込みを行う
    sub_matrices = np.lib.stride_tricks.as_strided(
        padded, shape=(i_h, i_w, k_h, k_w), strides=padded.strides * 2
    )
    return np.einsum("ijkl,kl->ij", sub_matrices, kernel)


def curvature(dem: np.ndarray, cell_size: int) -> np.ndarray:
    """曲率を求める"""

    # SAGA の Slope, Aspect, Curvature の 9 parameter 2nd order polynom に準拠
    z1 = dem[0:-2, 0:-2]
    z2 = dem[1:-1, 0:-2]
    z3 = dem[2:, 0:-2]
    z4 = dem[0:-2, 1:-1]
    z5 = dem[1:-1, 1:-1]
    z6 = dem[2:, 1:-1]
    z7 = dem[0:-2, 2:]
    z8 = dem[1:-1, 2:]
    z9 = dem[2:, 2:]

    cell_area = cell_size * cell_size
    r = ((z4 + z6) / 2 - z5) / cell_area
    t = ((z2 + z8) / 2 - z5) / cell_area
    p = (z6 - z4) / (2 * cell_size)
    q = (z8 - z2) / (2 * cell_size)
    s = (z1 - z3 - z7 + z9) / (4 * cell_area)
    p2 = p * p
    q2 = q * q
    spq = s * p * q

    # gene
    return -2 * (r + t)

    # plan
    p2_q2 = p2 + q2
    p2_q2 = np.where(p2_q2 > 1e-6, p2_q2, np.nan)
    return -(t * p2 + r * q2 - 2 * spq) / ((p2_q2) ** 1.5)
