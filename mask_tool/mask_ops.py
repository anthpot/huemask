import cv2
import numpy as np


def polygon_selection(shape, polygon):
    """返回多边形内部为 True 的布尔掩膜。
    shape=(H,W)，polygon=[(x,y),...]，x=列、y=行（与 cv2 一致）。"""
    sel = np.zeros(shape, dtype=np.uint8)
    if polygon and len(polygon) >= 3:
        cv2.fillPoly(sel, [np.array(polygon, dtype=np.int32)], 1)
    return sel.astype(bool)


def brush_selection(shape, points, radius):
    """沿点序列画实心圆与连接线段，返回布尔掩膜。
    points 为 [(x, y), ...]，x=列、y=行（与 cv2 一致）。"""
    sel = np.zeros(shape, dtype=np.uint8)
    r = max(1, int(radius))
    pts = [(int(x), int(y)) for (x, y) in points]
    for (x, y) in pts:
        cv2.circle(sel, (x, y), r, 1, -1)
    for p, q in zip(pts, pts[1:]):
        cv2.line(sel, p, q, 1, thickness=r * 2)
    return sel.astype(bool)


def hsv_selection(hsv_img, lower, upper):
    """cv2.inRange 的布尔包装。lower/upper 为 (H,S,V)。"""
    m = cv2.inRange(hsv_img, np.array(lower, dtype=np.uint8),
                    np.array(upper, dtype=np.uint8))
    return m.astype(bool)


def apply_selection(mask, selection, target_id, source_filter=None):
    """把 selection 命中的像素改为 target_id；支持源类别限制。
    原地修改 mask，返回撤销记录或 None（无实际改动）。"""
    eff = selection.copy()
    if source_filter is not None:
        eff &= (mask == source_filter)
    changed = eff & (mask != target_id)
    if not changed.any():
        return None
    ys, xs = np.where(changed)
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    before = mask[y0:y1, x0:x1].copy()
    mask[changed] = target_id
    return {"bbox": (y0, y1, x0, x1), "before": before}


def undo_op(mask, record):
    """用撤销记录还原 mask 的对应 bbox 区域。"""
    if record is None:
        return
    y0, y1, x0, x1 = record["bbox"]
    mask[y0:y1, x0:x1] = record["before"]


class UndoStack:
    def __init__(self, maxlen=20):
        self._stack = []
        self.maxlen = maxlen

    def push(self, record):
        if record is None:
            return
        self._stack.append(record)
        if len(self._stack) > self.maxlen:
            self._stack.pop(0)

    def can_undo(self):
        return bool(self._stack)

    def pop(self):
        return self._stack.pop() if self._stack else None

    def clear(self):
        self._stack.clear()


def colorize_mask(mask, palette_bgr):
    """按 id->BGR 上色，返回 HxWx3 BGR 图。"""
    out = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
    for cid, color in palette_bgr.items():
        out[mask == cid] = color
    return out
