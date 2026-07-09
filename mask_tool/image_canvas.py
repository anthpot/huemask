from PyQt5 import QtCore, QtGui, QtWidgets


class ImageCanvas(QtWidgets.QLabel):
    polygon_committed = QtCore.pyqtSignal(object)
    brush_committed = QtCore.pyqtSignal(object)
    mouse_pos = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.initial_scale = 1.0
        self.mode = "polygon"
        self.brush_radius = 20
        self.scrollArea = None

        self.scale = 1.0                 # 缩放（在显示分辨率之上）
        self.base_pixmap = None          # 显示分辨率的彩色叠加图
        self.points = []                 # 多边形点（显示分辨率坐标 QPoint）
        self._brush_pts = []             # 画笔点（全分辨率掩膜坐标 tuple）
        self._painting = False
        self._panning = False
        self._pan_start = QtCore.QPoint()
        self._scroll_start = QtCore.QPoint()

    # ---- 显示 ----
    def set_base_pixmap(self, qpix):
        self.base_pixmap = qpix.copy() if qpix is not None else None
        self.points.clear()
        self._brush_pts.clear()
        self.reset_view()

    def reset_view(self):
        if self.base_pixmap and not self.base_pixmap.isNull():
            self.setPixmap(self._scaled(self.base_pixmap))
        else:
            self.setPixmap(QtGui.QPixmap())

    def _scaled(self, pix):
        # 放大(>=1)用最近邻显示真实像素边界(利于精修)，缩小用平滑
        w = int(pix.width() * self.scale)
        h = int(pix.height() * self.scale)
        mode = QtCore.Qt.FastTransformation if self.scale >= 1.0 else QtCore.Qt.SmoothTransformation
        return pix.scaled(w, h, QtCore.Qt.KeepAspectRatio, mode)

    def fit_to_window(self):
        """按滚动区视口大小自适应缩放，使整图可见。"""
        if not self.base_pixmap or self.base_pixmap.isNull() or self.scrollArea is None:
            return
        vp = self.scrollArea.viewport().size()
        iw, ih = self.base_pixmap.width(), self.base_pixmap.height()
        if iw == 0 or ih == 0 or vp.width() == 0 or vp.height() == 0:
            return
        f = min(vp.width() / iw, vp.height() / ih)
        self.scale = max(0.02, min(f, 2.0))
        self.reset_view()

    # ---- 坐标换算 ----
    def _to_mask_coord(self, pos):
        base_x = pos.x() / self.scale
        base_y = pos.y() / self.scale
        mx = int(base_x / self.initial_scale)
        my = int(base_y / self.initial_scale)
        return mx, my

    def _to_base_point(self, pos):
        return QtCore.QPoint(int(pos.x() / self.scale), int(pos.y() / self.scale))

    # ---- 缩放 ----
    def wheelEvent(self, event):
        if not self.base_pixmap or self.base_pixmap.isNull():
            return
        if event.angleDelta().y() > 0:
            self.scale *= 1.2
        else:
            self.scale /= 1.2
        self.scale = min(max(self.scale, 0.02), 2.0)
        self._redraw_overlay_pixmap()

    # ---- 鼠标 ----
    def mousePressEvent(self, event):
        if not self.base_pixmap or self.base_pixmap.isNull():
            return
        # 平移：Ctrl+左键 或 中键
        if (event.modifiers() == QtCore.Qt.ControlModifier and event.button() == QtCore.Qt.LeftButton) \
                or event.button() == QtCore.Qt.MidButton:
            self._panning = True
            self._pan_start = event.globalPos()
            if self.scrollArea:
                self._scroll_start = QtCore.QPoint(
                    self.scrollArea.horizontalScrollBar().value(),
                    self.scrollArea.verticalScrollBar().value())
            self.setCursor(QtCore.Qt.OpenHandCursor)
            return

        if self.mode == "brush" and event.button() == QtCore.Qt.LeftButton:
            self._painting = True
            self._brush_pts = [self._to_mask_coord(event.pos())]
            return

        # polygon / hsv：左键加点
        if self.mode in ("polygon", "hsv") and event.button() == QtCore.Qt.LeftButton:
            self.setFocus()
            self.points.append(self._to_base_point(event.pos()))
            self._redraw_overlay_pixmap()
            return

        # polygon / hsv：右键闭合
        if self.mode in ("polygon", "hsv") and event.button() == QtCore.Qt.RightButton \
                and len(self.points) >= 3:
            poly = [(int(p.x() / self.initial_scale), int(p.y() / self.initial_scale))
                    for p in self.points]
            self.points.clear()
            self._redraw_overlay_pixmap()
            self.polygon_committed.emit(poly)
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning and self.scrollArea:
            delta = event.globalPos() - self._pan_start
            self.scrollArea.horizontalScrollBar().setValue(self._scroll_start.x() - delta.x())
            self.scrollArea.verticalScrollBar().setValue(self._scroll_start.y() - delta.y())
        elif self._painting:
            self._brush_pts.append(self._to_mask_coord(event.pos()))
            self._redraw_overlay_pixmap(current=event.pos())
        elif self.points:
            self._redraw_overlay_pixmap(current=event.pos())

        if self.base_pixmap and not self.base_pixmap.isNull():
            self.mouse_pos.emit(self._to_mask_coord(event.pos()))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._panning:
            self._panning = False
            self.unsetCursor()
        elif self._painting and event.button() == QtCore.Qt.LeftButton:
            self._painting = False
            pts = self._brush_pts
            self._brush_pts = []
            self._redraw_overlay_pixmap()
            if pts:
                self.brush_committed.emit(pts)
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.cancel_drawing()
        super().keyPressEvent(event)

    def cancel_drawing(self):
        """清除进行中的多边形/画笔绘制状态。"""
        self.points.clear()
        self._brush_pts.clear()
        self._painting = False
        if self.base_pixmap is not None and not self.base_pixmap.isNull():
            self._redraw_overlay_pixmap()

    # ---- 在叠加图上画临时多边形/画笔预览 ----
    def _redraw_overlay_pixmap(self, current=None):
        if self.base_pixmap is None:
            return
        temp = self.base_pixmap.copy()
        painter = QtGui.QPainter(temp)
        pen = QtGui.QPen(QtGui.QColor(255, 0, 0), 2)
        painter.setPen(pen)
        if len(self.points) > 1:
            painter.drawPolyline(QtGui.QPolygonF([QtCore.QPointF(p.x(), p.y()) for p in self.points]))
        if current is not None and self.points:
            painter.drawLine(self.points[-1], self._to_base_point(current))
        # 画笔预览：把全分辨率点换算回显示分辨率画圆
        if self._brush_pts:
            r = max(1, int(self.brush_radius * self.initial_scale))
            for (mx, my) in self._brush_pts:
                bx = int(mx * self.initial_scale)
                by = int(my * self.initial_scale)
                painter.drawEllipse(QtCore.QPoint(bx, by), r, r)
        painter.end()
        self.setPixmap(self._scaled(temp))
