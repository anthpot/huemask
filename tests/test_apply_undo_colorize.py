import numpy as np
from mask_tool.mask_ops import (
    apply_selection, undo_op, UndoStack, colorize_mask,
)


def _sel(shape, true_coords):
    s = np.zeros(shape, dtype=bool)
    for (y, x) in true_coords:
        s[y, x] = True
    return s


def test_apply_sets_target_id_and_returns_record():
    mask = np.zeros((5, 5), dtype=np.uint8)
    sel = _sel((5, 5), [(1, 1), (1, 2)])
    rec = apply_selection(mask, sel, target_id=3)
    assert mask[1, 1] == 3 and mask[1, 2] == 3
    assert mask[0, 0] == 0
    assert rec["bbox"] == (1, 2, 1, 3)   # y0,y1,x0,x1 (half-open)


def test_apply_no_change_returns_none():
    mask = np.full((4, 4), 2, dtype=np.uint8)
    sel = np.ones((4, 4), dtype=bool)
    assert apply_selection(mask, sel, target_id=2) is None  # 已全是 2


def test_source_filter_only_changes_matching_pixels():
    mask = np.array([[1, 2], [2, 1]], dtype=np.uint8)
    sel = np.ones((2, 2), dtype=bool)
    apply_selection(mask, sel, target_id=5, source_filter=2)
    assert mask.tolist() == [[1, 5], [5, 1]]   # 只有原来=2 的变 5


def test_undo_restores_previous_state():
    mask = np.zeros((5, 5), dtype=np.uint8)
    sel = _sel((5, 5), [(2, 2), (2, 3)])
    rec = apply_selection(mask, sel, target_id=4)
    undo_op(mask, rec)
    assert mask.sum() == 0


def test_undo_stack_maxlen_and_pop():
    st = UndoStack(maxlen=2)
    st.push({"bbox": (0, 1, 0, 1), "before": np.zeros((1, 1), np.uint8)})
    st.push({"bbox": (0, 1, 0, 1), "before": np.zeros((1, 1), np.uint8)})
    st.push(None)                      # None 不入栈
    st.push({"bbox": (1, 2, 1, 2), "before": np.zeros((1, 1), np.uint8)})
    assert st.can_undo() is True
    r = st.pop()
    assert r["bbox"] == (1, 2, 1, 2)   # LIFO
    st.pop()
    assert st.can_undo() is False
    assert st.pop() is None


def test_colorize_mask_maps_ids_to_bgr():
    mask = np.array([[0, 1], [2, 0]], dtype=np.uint8)
    palette = {0: (0, 0, 0), 1: (255, 0, 0), 2: (0, 255, 0)}
    out = colorize_mask(mask, palette)
    assert out.shape == (2, 2, 3)
    assert tuple(int(v) for v in out[0, 1]) == (255, 0, 0)
    assert tuple(int(v) for v in out[1, 0]) == (0, 255, 0)


def test_source_filter_zero_only_changes_background():
    mask = np.array([[0, 1], [2, 0]], dtype=np.uint8)
    sel = np.ones((2, 2), dtype=bool)
    apply_selection(mask, sel, target_id=5, source_filter=0)
    assert mask.tolist() == [[5, 1], [2, 5]]   # 只有原来=0 的变 5
