import os
import numpy as np
import cv2
from mask_tool.io_utils import imwrite_unicode, imread_unicode
from mask_tool.mask_ops import polygon_selection, apply_selection


def test_edited_mask_saves_and_reloads_identically(tmp_path):
    mask = np.zeros((50, 60), dtype=np.uint8)
    sel = polygon_selection(mask.shape, [(10, 10), (10, 30), (30, 30), (30, 10)])
    apply_selection(mask, sel, target_id=3)
    path = str(tmp_path / "穗子_out.png")
    assert imwrite_unicode(path, mask) is True
    back = imread_unicode(path, cv2.IMREAD_UNCHANGED)
    if back.ndim == 3:
        back = back[:, :, 0]
    assert back.dtype == np.uint8
    assert np.array_equal(back, mask)
    assert set(np.unique(back).tolist()) == {0, 3}
