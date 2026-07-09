import os
import cv2
import numpy as np
import json


def imread_unicode(path, flags=cv2.IMREAD_COLOR):
    """读取图像，兼容中文/Unicode 路径。失败返回 None。"""
    if not os.path.exists(path):
        return None
    data = np.fromfile(path, dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, flags)


def imwrite_unicode(path, img, ext=".png"):
    """写出图像，兼容中文/Unicode 路径。成功返回 True，失败返回 False。"""
    ok, buf = cv2.imencode(ext, img)
    if not ok:
        return False
    try:
        buf.tofile(path)
    except (OSError, IOError):
        return False
    return True


DEFAULT_CLASSES = {
    0: {"name": "background", "color": [0, 0, 0]},
    1: {"name": "spike",      "color": [220, 20, 60]},
    2: {"name": "leaf",       "color": [0, 200, 0]},
    3: {"name": "internode",  "color": [30, 110, 255]},
    4: {"name": "node",       "color": [255, 220, 0]},
    5: {"name": "number_tag", "color": [200, 0, 200]},
    6: {"name": "ruler",      "color": [0, 230, 230]},
    7: {"name": "colorcard",  "color": [255, 140, 0]},
}


def load_class_config(path):
    """读取类别配置 {id:int -> {"name","color"}}。缺失则写入默认并返回。"""
    if not os.path.exists(path):
        save_class_config(path, DEFAULT_CLASSES)
        return {k: dict(v) for k, v in DEFAULT_CLASSES.items()}
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {int(k): v for k, v in raw.items()}


def save_class_config(path, config):
    """以字符串键写出 JSON。"""
    raw = {str(k): v for k, v in config.items()}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2, ensure_ascii=False)
