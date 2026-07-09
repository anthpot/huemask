import numpy as np
from mask_tool.mask_ops import (
    polygon_selection, brush_selection, hsv_selection,
)


def test_polygon_selection_fills_interior():
    sel = polygon_selection((10, 10), [(2, 2), (2, 6), (6, 6), (6, 2)])
    assert sel.dtype == bool
    assert sel[4, 4] == True
    assert sel[0, 0] == False
    # 角落附近内部为真，外部为假
    assert sel.sum() > 0


def test_brush_selection_single_point_circle():
    sel = brush_selection((20, 20), [(10, 10)], radius=3)
    assert sel[10, 10] == True
    assert sel[10, 13] == True       # 半径内(同行,列+3)
    assert sel[10, 19] == False      # 半径外


def test_brush_selection_asymmetric_point_uses_x_as_col():
    # 点 (x=3, y=7) -> sel[7, 3] 为 True，锁定 x=列/y=行 约定
    sel = brush_selection((20, 20), [(3, 7)], radius=1)
    assert sel[7, 3] == True


def test_brush_selection_connects_segments():
    # 两点同一行(y=5)，x 从 10 到 30，连线为水平线，中点 sel[5,20]
    sel = brush_selection((40, 40), [(10, 5), (30, 5)], radius=2)
    assert sel[5, 20] == True


def test_hsv_selection_matches_range():
    # 造一张 HSV 图：左半 H=60(绿)，右半 H=0
    hsv = np.zeros((4, 4, 3), dtype=np.uint8)
    hsv[:, :2] = (60, 200, 200)
    hsv[:, 2:] = (0, 200, 200)
    sel = hsv_selection(hsv, (50, 100, 100), (70, 255, 255))
    assert sel[0, 0] == True
    assert sel[0, 3] == False
