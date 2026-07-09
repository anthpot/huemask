import os
import numpy as np
import cv2
from mask_tool.io_utils import imread_unicode, imwrite_unicode


def test_imwrite_then_imread_roundtrip_ascii(tmp_path):
    img = np.zeros((4, 5, 3), dtype=np.uint8)
    img[1, 2] = (10, 20, 30)
    path = str(tmp_path / "a.png")
    assert imwrite_unicode(path, img) is True
    back = imread_unicode(path)
    assert back is not None
    assert back.shape == (4, 5, 3)
    assert tuple(int(v) for v in back[1, 2]) == (10, 20, 30)


def test_roundtrip_unicode_path(tmp_path):
    img = np.full((3, 3), 7, dtype=np.uint8)
    path = str(tmp_path / "穗子_掩膜.png")
    assert imwrite_unicode(path, img) is True
    back = imread_unicode(path, cv2.IMREAD_UNCHANGED)
    assert back is not None
    assert back.shape == (3, 3)
    assert int(back[0, 0]) == 7


def test_imread_missing_returns_none(tmp_path):
    assert imread_unicode(str(tmp_path / "nope.png")) is None


def test_imwrite_failure_returns_false(tmp_path):
    img = np.zeros((2, 2, 3), dtype=np.uint8)
    bad_path = str(tmp_path / "no_such_dir" / "x.png")
    assert imwrite_unicode(bad_path, img) is False
