import os
import re
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from mask_tool import __version__
from mask_tool.i18n import tr, load_lang, save_lang, current_lang
from mask_tool.io_utils import (
    imread_unicode, imwrite_unicode, load_class_config,
)
from mask_tool.mask_ops import (
    polygon_selection, brush_selection, hsv_selection,
    apply_selection, undo_op, UndoStack, colorize_mask,
)
from mask_tool.image_canvas import ImageCanvas

# Directory names: prefer legacy Chinese folders if present, else English ones
# 目录名：优先使用中文旧目录（若存在），否则使用英文目录
if os.path.isdir("1_图像"):
    IMG_DIR, SRC_MASK_DIR, OUT_MASK_DIR = "1_图像", "2_掩膜", "3_修正掩膜"
else:
    IMG_DIR, SRC_MASK_DIR, OUT_MASK_DIR = "images", "masks", "masks_corrected"

CLASS_CONFIG_PATH = "class_config.json"
# 1.0 = render at native resolution; zooming is handled by the canvas (fit / wheel)
# 1.0 = 按原分辨率渲染（缩放清晰）；缩放由画布的 fit/滚轮控制
INITIAL_SCALE = 1.0


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]


class MaskEditor(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        load_lang()
        self.valid_startup = True
        if not os.path.isdir(IMG_DIR):
            QtWidgets.QMessageBox.critical(
                self, tr("err_title"), tr("img_dir_missing") % IMG_DIR)
            self.valid_startup = False
            return
        os.makedirs(OUT_MASK_DIR, exist_ok=True)

        self.class_config = load_class_config(CLASS_CONFIG_PATH)
        self.ids = sorted(self.class_config.keys())
        # id -> BGR
        self.palette_bgr = {
            cid: (c["color"][2], c["color"][1], c["color"][0])
            for cid, c in self.class_config.items()
        }

        self.file_list = sorted(
            [f for f in os.listdir(IMG_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))],
            key=natural_key)
        self.index = 0
        self.raw_image = None      # full-resolution BGR / 全分辨率 BGR
        self.raw_hsv = None        # full-resolution HSV / 全分辨率 HSV
        self.mask = None           # full-resolution uint8 class IDs / 全分辨率 uint8 ID
        self.display_image = None  # BGR image used for display / 显示用 BGR
        self.undo = UndoStack(maxlen=20)
        self.dirty = False
        self.target_id = self.ids[0] if self.ids else 0
        self.source_filter = None   # None = any / None=任意, otherwise int class id
        self.mode = "hsv"           # default to HSV filter mode / 默认 HSV 过滤模式
        self.hsv_region = None      # pending HSV polygon in mask coords / HSV模式待确认框选(掩膜坐标)

        self.initial_scale = INITIAL_SCALE
        self.canvas = ImageCanvas()
        self.canvas.initial_scale = self.initial_scale

        self.resize(1500, 800)
        self._init_ui()
        self._retranslate()

        if not self.file_list:
            QtWidgets.QMessageBox.warning(
                self, tr("info_title"), tr("no_images") % IMG_DIR)
        else:
            self.file_list_widget.setCurrentRow(0)  # triggers load_image / 触发 load_image

    # ---------- UI ----------
    def _init_ui(self):
        layout = QtWidgets.QHBoxLayout(self)

        self.scroll_area = QtWidgets.QScrollArea()
        self.canvas.scrollArea = self.scroll_area
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area, 6)

        ctrl = QtWidgets.QGridLayout()
        row = 0

        self.lang_lbl = QtWidgets.QLabel()
        ctrl.addWidget(self.lang_lbl, row, 0)
        self.lang_box = QtWidgets.QComboBox()
        self.lang_box.addItem("English", "en")
        self.lang_box.addItem("中文", "zh")
        self.lang_box.setCurrentIndex(0 if current_lang() == "en" else 1)
        self.lang_box.currentIndexChanged.connect(self._on_lang_changed)
        ctrl.addWidget(self.lang_box, row, 1)
        row += 1

        self.show_raw_cb = QtWidgets.QCheckBox()
        self.show_raw_cb.stateChanged.connect(self.render_overlay)
        ctrl.addWidget(self.show_raw_cb, row, 0)
        self.mode_box = QtWidgets.QComboBox()
        self.mode_box.addItems(["", "", ""])   # texts set in _retranslate
        self.mode_box.currentIndexChanged.connect(self._on_mode_changed)
        ctrl.addWidget(self.mode_box, row, 1)
        row += 1

        self.help_lbl = QtWidgets.QLabel()
        self.help_lbl.setWordWrap(True)
        self.help_lbl.setStyleSheet("color: gray;")
        ctrl.addWidget(self.help_lbl, row, 0, 1, 2)
        row += 1

        self.tgt_lbl = QtWidgets.QLabel()
        ctrl.addWidget(self.tgt_lbl, row, 0, 1, 2)
        row += 1
        self.target_list = QtWidgets.QListWidget()
        for cid in self.ids:
            self.target_list.addItem(f"{cid}: {self.class_config[cid]['name']}")
        self.target_list.setCurrentRow(0)
        self.target_list.currentRowChanged.connect(self._on_target_changed)
        ctrl.addWidget(self.target_list, row, 0, 1, 2)
        row += 1

        self.src_lbl = QtWidgets.QLabel()
        ctrl.addWidget(self.src_lbl, row, 0)
        self.source_box = QtWidgets.QComboBox()
        self.source_box.addItem("", None)      # "Any" text set in _retranslate
        for cid in self.ids:
            self.source_box.addItem(f"{cid}: {self.class_config[cid]['name']}", cid)
        self.source_box.currentIndexChanged.connect(self._on_source_changed)
        ctrl.addWidget(self.source_box, row, 1)
        row += 1

        self.brush_lbl = QtWidgets.QLabel()
        ctrl.addWidget(self.brush_lbl, row, 0)
        self.brush_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.brush_slider.setMinimum(1)
        self.brush_slider.setMaximum(200)
        self.brush_slider.setValue(20)
        self.brush_slider.valueChanged.connect(self._on_brush_changed)
        ctrl.addWidget(self.brush_slider, row, 1)
        row += 1

        # HSV range sliders / HSV 滑块
        self.sliders = {}
        self.hsv_value_labels = {}
        for ch, maxv in zip(["H", "S", "V"], [179, 255, 255]):
            hb = QtWidgets.QHBoxLayout()
            lab = QtWidgets.QLabel(ch + ":")
            lab.setFixedWidth(20)
            hb.addWidget(lab)
            lo = QtWidgets.QSlider(QtCore.Qt.Horizontal); lo.setMaximum(maxv)
            hi = QtWidgets.QSlider(QtCore.Qt.Horizontal); hi.setMaximum(maxv); hi.setValue(maxv)
            hb.addWidget(lo); hb.addWidget(hi)
            vl = QtWidgets.QLabel("0 - %d" % maxv); vl.setFixedWidth(70)
            hb.addWidget(vl)
            lo.valueChanged.connect(self._on_hsv_changed)
            hi.valueChanged.connect(self._on_hsv_changed)
            self.sliders[ch + "_low"] = lo
            self.sliders[ch + "_high"] = hi
            self.hsv_value_labels[ch] = vl
            ctrl.addLayout(hb, row, 0, 1, 2)
            row += 1

        self.btn_hsv_apply = QtWidgets.QPushButton()
        self.btn_hsv_apply.clicked.connect(self.confirm_hsv)
        ctrl.addWidget(self.btn_hsv_apply, row, 0)
        self.btn_hsv_cancel = QtWidgets.QPushButton()
        self.btn_hsv_cancel.clicked.connect(self.cancel_hsv)
        ctrl.addWidget(self.btn_hsv_cancel, row, 1)
        row += 1

        self.alpha_lbl = QtWidgets.QLabel()
        ctrl.addWidget(self.alpha_lbl, row, 0)
        self.alpha_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.alpha_slider.setMinimum(0); self.alpha_slider.setMaximum(100); self.alpha_slider.setValue(50)
        self.alpha_slider.valueChanged.connect(self.render_overlay)
        ctrl.addWidget(self.alpha_slider, row, 1)
        row += 1

        self.btn_undo = QtWidgets.QPushButton()
        self.btn_undo.clicked.connect(self.do_undo)
        ctrl.addWidget(self.btn_undo, row, 0)
        self.btn_save = QtWidgets.QPushButton()
        self.btn_save.clicked.connect(self.save_current)
        ctrl.addWidget(self.btn_save, row, 1)
        row += 1

        self.status_label = QtWidgets.QLabel("—")
        ctrl.addWidget(self.status_label, row, 0, 1, 2)
        row += 1

        ctrl.setRowStretch(row, 1)
        layout.addLayout(ctrl, 2)

        right = QtWidgets.QVBoxLayout()
        self.files_lbl = QtWidgets.QLabel()
        right.addWidget(self.files_lbl)
        self.file_list_widget = QtWidgets.QListWidget()
        self.file_list_widget.addItems(self.file_list)
        self.file_list_widget.currentRowChanged.connect(self._on_file_changed)
        right.addWidget(self.file_list_widget)
        self.coord_label = QtWidgets.QLabel()
        self.coord_label.setAlignment(QtCore.Qt.AlignCenter)
        right.addWidget(self.coord_label)
        layout.addLayout(right, 1)

        # signals / 信号
        self.canvas.polygon_committed.connect(self.on_polygon_committed)
        self.canvas.brush_committed.connect(self.on_brush_committed)
        self.canvas.mouse_pos.connect(self.on_mouse_pos)

        # shortcuts / 快捷键
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Z"), self, self.do_undo)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self, self.save_current)
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return), self, self.confirm_hsv)
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Enter), self, self.confirm_hsv)
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self, self.cancel_hsv)

        # default to HSV filter mode / 默认进入 HSV 过滤模式
        self.mode_box.setCurrentIndex(2)

    def _retranslate(self):
        """Apply the current language to every widget.
        把当前语言应用到所有控件。"""
        self.setWindowTitle(tr("app_title") % __version__)
        self.lang_lbl.setText(tr("language"))
        self.show_raw_cb.setText(tr("show_raw"))
        for i, key in enumerate(("mode_polygon", "mode_brush", "mode_hsv")):
            self.mode_box.setItemText(i, tr(key))
        self.help_lbl.setText(tr("help_text"))
        self.tgt_lbl.setText(tr("target_label"))
        self.tgt_lbl.setToolTip(tr("target_tip"))
        self.target_list.setToolTip(tr("target_tip"))
        self.src_lbl.setText(tr("source_label"))
        self.src_lbl.setToolTip(tr("source_tip"))
        self.source_box.setToolTip(tr("source_tip"))
        self.source_box.setItemText(0, tr("source_any"))
        self.brush_lbl.setText(tr("brush_size"))
        self.btn_hsv_apply.setText(tr("apply_hsv"))
        self.btn_hsv_cancel.setText(tr("cancel_sel"))
        self.alpha_lbl.setText(tr("opacity"))
        self.btn_undo.setText(tr("undo"))
        self.btn_save.setText(tr("save"))
        self.files_lbl.setText(tr("files"))
        self.coord_label.setText(tr("coord_empty"))
        self._update_status()

    # ---------- slots / 槽 ----------
    def _on_lang_changed(self, idx):
        save_lang(self.lang_box.itemData(idx))
        self._retranslate()

    def _on_mode_changed(self, idx):
        self.mode = ["polygon", "brush", "hsv"][idx]
        self.canvas.mode = self.mode
        if self.mode != "hsv":      # drop pending HSV region on mode switch / 离开HSV模式放弃待确认框选
            self.cancel_hsv()

    def _on_target_changed(self, row):
        if 0 <= row < len(self.ids):
            self.target_id = self.ids[row]
            if self.hsv_region is not None:
                self.render_overlay()   # preview highlight uses target color / 预览高亮用目标色

    def _on_source_changed(self, idx):
        self.source_filter = self.source_box.itemData(idx)
        if self.hsv_region is not None:
            self.render_overlay()

    def _on_brush_changed(self, val):
        self.canvas.brush_radius = val

    def _on_hsv_changed(self):
        for ch in ["H", "S", "V"]:
            lo = self.sliders[ch + "_low"].value()
            hi = self.sliders[ch + "_high"].value()
            self.hsv_value_labels[ch].setText("%d - %d" % (lo, hi))
        if self.hsv_region is not None:   # live preview inside the region / 实时预览框选区内命中
            self.render_overlay()

    def on_mouse_pos(self, pos):
        self.coord_label.setText(tr("coord") % (pos[0], pos[1]))

    def _on_file_changed(self, row):
        if self.dirty and self.mask is not None:
            resp = QtWidgets.QMessageBox.question(
                self, tr("unsaved_title"), tr("unsaved_q"),
                QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard
                | QtWidgets.QMessageBox.Cancel,
                QtWidgets.QMessageBox.Save)
            if resp == QtWidgets.QMessageBox.Cancel:
                self.file_list_widget.blockSignals(True)
                self.file_list_widget.setCurrentRow(self.index)  # revert selection / 退回原选中
                self.file_list_widget.blockSignals(False)
                return
            if resp == QtWidgets.QMessageBox.Save:
                self.save_current()
        self.index = row
        self.load_image()

    # ---------- editing / 编辑操作 ----------
    def on_polygon_committed(self, poly):
        if self.mask is None:
            return
        if self.mode == "hsv":
            # HSV mode: store the region, preview live while sliders move, Enter applies
            # HSV模式：先存框选区，调滑块实时预览，回车确认应用
            self.hsv_region = poly
            self.render_overlay()
            self.status_label.setText(tr("hsv_status"))
            return
        # polygon mode: apply immediately / polygon 模式：立即应用
        sel = polygon_selection(self.mask.shape, poly)
        rec = apply_selection(self.mask, sel, self.target_id, self.source_filter)
        self._after_edit(rec)

    def _hsv_region_selection(self):
        """Boolean map of pixels inside the region that match the HSV range
        (and the source-class filter, if set).
        计算当前框选区内、命中HSV区间(并满足源类别限制)的像素布尔图。"""
        if self.hsv_region is None or self.mask is None:
            return None
        inside = polygon_selection(self.mask.shape, self.hsv_region)
        lower = (self.sliders["H_low"].value(), self.sliders["S_low"].value(),
                 self.sliders["V_low"].value())
        upper = (self.sliders["H_high"].value(), self.sliders["S_high"].value(),
                 self.sliders["V_high"].value())
        sel = inside & hsv_selection(self.raw_hsv, lower, upper)
        if self.source_filter is not None:
            sel &= (self.mask == self.source_filter)
        return sel

    def confirm_hsv(self):
        if self.hsv_region is None or self.mask is None:
            return
        sel = self._hsv_region_selection()
        self.hsv_region = None
        # sel already honors the source filter; pass None to avoid double filtering
        # sel 已含源类别限制，这里 source_filter 传 None 避免重复
        rec = apply_selection(self.mask, sel, self.target_id, None)
        self._after_edit(rec)
        if rec is None:
            self.render_overlay()   # clear preview even with no hits / 无命中也要清掉预览
            self._update_status()

    def cancel_hsv(self):
        self.canvas.cancel_drawing()   # also clears in-progress polygon / 同时清除进行中的多边形
        if self.hsv_region is not None:
            self.hsv_region = None
            self.render_overlay()
            self._update_status()

    def on_brush_committed(self, pts):
        if self.mask is None or not pts:
            return
        sel = brush_selection(self.mask.shape, pts, self.brush_slider.value())
        rec = apply_selection(self.mask, sel, self.target_id, self.source_filter)
        self._after_edit(rec)

    def _after_edit(self, rec):
        if rec is None:
            return  # nothing actually changed / 无实际改动
        self.undo.push(rec)
        self.dirty = True
        self.render_overlay()
        self._update_status()

    def do_undo(self):
        if self.mask is None or not self.undo.can_undo():
            return
        rec = self.undo.pop()
        undo_op(self.mask, rec)
        self.dirty = True
        self.render_overlay()
        self._update_status()

    def save_current(self):
        if self.mask is None or not self.file_list:
            return
        base = os.path.splitext(self.file_list[self.index])[0] + ".png"
        out_path = os.path.join(OUT_MASK_DIR, base)
        if not imwrite_unicode(out_path, self.mask):
            QtWidgets.QMessageBox.critical(
                self, tr("err_title"), tr("save_failed") % out_path)
            return
        self.dirty = False
        self._update_status()
        self.status_label.setText(tr("saved") % base)

    # ---------- loading & rendering / 加载与渲染 ----------
    def load_image(self):
        if not self.file_list or not (0 <= self.index < len(self.file_list)):
            return
        fname = self.file_list[self.index]
        img = imread_unicode(os.path.join(IMG_DIR, fname), cv2.IMREAD_COLOR)
        if img is None:
            QtWidgets.QMessageBox.critical(
                self, tr("err_title"), tr("cannot_read") % fname)
            return
        self.raw_image = img
        self.raw_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, w = img.shape[:2]

        # Prefer the corrected mask, then the original mask, else all zeros
        # 优先加载已修正版，否则原始掩膜，否则全 0
        base = os.path.splitext(fname)[0] + ".png"
        out_path = os.path.join(OUT_MASK_DIR, base)
        src_path = os.path.join(SRC_MASK_DIR, base)
        if os.path.exists(out_path):
            mask = imread_unicode(out_path, cv2.IMREAD_UNCHANGED)
        elif os.path.exists(src_path):
            mask = imread_unicode(src_path, cv2.IMREAD_UNCHANGED)
        else:
            mask = None
            QtWidgets.QMessageBox.information(
                self, tr("info_title"), tr("mask_not_found") % base)

        if mask is None:
            mask = np.zeros((h, w), dtype=np.uint8)
        if mask.ndim == 3:
            import sys as _sys
            print(tr("multichannel_warn") % base, file=_sys.stderr)
            mask = mask[:, :, 0]
        if mask.shape[:2] != (h, w):
            QtWidgets.QMessageBox.warning(
                self, tr("mismatch_title"), tr("mismatch_text") % base)
            mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
        self.mask = mask.astype(np.uint8)

        # Render at full resolution (no downsampling) so zooming stays sharp
        # 全分辨率渲染（不再下采样），保证放大清晰
        self.display_image = img
        self.undo.clear()
        self.hsv_region = None
        self.dirty = False
        self.render_overlay()
        self._update_status()
        # Fit to window after loading (zoom resets on image switch, not on edits)
        # 新图加载后自适应窗口（仅切图时重置缩放，编辑时不重置）
        QtCore.QTimer.singleShot(0, self.canvas.fit_to_window)

    def render_overlay(self):
        if self.display_image is None:
            self.canvas.set_base_pixmap(QtGui.QPixmap())
            return
        dh, dw = self.display_image.shape[:2]
        if self.show_raw_cb.isChecked():
            overlay = self.display_image.copy()
        else:
            # mask matches image resolution; colorize and blend (background 0 keeps the photo)
            # mask 与原图同分辨率，直接上色叠加（背景 0 保持原图）
            color = colorize_mask(self.mask, self.palette_bgr)
            alpha = self.alpha_slider.value() / 100.0
            overlay = self.display_image.copy()
            fg = self.mask != 0
            blended = ((1.0 - alpha) * overlay[fg].astype(np.float32)
                       + alpha * color[fg].astype(np.float32))
            overlay[fg] = blended.astype(np.uint8)

        # Pending HSV region: highlight matching pixels + draw the outline (preview only)
        # HSV待确认框选：高亮命中像素 + 画出框选轮廓（预览，不改 mask）
        if self.hsv_region is not None:
            prev = self._hsv_region_selection()
            if prev is not None and prev.any():
                tcol = self.palette_bgr.get(self.target_id, (255, 255, 255))
                overlay[prev] = tcol           # hits shown in target color / 命中像素高亮为目标色
            poly = np.array(self.hsv_region, dtype=np.int32)
            thick = max(2, int(min(dh, dw) / 400))
            cv2.polylines(overlay, [poly], True, (0, 0, 255), thick, cv2.LINE_AA)

        rgb = np.ascontiguousarray(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
        qimg = QtGui.QImage(rgb.data, dw, dh, 3 * dw, QtGui.QImage.Format_RGB888)
        self.canvas.set_base_pixmap(QtGui.QPixmap.fromImage(qimg))

    def _update_status(self):
        if not self.file_list:
            self.status_label.setText("—")
            return
        star = tr("unsaved_star") if self.dirty else ""
        self.status_label.setText("%d/%d: %s%s" %
                                  (self.index + 1, len(self.file_list),
                                   self.file_list[self.index], star))
