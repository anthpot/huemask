import os
from mask_tool.app import resolve_data_dirs, dir_has_images


def test_resolve_prefers_chinese_legacy_dirs(tmp_path):
    (tmp_path / "1_图像").mkdir()
    (tmp_path / "images").mkdir()
    dirs = resolve_data_dirs(str(tmp_path))
    assert os.path.basename(dirs[0]) == "1_图像"
    assert os.path.basename(dirs[1]) == "2_掩膜"
    assert os.path.basename(dirs[2]) == "3_修正掩膜"


def test_resolve_english_dirs(tmp_path):
    (tmp_path / "images").mkdir()
    dirs = resolve_data_dirs(str(tmp_path))
    assert [os.path.basename(d) for d in dirs] == \
        ["images", "masks", "masks_corrected"]


def test_resolve_returns_none_when_missing(tmp_path):
    assert resolve_data_dirs(str(tmp_path)) is None


def test_dir_has_images(tmp_path):
    assert dir_has_images(str(tmp_path)) is False
    (tmp_path / "a.txt").write_text("x")
    assert dir_has_images(str(tmp_path)) is False
    (tmp_path / "b.JPG").write_bytes(b"\xff\xd8")
    assert dir_has_images(str(tmp_path)) is True


def test_dir_has_images_missing_path(tmp_path):
    assert dir_has_images(str(tmp_path / "nope")) is False
