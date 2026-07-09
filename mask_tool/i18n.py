"""UI translations. English is the default language; the choice is
persisted to settings.json.
界面翻译。默认英语，语言选择保存在 settings.json。"""
import json
import os

SETTINGS_PATH = "settings.json"
LANGS = ("en", "zh")
DEFAULT_LANG = "en"
_lang = DEFAULT_LANG

STRINGS = {
    "app_title": {
        "en": "HueMask v%s — Region-wise HSV Mask Annotation",
        "zh": "HueMask v%s — 分块HSV掩膜标注工具"},
    "err_title": {"en": "Error", "zh": "错误"},
    "info_title": {"en": "Info", "zh": "提示"},
    "unsaved_title": {"en": "Unsaved changes", "zh": "未保存"},
    "mismatch_title": {"en": "Size mismatch", "zh": "尺寸不符"},
    "no_images": {
        "en": "No images found in '%s'.",
        "zh": "'%s' 中没有图片。"},
    "open_data": {
        "en": "Open data folder…",
        "zh": "打开数据文件夹…"},
    "choose_data_title": {
        "en": "Choose data folder",
        "zh": "选择数据文件夹"},
    "no_data_hint": {
        "en": "No data folder found — click \"Open data folder…\" to choose one.",
        "zh": "未找到数据文件夹——点击「打开数据文件夹…」选择。"},
    "no_data_in_folder": {
        "en": "No images or 'images' subfolder found in:\n%s",
        "zh": "该文件夹中没有图片，也没有 'images'/'1_图像' 子文件夹：\n%s"},
    "language": {"en": "Language / 语言:", "zh": "Language / 语言:"},
    "show_raw": {
        "en": "Show raw image (no mask)",
        "zh": "显示原图(无掩膜)"},
    "mode_polygon": {"en": "Polygon fill", "zh": "多边形填充"},
    "mode_brush": {"en": "Brush", "zh": "画笔涂抹"},
    "mode_hsv": {"en": "HSV filter fill", "zh": "HSV过滤填充"},
    "help_text": {
        "en": ("Usage: draw a region on the image; pixels inside are set to "
               "\"(1) Target class\" below.\n\"(2) Source class\" restricts editing "
               "to pixels of one class; \"Any\" = change all."),
        "zh": ("用法：在图上框/涂出区域 → 区域内的像素改成下面的「① 目标类别」。\n"
               "「② 源类别」用来限定：只动原本属于某一类的像素，选「任意」=全部都改。")},
    "target_label": {
        "en": "(1) Target class:",
        "zh": "① 目标类别（改成这一类）:"},
    "target_tip": {
        "en": "Pixels in the selection will be painted as this class.",
        "zh": "选区里的像素最终会被刷成这个类别。"},
    "source_label": {
        "en": "(2) Source class:",
        "zh": "② 源类别（只改原来是）:"},
    "source_tip": {
        "en": ("Only pixels originally of this class are changed; \"Any\" changes "
               "all pixels in the region.\nE.g. fix pixels mislabeled as \"leaf\" "
               "back to \"spike\": set (1) to spike and (2) to leaf."),
        "zh": ("限定只修改原本属于某一类的像素；选「任意」则区域内全部都改。\n"
               "例：把误标成「叶」的部分改回「穗」——① 选 穗，② 选 叶。")},
    "source_any": {"en": "Any (all pixels)", "zh": "任意（区域内全部）"},
    "brush_size": {"en": "Brush size:", "zh": "画笔大小:"},
    "apply_hsv": {
        "en": "Apply HSV to region (Enter)",
        "zh": "应用HSV到框选区 (回车)"},
    "cancel_sel": {
        "en": "Cancel selection (Esc)",
        "zh": "取消框选 (Esc)"},
    "opacity": {"en": "Mask opacity:", "zh": "掩膜透明度:"},
    "undo": {"en": "Undo (Ctrl+Z)", "zh": "撤销 (Ctrl+Z)"},
    "save": {"en": "Save (Ctrl+S)", "zh": "保存当前图 (Ctrl+S)"},
    "files": {"en": "Files:", "zh": "文件列表:"},
    "coord_empty": {"en": "XY: ( , )", "zh": "坐标: ( , )"},
    "coord": {"en": "XY: (%d, %d)", "zh": "坐标: (%d, %d)"},
    "hsv_status": {
        "en": "Adjust H/S/V to preview, Enter = apply, Esc = cancel",
        "zh": "调整 H/S/V 预览，回车应用，Esc取消"},
    "saved": {"en": "Saved: %s", "zh": "已保存: %s"},
    "save_failed": {"en": "Save failed: %s", "zh": "保存失败: %s"},
    "cannot_read": {"en": "Cannot read image: %s", "zh": "无法读取图像: %s"},
    "mask_not_found": {
        "en": "Mask not found, creating blank: %s",
        "zh": "未找到掩膜，新建空白: %s"},
    "mismatch_text": {
        "en": "%s mask size differs from the image; resized to match.",
        "zh": "%s 掩膜尺寸与图像不符，已按原图缩放。"},
    "multichannel_warn": {
        "en": "Warning: mask %s has multiple channels, using channel 0",
        "zh": "警告: 掩膜 %s 为多通道，已取第0通道"},
    "unsaved_q": {
        "en": "Current image has unsaved changes. Save now?",
        "zh": "当前图有未保存修改，是否保存？"},
    "unsaved_star": {"en": " *unsaved", "zh": " *未保存"},
}


def tr(key):
    """Return the string for `key` in the current language."""
    return STRINGS[key][_lang]


def current_lang():
    return _lang


def set_lang(lang):
    global _lang
    if lang in LANGS:
        _lang = lang


def load_lang(path=SETTINGS_PATH):
    """Load the saved language; fall back to English."""
    global _lang
    lang = DEFAULT_LANG
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                lang = json.load(f).get("lang", DEFAULT_LANG)
        except (OSError, ValueError):
            lang = DEFAULT_LANG
    _lang = lang if lang in LANGS else DEFAULT_LANG
    return _lang


def save_lang(lang, path=SETTINGS_PATH):
    """Persist the language choice and make it current."""
    set_lang(lang)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"lang": _lang}, f, indent=2)
    except OSError:
        pass
