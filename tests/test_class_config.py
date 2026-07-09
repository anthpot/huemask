import json
from mask_tool.io_utils import (
    DEFAULT_CLASSES, load_class_config, save_class_config,
)


def test_default_classes_have_8_ids():
    assert set(DEFAULT_CLASSES.keys()) == set(range(8))
    assert DEFAULT_CLASSES[1]["name"] == "spike"
    assert len(DEFAULT_CLASSES[1]["color"]) == 3


def test_load_creates_default_when_missing(tmp_path):
    path = str(tmp_path / "class_config.json")
    cfg = load_class_config(path)
    assert set(cfg.keys()) == set(range(8))   # keys are ints
    # 文件应已写出
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    assert "1" in raw   # JSON 中键是字符串


def test_save_then_load_roundtrip_with_int_keys(tmp_path):
    path = str(tmp_path / "c.json")
    cfg = {0: {"name": "bg", "color": [1, 2, 3]},
           1: {"name": "spike", "color": [255, 0, 0]}}
    save_class_config(path, cfg)
    back = load_class_config(path)
    assert back[1]["name"] == "spike"
    assert back[1]["color"] == [255, 0, 0]
    assert isinstance(list(back.keys())[0], int)
